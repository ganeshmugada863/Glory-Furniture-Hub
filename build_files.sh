#!/bin/bash
echo "=== Glory Furniture Hub Vercel Build ==="
mkdir -p staticfiles
python3 -m pip install -r requirements.txt || pip install -r requirements.txt
python3 manage.py collectstatic --noinput || python manage.py collectstatic --noinput
echo "=== Build Finished Successfully ==="
