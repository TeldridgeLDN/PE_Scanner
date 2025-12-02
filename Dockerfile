# PE Scanner Backend API - Railway Deployment
# Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (if needed for any packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn for production server
RUN pip install --no-cache-dir gunicorn>=21.0.0

# Copy application code
COPY src/ ./src/
COPY config.yaml .
COPY pyproject.toml .
COPY README.md .

# Install package in editable mode (so imports work correctly)
RUN pip install -e .

# Expose port (Railway will provide $PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Start gunicorn with proper configuration
# Use shell form to properly expand $PORT environment variable
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info --access-logfile - --error-logfile - src.pe_scanner.api.app:app

