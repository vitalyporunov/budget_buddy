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
