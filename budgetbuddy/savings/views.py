from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SavingsGoal
from .forms import SavingsGoalForm

@login_required
def savings_goal_list(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, 'savings/savings_goal_list.html', {'goals': goals})

@login_required
def add_savings_goal(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Savings goal added successfully!")
            return redirect('savings_goal_list')
    else:
        form = SavingsGoalForm()

    return render(request, 'savings/add_savings_goal.html', {'form': form})

@login_required
def update_savings_goal(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Savings goal updated successfully!")
            return redirect('savings_goal_list')
    else:
        form = SavingsGoalForm(instance=goal)

    return render(request, 'savings/update_savings_goal.html', {'form': form, 'goal': goal})

@login_required
def delete_savings_goal(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Savings goal deleted successfully!")
        return redirect('savings_goal_list')

    return render(request, 'savings/delete_savings_goal.html', {'goal': goal})
