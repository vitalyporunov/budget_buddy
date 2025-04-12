from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Investment

User = get_user_model()
class InvestmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.list_url = reverse('investment_list')
        self.add_url = reverse('add_investment')

        self.investment = Investment.objects.create(
            user=self.user,
            symbol='AAPL',
            quantity=5
        )

    def test_investment_list_redirects_if_not_logged_in(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_investment_list_view_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'investments/investment_list.html')
        self.assertContains(response, 'AAPL')

    def test_add_investment_view_GET(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'investments/add_investment.html')

    def test_add_investment_view_POST(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.add_url, {
            'symbol': 'GOOGL',
            'quantity': 10
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Investment.objects.filter(user=self.user, symbol='GOOGL').exists())

    def test_investment_data_is_user_specific(self):
        other_user = User.objects.create_user(username='otheruser', password='pass456')
        Investment.objects.create(user=other_user, symbol='TSLA', quantity=3)

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.list_url)

        self.assertContains(response, 'AAPL')
        self.assertNotContains(response, 'TSLA')  
