from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SharedBudget, Expense, ExpenseSplit
from .forms import SharedBudgetForm, ExpenseForm

# -------------------------
# ✅ List All Shared Budgets
# -------------------------
@login_required
def shared_budget_list(request):
    """View to list shared budgets where the user is a member"""
    budgets = SharedBudget.objects.filter(members=request.user)
    return render(request, 'shared_budgeting/shared_budget_list.html', {'budgets': budgets})

# -------------------------
# ✅ Create a Shared Budget
# -------------------------
@login_required
def create_shared_budget(request):
    """View to create a new shared budget"""
    form = SharedBudgetForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        budget = form.save(commit=False)
        budget.created_by = request.user
        budget.save()
        form.save_m2m()  # Save many-to-many relationships
        messages.success(request, "🎉 Shared Budget Created Successfully!")
        return redirect('shared_budget_list')

    return render(request, 'shared_budgeting/create_shared_budget.html', {'form': form})

# -------------------------
# ✅ View Budget Details & Balances
# -------------------------
@login_required
def budget_detail(request, budget_id):
    """View details of a shared budget, including expenses & balances"""
    budget = get_object_or_404(SharedBudget, id=budget_id, members=request.user)
    expenses = Expense.objects.filter(budget=budget).prefetch_related('expensesplit_set')

    # Calculate who owes what
    balances = {}
    for expense in expenses:
        for split in expense.expensesplit_set.all():
            balances[split.user] = balances.get(split.user, 0) + split.amount_owed

    return render(request, 'shared_budgeting/budget_detail.html', {
        'budget': budget,
        'expenses': expenses,
        'balances': balances
    })

# -------------------------
# ✅ Add an Expense to a Budget
# -------------------------
@login_required
def add_expense(request, budget_id):
    """View to add an expense to a shared budget"""
    budget = get_object_or_404(SharedBudget, id=budget_id, members=request.user)
    form = ExpenseForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        expense = form.save(commit=False)
        expense.budget = budget
        expense.save()

        # Split expense equally among members
        members = list(budget.members.all())
        split_amount = round(expense.amount / len(members), 2)

        ExpenseSplit.objects.bulk_create([
            ExpenseSplit(expense=expense, user=member, amount_owed=split_amount) for member in members
        ])

        messages.success(request, "✅ Expense Added Successfully!")
        return redirect('budget_detail', budget_id=budget.id)

    return render(request, 'shared_budgeting/add_expense.html', {'form': form, 'budget': budget})
