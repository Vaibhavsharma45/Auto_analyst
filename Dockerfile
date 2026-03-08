# DataMind Pro — HuggingFace Spaces Dockerfile
FROM python:3.11-slim

# System dependencies for matplotlib, scipy, etc.
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker cache)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create required directories
RUN mkdir -p data/uploads reports/output data

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

# HuggingFace uses port 7860
EXPOSE 7860

# Start with gunicorn on port 7860
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "180", "--max-requests", "1000"]