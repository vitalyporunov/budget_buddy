from . import views
from django.urls import path
from .views import shared_budget_list, create_shared_budget, budget_detail, add_expense

urlpatterns = [
    path('', shared_budget_list, name='shared_budget_list'),
    path('create/', create_shared_budget, name='create_shared_budget'),
    path('<int:budget_id>/', budget_detail, name='budget_detail'),
    path('<int:budget_id>/add_expense/', add_expense, name='add_expense'),
    path('budget/<int:pk>/edit/', views.edit_shared_budget, name='edit_shared_budget'),
    path('budget/<int:pk>/delete/', views.delete_shared_budget, name='delete_shared_budget'),
]
