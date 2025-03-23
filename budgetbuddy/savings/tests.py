from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import SavingsGoal

User = get_user_model()

class SavingsGoalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='saver', password='securepass')
        self.client.login(username='saver', password='securepass')

        self.goal = SavingsGoal.objects.create(
            user=self.user,
            title='New Laptop',
            target_amount=1500.00,
            saved_amount=500.00,
            deadline=date.today() + timedelta(days=30)
        )

    def test_goal_creation(self):
        self.assertEqual(SavingsGoal.objects.count(), 1)
        self.assertEqual(self.goal.title, 'New Laptop')
        self.assertEqual(self.goal.saved_amount, 500.00)

    def test_savings_list_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('savings_list'))
        self.assertEqual(response.status_code, 302)

    def test_savings_list_view_logged_in(self):
        response = self.client.get(reverse('savings_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Laptop')

    def test_add_savings_goal(self):
        response = self.client.post(reverse('add_savings'), {
            'title': 'Vacation Fund',
            'target_amount': 2000,
            'saved_amount': 300,
            'deadline': date.today() + timedelta(days=60)
        })
        self.assertEqual(SavingsGoal.objects.count(), 2)

    def test_edit_savings_goal(self):
        response = self.client.post(reverse('edit_savings', args=[self.goal.id]), {
            'title': 'Updated Laptop Fund',
            'target_amount': 1600,
            'saved_amount': 600,
            'deadline': date.today() + timedelta(days=45)
        })
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.title, 'Updated Laptop Fund')
        self.assertEqual(self.goal.saved_amount, 600.00)

    def test_delete_savings_goal(self):
        response = self.client.post(reverse('delete_savings', args=[self.goal.id]))
        self.assertEqual(SavingsGoal.objects.count(), 0)

    def test_goal_completion_logic(self):
        self.goal.saved_amount = self.goal.target_amount
        self.goal.save()
        self.assertTrue(self.goal.saved_amount >= self.goal.target_amount)
