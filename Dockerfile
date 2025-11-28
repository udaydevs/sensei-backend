# Use official Python runtime
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (important for qdrant + google sdk)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Expose Cloud Run port
ENV PORT=8080

# Start FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
