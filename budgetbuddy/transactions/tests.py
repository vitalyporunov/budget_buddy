from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Transaction, Tag
from datetime import date

User = get_user_model()

class TransactionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='testpass')
        self.tag = Tag.objects.create(name='Food', user=self.user)

        self.transaction = Transaction.objects.create(
            user=self.user,
            amount=25.50,
            date=date.today(),
            category='expense',
            description='Lunch with friends'
        )
        self.transaction.tags.add(self.tag)

    def test_transaction_creation(self):
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(self.transaction.amount, 25.50)
        self.assertEqual(self.transaction.tags.first().name, 'Food')

    def test_transaction_list_view_requires_login(self):
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_transaction_list_view_logged_in(self):
        self.client.login(username='tester', password='testpass')
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lunch with friends')

    def test_add_transaction(self):
        self.client.login(username='tester', password='testpass')
        response = self.client.post(reverse('add_transaction'), {
            'amount': 100,
            'category': 'income',
            'description': 'Freelance work',
            'tags': [self.tag.id],
            'date': date.today()
        })
        self.assertEqual(Transaction.objects.count(), 2)
        self.assertRedirects(response, reverse('transaction_list'))

    def test_edit_transaction(self):
        self.client.login(username='tester', password='testpass')
        response = self.client.post(reverse('edit_transaction', args=[self.transaction.id]), {
            'amount': 30.00,
            'category': 'expense',
            'description': 'Updated lunch',
            'tags': [self.tag.id],
            'date': date.today()
        })
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.amount, 30.00)
        self.assertEqual(self.transaction.description, 'Updated lunch')

    def test_delete_transaction(self):
        self.client.login(username='tester', password='testpass')
        response = self.client.post(reverse('delete_transaction', args=[self.transaction.id]))
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertRedirects(response, reverse('transaction_list'))
