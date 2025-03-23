from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import SharedBudget, Expense, ExpenseSplit
from datetime import date

User = get_user_model()

class SharedBudgetingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='password123')
        self.user2 = User.objects.create_user(username='bob', password='password456')

        # Create shared budget with both users
        self.budget = SharedBudget.objects.create(name='Roommates', owner=self.user1)
        self.budget.members.set([self.user1, self.user2])

        # Login as alice
        self.client.login(username='alice', password='password123')

        # Create an expense
        self.expense = Expense.objects.create(
            budget=self.budget,
            paid_by=self.user1,
            amount=100.00,
            description='Groceries',
            date=date.today()
        )

        # Split between two people
        self.split1 = ExpenseSplit.objects.create(expense=self.expense, user=self.user1, share=50.00)
        self.split2 = ExpenseSplit.objects.create(expense=self.expense, user=self.user2, share=50.00)

    def test_shared_budget_created(self):
        self.assertEqual(SharedBudget.objects.count(), 1)
        self.assertEqual(self.budget.members.count(), 2)

    def test_expense_created_and_split(self):
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(ExpenseSplit.objects.count(), 2)
        total_split = sum([s.share for s in self.expense.splits.all()])
        self.assertEqual(total_split, self.expense.amount)

    def test_budget_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('shared_budget_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_budget_view_logged_in(self):
        response = self.client.get(reverse('shared_budget_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Roommates')

    def test_add_expense_view(self):
        response = self.client.post(reverse('add_expense', args=[self.budget.id]), {
            'amount': 75.00,
            'description': 'Pizza night',
            'paid_by': self.user1.id,
            'date': date.today()
        })
        self.assertEqual(Expense.objects.count(), 2)

    def test_edit_expense(self):
        response = self.client.post(reverse('edit_expense', args=[self.expense.id]), {
            'amount': 120.00,
            'description': 'Updated groceries',
            'paid_by': self.user1.id,
            'date': date.today()
        })
        self.expense.refresh_from_db()
        self.assertEqual(self.expense.amount, 120.00)

    def test_delete_expense(self):
        response = self.client.post(reverse('delete_expense', args=[self.expense.id]))
        self.assertEqual(Expense.objects.count(), 0)
