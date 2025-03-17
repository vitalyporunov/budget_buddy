import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for matplotlib
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction
from django.db.models import Sum
from datetime import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas

@login_required
def financial_report(request):
    transactions = Transaction.objects.filter(user=request.user)

    # Get selected date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    # Calculate totals
    total_income = transactions.filter(category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(category='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Generate Pie Chart (Income vs Expenses)
    labels = ['Income', 'Expenses']
    values = [total_income, total_expense]
    colors = ['green', 'red']

    plt.figure(figsize=(5, 5))
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title("Income vs Expenses")

    # Convert pie chart to base64 image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    pie_chart = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return render(request, 'reports/financial_report.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'pie_chart': pie_chart
    })

@login_required
def generate_pdf(request):
    transactions = Transaction.objects.filter(user=request.user)

    # Get selected date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    # Calculate totals
    total_income = transactions.filter(category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(category='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="financial_report.pdf"'
    pdf = canvas.Canvas(response)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, 800, "Financial Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, f"Total Income: ${total_income}")
    pdf.drawString(100, 730, f"Total Expenses: ${total_expense}")
    pdf.drawString(100, 710, f"Net Savings: ${total_income - total_expense}")

    pdf.save()
    return response
