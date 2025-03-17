from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils.dateparse import parse_date
from .models import Transaction
from .forms import TransactionForm
import matplotlib.pyplot as plt
import io
import base64

# -------------------------
# ✅ List & Filter Transactions
# -------------------------
@login_required
def transaction_list(request):
    """Lists transactions with filtering and income-expense summary."""

    # Get filter parameters
    category = request.GET.get('category', '').strip()
    date_from = parse_date(request.GET.get('date_from', '').strip()) if request.GET.get('date_from') else None
    date_to = parse_date(request.GET.get('date_to', '').strip()) if request.GET.get('date_to') else None

    # Apply filters dynamically
    filters = Q(user=request.user)
    if category:
        filters &= Q(category=category)
    if date_from:
        filters &= Q(date__gte=date_from)
    if date_to:
        filters &= Q(date__lte=date_to)

    # Query transactions based on filters
    transactions = Transaction.objects.filter(filters).order_by('-date')

    # Compute Total Income & Expenses
    total_income = transactions.filter(category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(category='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'transactions/transaction_list.html', {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
    })

# -------------------------
# ✅ Handle Transaction (Add & Edit)
# -------------------------
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    
    return render(request, 'transactions/add_transaction.html', {'form': form})

@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)

    return render(request, 'transactions/edit_transaction.html', {'form': form})

# -------------------------
# ✅ Delete Transaction
# -------------------------
@login_required
def delete_transaction(request, transaction_id):
    """Handles deleting a transaction."""
    
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')

    return render(request, 'transactions/delete_transaction.html', {'transaction': transaction})

# -------------------------
# ✅ Report View - Income vs Expense Pie Chart
# -------------------------
@login_required
def report_view(request):
    """Generates an income vs expense pie chart."""

    transactions = Transaction.objects.filter(user=request.user)
    
    # Compute total income and expense
    income = transactions.filter(category="income").aggregate(Sum('amount'))['amount__sum'] or 0
    expense = transactions.filter(category="expense").aggregate(Sum('amount'))['amount__sum'] or 0

    # Handle cases where no transactions exist
    if not income and not expense:
        return render(request, 'transactions/report.html', {'graph': None})

    # Generate Pie Chart
    labels, values, colors = ['Income', 'Expense'], [income, expense], ['green', 'red']

    plt.figure(figsize=(5,5))
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    plt.title("Income vs Expenses")

    # Convert the plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'transactions/report.html', {'graph': graph})
