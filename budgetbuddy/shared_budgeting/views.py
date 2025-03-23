from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SharedBudget, Expense, ExpenseSplit
from .forms import SharedBudgetForm, ExpenseForm

# -------------------------
# 🌐 List Shared Budgets
# -------------------------
@login_required
def shared_budget_list(request):
    budgets = SharedBudget.objects.filter(members=request.user)
    return render(request, 'shared_budgeting/shared_budget_list.html', {'budgets': budgets})


# -------------------------
# ➕ Create Shared Budget
# -------------------------
@login_required
def create_shared_budget(request):
    form = SharedBudgetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        budget = form.save(commit=False)
        budget.created_by = request.user
        budget.save()
        form.save_m2m()
        messages.success(request, "🎉 Shared Budget Created Successfully!")
        return redirect('shared_budget_list')
    return render(request, 'shared_budgeting/create_shared_budget.html', {'form': form})


# -------------------------
# 🔍 View Budget Details
# -------------------------
@login_required
def budget_detail(request, budget_id):
    budget = get_object_or_404(SharedBudget, id=budget_id, members=request.user)
    expenses = Expense.objects.filter(budget=budget).prefetch_related('expensesplit_set')

    # Calculate balances per user
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
# ➕ Add Expense to Shared Budget
# -------------------------
@login_required
def add_expense(request, budget_id):
    budget = get_object_or_404(SharedBudget, id=budget_id, members=request.user)
    form = ExpenseForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        expense = form.save(commit=False)
        expense.budget = budget
        expense.save()

        members = list(budget.members.all())
        if members:
            split_amount = round(expense.amount / len(members), 2)
            ExpenseSplit.objects.bulk_create([
                ExpenseSplit(expense=expense, user=member, amount_owed=split_amount) for member in members
            ])

        messages.success(request, "✅ Expense Added Successfully!")
        return redirect('budget_detail', budget_id=budget.id)

    return render(request, 'shared_budgeting/add_expense.html', {'form': form, 'budget': budget})


# -------------------------
# ✏️ Edit Shared Budget
# -------------------------
@login_required
def edit_shared_budget(request, pk):
    budget = get_object_or_404(SharedBudget, pk=pk)
    if request.user != budget.created_by:
        messages.warning(request, "You are not authorized to edit this budget.")
        return redirect('shared_budget_list')

    form = SharedBudgetForm(request.POST or None, instance=budget)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "✅ Shared Budget Updated!")
        return redirect('shared_budget_list')

    return render(request, 'shared_budgeting/edit_budget.html', {'form': form, 'budget': budget})


# -------------------------
# ❌ Delete Shared Budget
# -------------------------
@login_required
def delete_shared_budget(request, pk):
    budget = get_object_or_404(SharedBudget, pk=pk)
    if request.user != budget.created_by:
        messages.warning(request, "You are not authorized to delete this budget.")
        return redirect('shared_budget_list')

    if request.method == 'POST':
        budget.delete()
        messages.success(request, "🗑️ Shared Budget Deleted.")
        return redirect('shared_budget_list')

    return render(request, 'shared_budgeting/delete_budget_confirm.html', {'budget': budget})
