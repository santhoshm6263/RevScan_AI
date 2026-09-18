# Production Dockerfile for RevScan AI
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    DASHBOARD_PORT=8501

# Install system dependencies (including ADB client and curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    adb \
    curl \
    graphviz \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application source code
COPY . .

# Create persistent storage directories
RUN mkdir -p data/screenshots data/ui_trees data/knowledge

# Expose backend API and Streamlit dashboard ports
EXPOSE 8000 8501

# Default command launches both backend API and frontend dashboard
CMD ["python", "run.py", "all"]
