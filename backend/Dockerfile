# backend/Dockerfile
# Use a stable Debian base to avoid apt repo issues
FROM python:3.11-bullseye

# Set working dir
WORKDIR /app

# Make apt quiet and noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install apt prerequisites and runtime deps (ca-certificates first)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      apt-transport-https \
      gnupg \
      wget \
      unzip \
      curl \
      libaio1 \
 && rm -rf /var/lib/apt/lists/*


# Use provided extracted instantclient_23_9 folder
COPY instantclient_23_9 /opt/oracle/instantclient
RUN echo /opt/oracle/instantclient > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig
# Env for Oracle client
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient
ENV PATH=$LD_LIBRARY_PATH:$PATH

# Copy & install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
