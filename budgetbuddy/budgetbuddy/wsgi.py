"""
WSGI config for budgetbuddy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
import sys
print("PYTHON PATH:", sys.path)
print("FILES:", os.listdir('.'))

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budgetbuddy.settings')

# Get the WSGI application
application = get_wsgi_application()


