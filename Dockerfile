# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (incl. curl) — update+install in one layer, then clean
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    libxml2 \
    libxslt1.1 \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Optional connectivity check
RUN curl -I https://google.com

WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && pip check

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
