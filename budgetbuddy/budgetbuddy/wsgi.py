"""
WSGI config for budgetbuddy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
import os, sys
print("DEBUG:: PATH", sys.path)
print("DEBUG:: FILES", os.listdir("."))

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budgetbuddy.settings')

application = get_wsgi_application()



