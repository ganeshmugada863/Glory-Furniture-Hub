FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOME=/home/user

WORKDIR /home/user/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user

COPY requirements.txt /home/user/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/user/app/

RUN python manage.py collectstatic --noinput

RUN chown -R user:user /home/user/app && chmod -R 777 /home/user/app

USER user

EXPOSE 10000

CMD ["sh", "-c", "python manage.py migrate --noinput || true; exec gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120 glory_furniture.wsgi:application"]
