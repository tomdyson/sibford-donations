FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Change to the Django project directory
WORKDIR /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create script to run migrations and start the application
RUN echo '#!/bin/bash\npython manage.py migrate\nexec gunicorn sibford_donations.wsgi:application --bind 0.0.0.0:${PORT:-8000}' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Run migrations and start application
CMD ["/app/entrypoint.sh"]
