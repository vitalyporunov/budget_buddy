from django.urls import path
from .views import investment_list, add_investment, delete_investment

urlpatterns = [
    path('', investment_list, name='investment_list'),
    path('add/', add_investment, name='add_investment'),
    path('delete/<int:investment_id>/', delete_investment, name='delete_investment'),
]
