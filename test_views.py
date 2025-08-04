#!/usr/bin/env python3
# ignore flake8
# flake8: noqa: E402, F401
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carhouse.settings')
django.setup()

from django.test import RequestFactory
from authentication.views.auth.auth import LoginView, SignupView
from app.views.views import ContactView

# Test the views
rf = RequestFactory()

print("Testing views...")

try:
    # Test LoginView
    request = rf.get('/login')
    view = LoginView()
    view.setup(request)
    print("✓ LoginView OK")
except Exception as e:
    print(f"✗ LoginView Error: {e}")

try:
    # Test SignupView
    request = rf.get('/signup')
    view = SignupView()
    view.setup(request)
    print("✓ SignupView OK")
except Exception as e:
    print(f"✗ SignupView Error: {e}")

try:
    # Test ContactView
    request = rf.get('/contact')
    view = ContactView()
    view.setup(request)
    print("✓ ContactView OK")
except Exception as e:
    print(f"✗ ContactView Error: {e}")

print("Testing complete!")
