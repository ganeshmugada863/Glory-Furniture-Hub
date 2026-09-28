#!/bin/bash
echo "=== Glory Furniture Hub Vercel Build ==="
mkdir -p staticfiles
python3 -m pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt --break-system-packages || true
python3 manage.py collectstatic --noinput || python manage.py collectstatic --noinput
echo "=== Build Finished Successfully ==="
