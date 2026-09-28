#!/bin/bash
echo "=== Glory Furniture Hub Vercel Build ==="
echo "1. Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo "2. Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "=== Build Finished Successfully ==="
