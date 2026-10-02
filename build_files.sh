#!/bin/bash
echo "=== Glory Furniture Hub Vercel Build ==="
mkdir -p staticfiles

python3 -m pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt --break-system-packages || true

# Run database migrations
python3 manage.py migrate --noinput || python manage.py migrate --noinput || true

# Run standard Django collectstatic
python3 manage.py collectstatic --noinput --clear || python manage.py collectstatic --noinput --clear

# Guarantee all static project files are copied into staticfiles root
cp -rf static/* staticfiles/ 2>/dev/null || true

# Mirror static files inside static/ folder so /static/(.*) matches static/$1 directly
mkdir -p staticfiles/static
cp -rf staticfiles/css staticfiles/static/ 2>/dev/null || true
cp -rf staticfiles/images staticfiles/static/ 2>/dev/null || true
cp -rf staticfiles/js staticfiles/static/ 2>/dev/null || true
cp -rf staticfiles/admin staticfiles/static/ 2>/dev/null || true
cp -f staticfiles/favicon.svg staticfiles/static/ 2>/dev/null || true

# Mirror media assets so /media/(.*) is served directly by Vercel CDN
mkdir -p staticfiles/media
cp -rf media/* staticfiles/media/ 2>/dev/null || true

echo "=== Files in staticfiles/static/css ==="
ls -la staticfiles/static/css || true
echo "=== Files in staticfiles/static/images ==="
ls -la staticfiles/static/images || true
echo "=== Files in staticfiles/media/products ==="
ls -la staticfiles/media/products 2>/dev/null | head -n 10 || true
echo "=== Build Finished Successfully ==="
