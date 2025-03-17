from django.urls import path
from .views import (
    register_view, login_view, logout_view,  # HTML Views
    RegisterAPIView, LoginAPIView, LogoutAPIView  # API Views
)

urlpatterns = [
    # 🌟 Web-Based Authentication (HTML Pages)
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # 🔹 API-Based Authentication (REST Endpoints)
    path('api/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
]
