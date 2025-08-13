# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (incl. curl) — update and install in ONE layer, then clean
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi8 \
    libxml2 \
    libxslt1.1 \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Optional: quick connectivity check (after curl + certs exist)
RUN curl -I https://google.com

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--hos]()
