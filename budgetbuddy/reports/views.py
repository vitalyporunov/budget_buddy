import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for matplotlib
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas

# ----------------------------
# ✅ Helper Function: Get Filtered Transactions
# ----------------------------
def get_filtered_transactions(user, date_from, date_to):
    """Filters transactions based on the user and optional date range."""
    transactions = Transaction.objects.filter(user=user)
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    return transactions


# ----------------------------
# ✅ Financial Report View (Pie & Bar Chart)
# ----------------------------
@login_required
def financial_report(request):
    """Generates a financial report with a Pie Chart (Income vs Expenses) & Monthly Bar Chart."""
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    transactions = get_filtered_transactions(request.user, date_from, date_to)

    # Calculate totals
    total_income = transactions.filter(category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(category='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # 🔹 Generate Pie Chart
    pie_chart = generate_pie_chart(total_income, total_expense)

    # 🔹 Generate Bar Chart (Monthly Spending Trends)
    bar_chart = generate_bar_chart(transactions)

    return render(request, 'reports/financial_report.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'pie_chart': pie_chart,
        'bar_chart': bar_chart,
    })


# ----------------------------
# ✅ Generate Pie Chart (Income vs Expenses)
# ----------------------------
def generate_pie_chart(income, expense):
    """Generates a pie chart comparing income vs. expenses."""
    
    if income == 0 and expense == 0:
        return None  # No chart if no data
    
    labels = ['Income', 'Expenses']
    values = [income, expense]
    colors = ['green', 'red']

    plt.figure(figsize=(5, 5))
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title("Income vs Expenses")

    return convert_plot_to_base64()


# ----------------------------
# ✅ Generate Bar Chart (Monthly Trends)
# ----------------------------
def generate_bar_chart(transactions):
    """Generates a bar chart showing monthly income & expenses trends."""
    
    # Aggregate transactions by month
    monthly_data = transactions.annotate(month=TruncMonth('date')).values('month', 'category').annotate(total=Sum('amount'))

    # Convert to dictionary
    income_data = {data['month']: data['total'] for data in monthly_data if data['category'] == 'income'}
    expense_data = {data['month']: data['total'] for data in monthly_data if data['category'] == 'expense'}
    
    months = sorted(set(income_data.keys()).union(expense_data.keys()))
    income_values = [income_data.get(month, 0) for month in months]
    expense_values = [expense_data.get(month, 0) for month in months]

    # Generate bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(months, income_values, color='green', label='Income')
    plt.bar(months, expense_values, color='red', label='Expense', alpha=0.7)
    plt.xlabel("Month")
    plt.ylabel("Amount ($)")
    plt.title("Monthly Income vs Expenses")
    plt.xticks(rotation=45)
    plt.legend()

    return convert_plot_to_base64()


# ----------------------------
# ✅ Convert Matplotlib Plot to Base64
# ----------------------------
def convert_plot_to_base64():
    """Converts a Matplotlib plot into a Base64 string for embedding in HTML."""
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()


# ----------------------------
# ✅ Generate PDF Report
# ----------------------------
@login_required
def generate_pdf(request):
    """Generates a downloadable PDF report for the financial summary."""
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    transactions = get_filtered_transactions(request.user, date_from, date_to)

    # Calculate totals
    total_income = transactions.filter(category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(category='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Create PDF Response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="financial_report.pdf"'
    pdf = canvas.Canvas(response)

    # Add Report Title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, 800, "Financial Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, f"Total Income: ${total_income}")
    pdf.drawString(100, 730, f"Total Expenses: ${total_expense}")
    pdf.drawString(100, 710, f"Net Savings: ${total_income - total_expense}")

    pdf.save()
    return response
