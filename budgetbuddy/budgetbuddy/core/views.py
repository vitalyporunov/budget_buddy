from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Budget, Transaction, SavingsGoal, Debt

# Home view
def home(request):  # Fixed typo in 'ddef home'
    return render(request, 'home.html')

# Signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')

# Budget view
@login_required
def budget_view(request):
    user = request.user

    # Get the user's current budget (or create one if it doesn't exist)
    budget, created = Budget.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Handle form submission to update the budget
        try:
            new_limit = float(request.POST['limit'])
            if new_limit >= 0:
                budget.limit = new_limit
                budget.save()
                message = "Your budget has been updated successfully!"
            else:
                message = "Please enter a valid amount for the limit."
        except ValueError:
            message = "Invalid input. Please enter a valid number."

        return render(request, 'budget.html', {'budget': budget, 'message': message})

    return render(request, 'budget.html', {'budget': budget})

# Dashboard view (updated to include transactions and savings goals)
@login_required
def dashboard(request):
    user = request.user

    # Fetch the user's budget (or create one if it doesn't exist)
    budget, created = Budget.objects.get_or_create(user=user)

    # Fetch the user's savings goals
    savings_goals = SavingsGoal.objects.filter(user=user)

    # Fetch recent transactions (limit to the last 5)
    transactions = Transaction.objects.filter(user=user).order_by('-transaction_date')[:5]

    return render(request, 'dashboard.html', {
        'budget': budget,
        'savings_goals': savings_goals,
        'transactions': transactions
    })

# Debt view (for managing user debts)
@login_required
def debt_view(request):
    user = request.user

    # Fetch the user's debts
    debts = Debt.objects.filter(user=user)

    if request.method == 'POST':
        # Handle form submission to add a new debt
        debt_name = request.POST.get('debt_name')
        amount_due = request.POST.get('amount_due')
        due_date = request.POST.get('due_date')

        # Save the new debt
        Debt.objects.create(
            user=user,
            debt_name=debt_name,
            amount_due=amount_due,
            due_date=due_date
        )

        return redirect('debt')

    return render(request, 'debt.html', {'debts': debts})

# Goal view for displaying and managing savings goals
@login_required
def goal_view(request):
    user = request.user

    # Fetch the user's savings goals
    goals = SavingsGoal.objects.filter(user=user)

    if request.method == 'POST':
        # Handle form submission to create a new goal
        goal_name = request.POST.get('goal_name')
        target_amount = request.POST.get('target_amount')
        current_balance = request.POST.get('current_balance')

        # Create the new goal
        SavingsGoal.objects.create(
            user=user,
            goal_name=goal_name,
            target_amount=target_amount,
            current_balance=current_balance
        )

        return redirect('goal')  # Redirect to the goals page after adding the goal

    return render(request, 'goals.html', {'goals': goals})

# Reports view
@login_required
def reports_view(request):
    # Dummy data for the report - you can replace it with actual data
    reports_data = {
        'spending_report': [
            {'category': 'Food', 'amount': 200},
            {'category': 'Entertainment', 'amount': 150},
            {'category': 'Bills', 'amount': 300},
        ],
        'income_report': [
            {'source': 'Salary', 'amount': 2000},
            {'source': 'Freelance', 'amount': 500},
        ]
    }

    return render(request, 'reports.html', {'reports_data': reports_data})