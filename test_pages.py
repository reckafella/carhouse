#!/usr/bin/env python3
# ignore flake8
# flake8: noqa: E402, F401
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carhouse.settings')
django.setup()

from django.test import Client
from django.urls import reverse

# Test client
client = Client()

print("Testing actual page requests...")

try:
    # Test login page
    response = client.get(reverse('authentication:login'))
    print(f"✓ Login page: Status {response.status_code}")
    if response.status_code != 200:
        print(f"Response content: {response.content.decode()[:200]}...")
except Exception as e:
    print(f"✗ Login page Error: {e}")

try:
    # Test signup page  
    response = client.get(reverse('authentication:signup'))
    print(f"✓ Signup page: Status {response.status_code}")
    if response.status_code != 200:
        print(f"Response content: {response.content.decode()[:200]}...")
except Exception as e:
    print(f"✗ Signup page Error: {e}")

try:
    # Test contact page
    response = client.get(reverse('app:contact'))
    print(f"✓ Contact page: Status {response.status_code}")
    if response.status_code != 200:
        print(f"Response content: {response.content.decode()[:200]}...")
except Exception as e:
    print(f"✗ Contact page Error: {e}")

print("Page testing complete!")
