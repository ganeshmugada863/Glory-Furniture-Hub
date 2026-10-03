FROM python:3.12-alpine

WORKDIR /app

COPY redirect_server.py /app/

EXPOSE 10000

ENV PORT=10000 \
    PYTHONUNBUFFERED=1

CMD ["python", "redirect_server.py"]
