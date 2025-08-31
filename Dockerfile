FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# # Install system dependencies (optional)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the Django app
COPY app /app

# Add Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "joefish.wsgi:application"]