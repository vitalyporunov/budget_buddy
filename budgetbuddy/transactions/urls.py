from django.urls import path
from .views import transaction_list, add_transaction

urlpatterns = [
    path('', transaction_list, name='transaction_list'),
    path('add/', add_transaction, name='add_transaction'),
]
