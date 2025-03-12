from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('signup/', views.signup, name='signup'),  
    path('login/', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'),  
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('debt/', views.debt_view, name='debt'),  
    path('budget/', views.budget_view, name='budget'), 
    path('goal/', views.goal_view, name='goal'),  
    path('reports/', views.reports_view, name='reports'),
    path('income-expense/', views.income_expense_view, name='income_expense'),
]

