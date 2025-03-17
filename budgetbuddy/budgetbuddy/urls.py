"""
URL configuration for budgetbuddy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('transactions/', include('transactions.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('investments/', include('investments.urls')),
    path('savings/', include('savings.urls')),
    path('shared_budgeting/', include('shared_budgeting.urls')),
]

LOGIN_REDIRECT_URL = 'dashboard'  # Redirect to dashboard after login
LOGOUT_REDIRECT_URL = 'login'