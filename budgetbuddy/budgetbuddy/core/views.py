from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Budget, Transaction, SavingsGoal, Debt
import matplotlib.pyplot as plt
import io
import urllib

# Home view
def home(request):
    return render(request, 'home.html')

# Signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            login(request, user)  # Log the user in after successful sign-up
            return redirect('dashboard')  # Redirect to the dashboard after sign-up
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')  
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    
    return render(request, 'login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')

# Budget view
@login_required
def budget_view(request):
    user = request.user
    budget, created = Budget.objects.get_or_create(user=user) 

    if request.method == 'POST':
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
    budget, created = Budget.objects.get_or_create(user=user)
    savings_goals = SavingsGoal.objects.filter(user=user)
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
    debts = Debt.objects.filter(user=user)

    if request.method == 'POST':
        debt_name = request.POST.get('debt_name')
        amount_due = request.POST.get('amount_due')
        due_date = request.POST.get('due_date')

        Debt.objects.create(user=user, debt_name=debt_name, amount_due=amount_due, due_date=due_date)
        return redirect('debt')

    return render(request, 'debt.html', {'debts': debts})

# Goal view for displaying and managing savings goals
@login_required
def goal_view(request):
    user = request.user
    goals = SavingsGoal.objects.filter(user=user)

    if request.method == 'POST':
        goal_name = request.POST.get('goal_name')
        target_amount = request.POST.get('target_amount')
        current_balance = request.POST.get('current_balance')

        SavingsGoal.objects.create(user=user, goal_name=goal_name, target_amount=target_amount, current_balance=current_balance)
        return redirect('goal')

    return render(request, 'goals.html', {'goals': goals})

# Reports view
@login_required
def reports_view(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    total_income = sum(t.amount for t in transactions if t.transaction_type == 'Income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'Expense')
    net_savings = total_income - total_expenses

    # Category pie chart
    categories = {}
    for transaction in transactions.filter(transaction_type='Expense'):
        categories[transaction.category] = categories.get(transaction.category, 0) + transaction.amount

    category_pie_chart_url = generate_category_pie_chart(categories)
    income_expenses_line_graph_url = generate_income_expenses_line_graph(transactions)

    return render(request, 'reports.html', {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'category_pie_chart_url': category_pie_chart_url,
        'income_expenses_line_graph_url': income_expenses_line_graph_url
    })

# Generate pie chart for expense categories
def generate_category_pie_chart(categories):
    labels = categories.keys()
    sizes = categories.values()

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_data = urllib.parse.quote(buf.getvalue())
    buf.close()

    return f"data:image/png;base64,{image_data}"

# Generate line graph for income and expenses over time
def generate_income_expenses_line_graph(transactions):
    dates = []
    income_data = []
    expense_data = []

    for transaction in transactions:
        dates.append(transaction.transaction_date.strftime('%Y-%m-%d'))
        if transaction.transaction_type == 'Income':
            income_data.append(transaction.amount)
            expense_data.append(0)
        else:
            income_data.append(0)
            expense_data.append(transaction.amount)

    fig, ax = plt.subplots()
    ax.plot(dates, income_data, label="Income", color='green')
    ax.plot(dates, expense_data, label="Expense", color='red')

    ax.set_xlabel('Date')
    ax.set_ylabel('Amount')
    ax.set_title('Income and Expenses Over Time')
    ax.legend()

    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_data = urllib.parse.quote(buf.getvalue())
    buf.close()

    return f"data:image/png;base64,{image_data}"

# Income/Expense view
@login_required
def income_expense_view(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        transaction_type = request.POST.get('transaction_type')
        category = request.POST.get('category')
        date = request.POST.get('date')

        # Save the new transaction to the database
        transaction = Transaction(
            user=user,
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            transaction_date=date
        )
        transaction.save()

    return render(request, 'income_expense.html', {'transactions': transactions})
