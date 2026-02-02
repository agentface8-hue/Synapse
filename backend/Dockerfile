FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Use bash to properly expand PORT environment variable
# Railway sets PORT dynamically, fallback to 8000 for local development
CMD ["/bin/bash", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
