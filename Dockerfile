FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOME=/home/user

WORKDIR /home/user/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user

COPY requirements.txt /home/user/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/user/app/

RUN python manage.py collectstatic --noinput

RUN chown -R user:user /home/user/app

USER user

EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120", "glory_furniture.wsgi:application"]
