from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Budget

# Home view
def home(request):
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

# Dashboard view
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

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
