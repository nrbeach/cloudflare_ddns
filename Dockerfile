FROM python:alpine

WORKDIR /app

COPY requirements.txt .
COPY cloudflare_ddns.py .

RUN pip install -r requirements.txt

ENTRYPOINT python3 cloudflare_ddns.py
