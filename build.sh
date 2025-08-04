#!/usr/bin/env bash
set -o errexit

# Update pip && install dependencies
#python3 -m pip install -r requirements.txt

# Collect static files
#python3 manage.py collectstatic --no-input --clear

# Apply database migrations
#python3 manage.py makemigrations

#python3 manage.py migrate

# create superuser
python3 ./manage.py create_superuser
