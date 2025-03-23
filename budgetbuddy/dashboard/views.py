import matplotlib
matplotlib.use('Agg')  # Use Agg backend to prevent GUI errors
import matplotlib.pyplot as plt
import seaborn as sns
import io
import urllib, base64
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction
from django.db.models import Sum
from datetime import datetime

@login_required
def dashboard_view(request):
    # Calculate total income and expenses
    total_income = Transaction.objects.filter(user=request.user, category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(user=request.user, category='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Get recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]

    # Generate Pie Chart for Income vs Expenses
    labels = ['Income', 'Expense']
    values = [total_income, total_expense]
    colors = ['green', 'red']

    plt.figure(figsize=(5, 5))
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title("Income vs Expenses")

    # Save pie chart as image
    pie_buffer = io.BytesIO()
    plt.savefig(pie_buffer, format='png')
    plt.close()  # Close the figure to free memory
    pie_buffer.seek(0)
    pie_image = base64.b64encode(pie_buffer.getvalue()).decode()
    pie_buffer.close()

    # Generate Monthly Report (Bar Chart)
    monthly_data = Transaction.objects.filter(user=request.user).values('date').order_by('date')
    monthly_totals = {}

    for transaction in monthly_data:
        month = transaction['date'].strftime('%Y-%m')  # Get YYYY-MM format
        amount = Transaction.objects.filter(user=request.user, date__startswith=month).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_totals[month] = amount

    # Plot Bar Chart
    plt.figure(figsize=(7, 5))
    sns.barplot(x=list(monthly_totals.keys()), y=list(monthly_totals.values()), palette="Blues_r")
    plt.xlabel("Month")
    plt.ylabel("Total Amount ($)")
    plt.title("Monthly Expenses & Income")

    # Save bar chart as image
    bar_buffer = io.BytesIO()
    plt.savefig(bar_buffer, format='png')
    plt.close()  # Close the figure to free memory
    bar_buffer.seek(0)
    bar_image = base64.b64encode(bar_buffer.getvalue()).decode()
    bar_buffer.close()

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'pie_chart': pie_image,
        'bar_chart': bar_image
    }

    return render(request, 'dashboard/home.html', context)

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


import matplotlib.pyplot as plt
import io, base64
from datetime import datetime
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from transactions.models import Transaction


def generate_monthly_income_expense_chart(user):
    transactions = Transaction.objects.filter(user=user)

    # Group by month
    monthly_data = transactions.annotate(month=TruncMonth('date')).values('month', 'category').annotate(
        total=Sum('amount')
    ).order_by('month')

    # Prepare data structure
    income_data = {}
    expense_data = {}
    months = []

    for item in monthly_data:
        month_label = item['month'].strftime("%b %Y")
        if month_label not in months:
            months.append(month_label)

        if item['category'] == 'income':
            income_data[month_label] = item['total']
        elif item['category'] == 'expense':
            expense_data[month_label] = item['total']

    income = [income_data.get(month, 0) for month in months]
    expenses = [expense_data.get(month, 0) for month in months]

    # Create chart
    plt.figure(figsize=(8, 5))
    x = range(len(months))
    plt.bar(x, income, width=0.4, label='Income', align='center', color='mediumseagreen')
    plt.bar([i + 0.4 for i in x], expenses, width=0.4, label='Expenses', align='center', color='salmon')
    plt.xticks([i + 0.2 for i in x], months, rotation=45)
    plt.ylabel("Amount ($)")
    plt.title("Monthly Income & Expenses")
    plt.legend()

    # Return as base64 image
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()
