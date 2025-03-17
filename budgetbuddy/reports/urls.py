from django.urls import path
from .views import financial_report, generate_pdf

urlpatterns = [
    path('', financial_report, name='financial_report'),
    path('generate_pdf/', generate_pdf, name='generate_pdf'),
]
