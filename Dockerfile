FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Set permissions for Hugging Face non-root user (UID 1000)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app && chmod -R 775 /app
USER appuser

EXPOSE 7860

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn glory_furniture.wsgi:application --bind 0.0.0.0:7860 --workers 3 --timeout 120"]
