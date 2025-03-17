from django.urls import path
from .views import savings_goal_list, add_savings_goal, update_savings_goal, delete_savings_goal

urlpatterns = [
    path('', savings_goal_list, name='savings_goal_list'),
    path('add/', add_savings_goal, name='add_savings_goal'),
    path('update/<int:goal_id>/', update_savings_goal, name='update_savings_goal'),
    path('delete/<int:goal_id>/', delete_savings_goal, name='delete_savings_goal'),
]
