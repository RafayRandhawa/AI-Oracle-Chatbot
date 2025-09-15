# backend/Dockerfile
FROM python:3.11-bullseye

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

# Install prerequisites
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

# Copy Oracle Instant Client (only once!)
COPY instantclient_23_9 /opt/oracle/instantclient

# Configure linker and env
RUN echo /opt/oracle/instantclient > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient
ENV PATH=$LD_LIBRARY_PATH:$PATH
ENV INSTANT_CLIENT=/opt/oracle/instantclient

# Fix broken libclntsh symlink
RUN cd /opt/oracle/instantclient && \
    rm -f libclntsh.so && \
    ln -s libclntsh.so.23.1 libclntsh.so

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
