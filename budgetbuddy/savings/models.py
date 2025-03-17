from django.db import models
from django.conf import settings

class SavingsGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)

    def progress_percentage(self):
        """ Calculate progress percentage """
        if self.target_amount == 0:
            return 0
        return min(int((self.current_savings / self.target_amount) * 100), 100)

    def __str__(self):
        return f"{self.name} - {self.user.username}"
