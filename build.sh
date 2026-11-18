#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Ensure database directory exists for SQLite fallback
mkdir -p database

# Collect all static files for WhiteNoise
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Create or update super admin for custom admin panel
python manage.py create_panel_admin
