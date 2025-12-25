FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
# We install gcc and python3-dev only to compile asyncpg
# Then we clean up the apt cache to keep the image slim
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install dependencies
# comments: upgrading pip helps avoid build issues with newer python versions
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# # Copy application code
COPY . .

# # Copy application code
EXPOSE 8000

# # Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# FROM python:3.12-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     postgresql-client \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY . .

# # Expose port
# EXPOSE 8000

# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# # Run application
# CMD ["python", "-m", "docker build -t identity-service .", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
