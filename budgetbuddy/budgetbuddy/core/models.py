from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=[('Income', 'Income'), ('Expense', 'Expense')], max_length=7)

    def __str__(self):
        return f"{self.type}: {self.category} - ${self.amount} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['-date']  # Ordering transactions by date (most recent first)

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    current_spending = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Budget for {self.user.username}: ${self.limit} limit, ${self.current_spending} spent"

    def update_spending(self):
        """ Updates the current spending based on transactions """
        self.current_spending = self.user.transaction_set.filter(date__gte=self.created_at).aggregate(
            total_spent=models.Sum('amount')
        )['total_spent'] or 0
        self.save()

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.goal_name} - ${self.current_balance} / ${self.target_amount}"

    def update_balance(self):
        """ Updates the current balance for the goal based on transactions """
        self.current_balance = self.user.transaction_set.filter(category=self.goal_name).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.save()

class Debt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    debt_name = models.CharField(max_length=255)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.debt_name} - ${self.amount_due} due on {self.due_date}"

    class Meta:
        ordering = ['due_date']  # Sorting debts by due date (earliest due first)
