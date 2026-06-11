# Brahmakaal — Dockerfile for Coolify deployment
FROM python:3.11-slim

WORKDIR /app

# Install system deps (psycopg2 needs libpq)
RUN apt-get update && apt-get install -y \
    gcc libpq-dev wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -u 10014 appuser

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download ephemeris at build time (not in git)
RUN wget -q "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de421.bsp" -O de421.bsp

# Copy source
COPY . .

# Fix ownership
RUN chown -R appuser:appuser /app

USER 10014

EXPOSE 8888

# Start server
CMD ["python", "start_production.py"]
