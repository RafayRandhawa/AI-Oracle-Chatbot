# Backend Dockerfile for Oracle AI Chatbot
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies and security updates
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libaio1 \
    wget \
    unzip \
    curl \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Oracle Instant Client
RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linux.x64-21.13.0.0.0dbru.zip \
    && unzip instantclient-basic-linux.x64-21.13.0.0.0dbru.zip \
    && rm instantclient-basic-linux.x64-21.13.0.0.0dbru.zip \
    && mv instantclient_21_13 /opt/oracle/instantclient \
    && echo /opt/oracle/instantclient > /etc/ld.so.conf.d/oracle-instantclient.conf \
    && ldconfig

# Set Oracle environment variables
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient
ENV ORACLE_HOME=/opt/oracle/instantclient

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
