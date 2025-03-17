from django.db import models
from django.conf import settings

class SharedBudget(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_budgets')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='budget_members')

    def __str__(self):
        return self.name

class Expense(models.Model):
    budget = models.ForeignKey(SharedBudget, on_delete=models.CASCADE, related_name='expenses')
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='paid_expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - ${self.amount}"

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='splitted_expenses')
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} owes ${self.amount_owed} for {self.expense.description}"
