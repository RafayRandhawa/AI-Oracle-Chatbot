# Oracle AI Chatbot - Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Oracle database accessible from deployment environment

### 1. Configure Environment
```bash
# Copy the example environment files
cp env.example .env
cp frontend/env.example frontend/.env

# Edit .env files with your actual configuration
# Update database credentials, API keys, etc.
```

### 2. Deploy the Application

#### Windows:
```powershell
.\deploy.ps1
```

#### Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

#### Manual Deployment:
```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **N8N Interface**: http://localhost/n8n (if enabled)

## Service Management

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Clean Up
```bash
docker-compose down --volumes --remove-orphans
docker system prune -f
```

## Health Checks
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000/health
- Nginx: http://localhost/health

## Configuration Files
- `docker-compose.yml` - Service orchestration
- `nginx/nginx.conf` - Main nginx configuration
- `nginx/conf.d/default.conf` - Site routing
- `backend/Dockerfile` - Backend container
- `frontend/Dockerfile` - Frontend container

## Troubleshooting
1. Check if ports 80, 8000, 3000 are available
2. Verify Oracle database connectivity
3. Check environment variables in .env file
4. Review service logs for errors

For detailed information, see [CHANGES.md](CHANGES.md).
