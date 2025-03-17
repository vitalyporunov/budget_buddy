from django import forms
from .models import SharedBudget, Expense

class SharedBudgetForm(forms.ModelForm):
    class Meta:
        model = SharedBudget
        fields = ['name', 'members']
        widgets = {
            'members': forms.CheckboxSelectMultiple()
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'payer']
