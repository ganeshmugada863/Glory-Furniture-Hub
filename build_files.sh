#!/bin/bash
echo "=== Glory Furniture Hub Vercel Build ==="
mkdir -p staticfiles
python3 -m pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt --break-system-packages || true
python3 manage.py collectstatic --noinput --clear || python manage.py collectstatic --noinput --clear
# Mirror static files inside static/ folder so /static/(.*) matches static/$1 directly
mkdir -p staticfiles/static
cp -r staticfiles/css staticfiles/static/ 2>/dev/null || true
cp -r staticfiles/images staticfiles/static/ 2>/dev/null || true
cp -r staticfiles/js staticfiles/static/ 2>/dev/null || true
cp -r staticfiles/admin staticfiles/static/ 2>/dev/null || true
cp staticfiles/favicon.svg staticfiles/static/ 2>/dev/null || true
echo "=== Static files count in staticfiles ==="
ls -la staticfiles
echo "=== Build Finished Successfully ==="
