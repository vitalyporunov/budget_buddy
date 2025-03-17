from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction
from django.db.models import Sum

@login_required
def dashboard_view(request):
    # Calculate total income and total expenses
    total_income = Transaction.objects.filter(user=request.user, category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(user=request.user, category='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Get recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'recent_transactions': recent_transactions
    }
    return render(request, 'dashboard/home.html', context)

