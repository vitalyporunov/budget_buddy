from django.db import models
from django.conf import settings

class Investment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)  
    name = models.CharField(max_length=100)
    quantity = models.FloatField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.symbol})"
