from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from investments.models import Investment
from shared_budgeting.models import SharedBudget, Expense
from datetime import date

User = get_user_model()

class ReportsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='report_user', password='testpass123')
        self.client.login(username='report_user', password='testpass123')

        # Create investment
        Investment.objects.create(
            user=self.user,
            symbol='AAPL',
            quantity=2,
            purchase_price=150.00
        )

        # Create shared budget + expense
        budget = SharedBudget.objects.create(name='Roommates', owner=self.user)
        budget.members.add(self.user)
        Expense.objects.create(
            budget=budget,
            paid_by=self.user,
            amount=100.00,
            description='Electric Bill',
            date=date.today()
        )

    def test_reports_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('financial_report'))
        self.assertEqual(response.status_code, 302)  # should redirect to login

    def test_reports_view_logged_in(self):
        response = self.client.get(reverse('financial_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/financial_report.html')
        self.assertContains(response, "Investment Portfolio")
        self.assertContains(response, "Shared Budget Summary")

    def test_reports_render_without_investments_or_budgets(self):
        # New user with no data
        self.client.logout()
        new_user = User.objects.create_user(username='nodata', password='nopass')
        self.client.login(username='nodata', password='nopass')
        response = self.client.get(reverse('financial_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Financial Report")
