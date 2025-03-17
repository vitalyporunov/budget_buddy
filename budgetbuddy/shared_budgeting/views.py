from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import SharedBudget, Expense, ExpenseSplit
from .forms import SharedBudgetForm, ExpenseForm

@login_required
def shared_budget_list(request):
    budgets = SharedBudget.objects.filter(members=request.user)
    return render(request, 'shared_budgeting/shared_budget_list.html', {'budgets': budgets})

@login_required
def create_shared_budget(request):
    if request.method == 'POST':
        form = SharedBudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.created_by = request.user
            budget.save()
            form.save_m2m()
            messages.success(request, "Shared Budget Created Successfully!")
            return redirect('shared_budget_list')
    else:
        form = SharedBudgetForm()

    return render(request, 'shared_budgeting/create_shared_budget.html', {'form': form})

@login_required
def budget_detail(request, budget_id):
    budget = get_object_or_404(SharedBudget, id=budget_id, members=request.user)
    expenses = Expense.objects.filter(budget=budget)

    # Calculate who owes what
    balances = {}
    for expense in expenses:
        splits = ExpenseSplit.objects.filter(expense=expense)
        for split in splits:
            if split.user not in balances:
                balances[split.user] = 0
            balances[split.user] += split.amount_owed

    return render(request, 'shared_budgeting/budget_detail.html', {'budget': budget, 'expenses': expenses, 'balances': balances})

@login_required
def add_expense(request, budget_id):
    budget = get_object_or_404(SharedBudget, id=budget_id, members=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget
            expense.save()

            # Split expense equally
            members = budget.members.all()
            split_amount = expense.amount / len(members)
            for member in members:
                ExpenseSplit.objects.create(expense=expense, user=member, amount_owed=split_amount)

            messages.success(request, "Expense Added Successfully!")
            return redirect('budget_detail', budget_id=budget.id)
    else:
        form = ExpenseForm()

    return render(request, 'shared_budgeting/add_expense.html', {'form': form, 'budget': budget})
