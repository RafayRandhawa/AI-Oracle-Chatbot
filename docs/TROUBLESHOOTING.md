# Troubleshooting and FAQ Guide

## Overview

This comprehensive troubleshooting guide covers common issues, solutions, and frequently asked questions for the Oracle AI Chatbot project. Use this guide to diagnose and resolve problems across all components of the system.

---

## 🚨 Quick Diagnostic Commands

### System Health Check

```bash
# Check all services status
docker-compose ps

# Check service health endpoints
curl http://localhost/health
curl http://localhost:8000/health
curl http://localhost:3000/health
curl http://localhost:5678/health

# View recent logs
docker-compose logs --tail=50
```

### Service-Specific Checks

```bash
# Backend service
docker-compose logs backend --tail=20
curl http://localhost:8000/health

# Frontend service  
docker-compose logs frontend --tail=20
curl http://localhost:3000/health

# N8N service
docker-compose logs n8n --tail=20
curl http://localhost:5678/health

# Nginx service
docker-compose logs nginx --tail=20
curl http://localhost/health
```

---

## 🔧 Common Issues and Solutions

### 1. Docker and Container Issues

#### Issue: Containers won't start

**Symptoms:**
- `docker-compose up` fails
- Containers exit immediately
- Port conflicts

**Solutions:**

```bash
# Check for port conflicts
netstat -tulpn | grep :80
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
netstat -tulpn | grep :5678

# Stop conflicting services
sudo systemctl stop apache2  # If using port 80
sudo systemctl stop nginx    # If using port 80

# Clean up Docker resources
docker-compose down --volumes --remove-orphans
docker system prune -f

# Rebuild containers
docker-compose up -d --build
```

#### Issue: Out of disk space

**Symptoms:**
- Docker build fails
- Containers can't start
- "No space left on device" errors

**Solutions:**

```bash
# Check disk usage
df -h
docker system df

# Clean up Docker resources
docker system prune -a -f
docker volume prune -f
docker image prune -a -f

# Remove unused containers
docker container prune -f
```

#### Issue: Permission denied errors

**Symptoms:**
- "Permission denied" when accessing files
- Container can't write to volumes
- File permission errors

**Solutions:**

```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .

# Fix Docker socket permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker service
sudo systemctl restart docker
```

---

### 2. Backend Issues

#### Issue: Database connection failed

**Symptoms:**
- "Database connection failed" errors
- Oracle client not found
- Authentication errors

**Solutions:**

```bash
# Check Oracle Instant Client installation
docker-compose exec backend ls -la /opt/oracle/instantclient

# Verify environment variables
docker-compose exec backend env | grep DB_

# Test database connectivity
docker-compose exec backend python -c "
import oracledb
try:
    conn = oracledb.connect(user='your_user', password='your_pass', dsn='your_dsn')
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"

# Check Oracle service status
docker-compose exec backend ping your_oracle_host
```

**Environment Configuration:**
```env
# Verify these in your .env file
DB_HOST=your_oracle_host
DB_PORT=1521
DB_SERVICE_NAME=your_service_name
DB_USERNAME=your_username
DB_PASSWORD=your_password
INSTANT_CLIENT=/opt/oracle/instantclient
```

#### Issue: JWT authentication errors

**Symptoms:**
- "Invalid token" errors
- Authentication failures
- Cookie issues

**Solutions:**

```bash
# Check JWT configuration
docker-compose exec backend env | grep JWT_

# Verify JWT secret key
echo $JWT_SECRET_KEY | wc -c  # Should be at least 32 characters

# Test authentication endpoint
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Check cookie settings
curl -I http://localhost:8000/auth/login
```

**JWT Configuration:**
```env
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Issue: AI service errors

**Symptoms:**
- "AI service unavailable" errors
- Gemini API failures
- SQL generation failures

**Solutions:**

```bash
# Check Gemini API key
docker-compose exec backend env | grep GOOGLE_AI_API_KEY

# Test Gemini API connectivity
docker-compose exec backend python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content('Hello')
    print('Gemini API connection successful')
except Exception as e:
    print(f'Gemini API connection failed: {e}')
"

# Check API quota
curl -H "Authorization: Bearer $GOOGLE_AI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

---

### 3. Frontend Issues

#### Issue: Frontend won't load

**Symptoms:**
- Blank page
- "Cannot connect to server" errors
- Build failures

**Solutions:**

```bash
# Check frontend build
docker-compose exec frontend npm run build

# Check environment variables
docker-compose exec frontend env | grep REACT_APP_

# Test frontend health
curl http://localhost:3000/health

# Check nginx configuration
docker-compose exec frontend nginx -t
```

**Environment Configuration:**
```env
# Verify these in frontend/.env
REACT_APP_API_BASE_URL=http://localhost/api
REACT_APP_N8N_URL=http://localhost/webhook/your-webhook-id
```

#### Issue: Authentication redirects

**Symptoms:**
- Infinite redirect loops
- Login page not loading
- Session not persisting

**Solutions:**

```bash
# Check authentication flow
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer your-token"

# Test login endpoint
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Check CORS configuration
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Requested-With" \
  -X OPTIONS http://localhost:8000/auth/login
```

#### Issue: Chat messages not saving

**Symptoms:**
- Messages disappear on refresh
- Session not persisting
- Database save failures

**Solutions:**

```bash
# Check session endpoints
curl -X GET http://localhost:8000/sessions/list \
  -H "Authorization: Bearer your-token"

# Test message storage
curl -X POST http://localhost:8000/sessions/1/messages \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "test message"}'

# Check database tables
docker-compose exec backend python -c "
from db_handler import get_connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM chat_sessions')
print(f'Sessions: {cursor.fetchone()[0]}')
cursor.execute('SELECT COUNT(*) FROM chat_messages')
print(f'Messages: {cursor.fetchone()[0]}')
conn.close()
"
```

---

### 4. N8N Workflow Issues

#### Issue: Webhook not triggering

**Symptoms:**
- Messages not processed
- Workflow not executing
- N8N service errors

**Solutions:**

```bash
# Check N8N service status
docker-compose logs n8n --tail=20

# Test webhook endpoint
curl -X POST http://localhost:5678/webhook-test/your-webhook-id \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Check N8N health
curl http://localhost:5678/health

# Verify workflow is active
curl -X GET http://localhost:5678/api/v1/workflows \
  -H "Authorization: Bearer your-n8n-token"
```

#### Issue: AI generation failures

**Symptoms:**
- "AI generation failed" errors
- Empty responses
- Timeout errors

**Solutions:**

```bash
# Check Gemini API in N8N
docker-compose exec n8n env | grep GOOGLE_AI_API_KEY

# Test workflow manually
curl -X POST http://localhost:5678/api/v1/workflows/workflow-id/execute \
  -H "Authorization: Bearer your-n8n-token" \
  -H "Content-Type: application/json" \
  -d '{"message": "test query"}'

# Check N8N execution logs
curl -X GET http://localhost:5678/api/v1/executions \
  -H "Authorization: Bearer your-n8n-token"
```

---

### 5. Nginx Issues

#### Issue: Reverse proxy not working

**Symptoms:**
- 502 Bad Gateway errors
- Service unavailable
- Routing failures

**Solutions:**

```bash
# Check nginx configuration
docker-compose exec nginx nginx -t

# Test upstream services
curl http://localhost:8000/health  # Backend
curl http://localhost:3000/health # Frontend
curl http://localhost:5678/health # N8N

# Check nginx logs
docker-compose logs nginx --tail=20

# Restart nginx
docker-compose restart nginx
```

#### Issue: SSL/HTTPS problems

**Symptoms:**
- Certificate errors
- Mixed content warnings
- HTTPS redirect issues

**Solutions:**

```bash
# Check SSL certificate
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:443 -servername localhost

# Verify certificate chain
curl -I https://localhost/health
```

---

## 📋 Frequently Asked Questions

### General Questions

#### Q: How do I reset the entire system?

**A:** Complete system reset:

```bash
# Stop all services
docker-compose down

# Remove all containers, volumes, and networks
docker-compose down --volumes --remove-orphans
docker system prune -a -f

# Remove environment files (optional)
rm .env frontend/.env

# Recreate environment files
cp env.example .env
cp frontend/env.example frontend/.env

# Edit configuration files with your settings
# Then restart
docker-compose up -d --build
```

#### Q: How do I update the application?

**A:** Application update process:

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Check service status
docker-compose ps
```

#### Q: How do I backup my data?

**A:** Data backup procedure:

```bash
# Backup database (if using external Oracle)
# Use your Oracle backup tools

# Backup application data
docker-compose exec backend python -c "
from db_handler import get_connection
import json
conn = get_connection()
cursor = conn.cursor()

# Export sessions
cursor.execute('SELECT * FROM chat_sessions')
sessions = cursor.fetchall()

# Export messages  
cursor.execute('SELECT * FROM chat_messages')
messages = cursor.fetchall()

with open('/app/backup.json', 'w') as f:
    json.dump({'sessions': sessions, 'messages': messages}, f)

conn.close()
print('Backup completed')
"

# Copy backup file
docker cp container_id:/app/backup.json ./backup_$(date +%Y%m%d).json
```

### Configuration Questions

#### Q: How do I change the database connection?

**A:** Database configuration:

1. **Edit environment file:**
```env
# Update .env file
DB_HOST=your_new_host
DB_PORT=1521
DB_SERVICE_NAME=your_service_name
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

2. **Restart backend service:**
```bash
docker-compose restart backend
```

3. **Test connection:**
```bash
docker-compose exec backend python -c "
from db_handler import get_connection
conn = get_connection()
print('Connection successful')
conn.close()
"
```

#### Q: How do I configure SSL/HTTPS?

**A:** SSL configuration:

1. **Generate SSL certificates:**
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

2. **Update nginx configuration:**
```nginx
# Add SSL configuration to nginx/conf.d/default.conf
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... rest of configuration
}
```

3. **Restart nginx:**
```bash
docker-compose restart nginx
```

#### Q: How do I change the AI model?

**A:** AI model configuration:

1. **Update backend configuration:**
```python
# In ai_handler.py
GEMINI_MODEL = "models/gemini-2.0-flash-lite-preview"  # Change model here
```

2. **Update N8N workflow:**
- Open N8N interface
- Edit Gemini AI node
- Change model name
- Save workflow

3. **Restart services:**
```bash
docker-compose restart backend n8n
```

### Performance Questions

#### Q: How do I improve performance?

**A:** Performance optimization:

1. **Database optimization:**
```sql
-- Add indexes for common queries
CREATE INDEX idx_employees_dept_id ON employees(dept_id);
CREATE INDEX idx_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_attendance_emp_date ON attendance(emp_id, attendance_date);
```

2. **Application optimization:**
```bash
# Increase Docker resources
# Edit docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

3. **Caching:**
```python
# Enable metadata caching
# In db_handler.py
_cached_metadata = None  # Already implemented
```

#### Q: How do I monitor system performance?

**A:** Performance monitoring:

```bash
# Check resource usage
docker stats

# Check service health
curl http://localhost/health
curl http://localhost:8000/health

# Monitor logs
docker-compose logs -f

# Check database performance
docker-compose exec backend python -c "
from db_handler import get_connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM employees')
print(f'Employees: {cursor.fetchone()[0]}')
conn.close()
"
```

### Security Questions

#### Q: How do I secure the application?

**A:** Security hardening:

1. **Environment security:**
```bash
# Use strong passwords
JWT_SECRET_KEY=your-very-long-random-secret-key-at-least-32-characters
DB_PASSWORD=your-strong-database-password

# Restrict file permissions
chmod 600 .env
chmod 600 frontend/.env
```

2. **Network security:**
```bash
# Use firewall rules
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8000  # Block direct backend access
sudo ufw deny 3000  # Block direct frontend access
sudo ufw deny 5678  # Block direct N8N access
```

3. **Docker security:**
```yaml
# Use non-root users in Dockerfile
USER 1000:1000

# Limit container resources
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
```

#### Q: How do I enable authentication?

**A:** Authentication setup:

1. **Create user accounts:**
```sql
-- Connect to Oracle database
INSERT INTO users (user_id, username, password_hash, email) 
VALUES (users_seq.NEXTVAL, 'admin', '$2b$12$hashed_password', 'admin@company.com');
```

2. **Configure JWT:**
```env
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. **Test authentication:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

---

## 🆘 Getting Help

### Log Collection

When reporting issues, collect these logs:

```bash
# System information
docker --version
docker-compose --version
uname -a

# Service logs
docker-compose logs > system_logs.txt
docker-compose ps > service_status.txt

# Configuration
cat .env > environment_config.txt
cat frontend/.env > frontend_config.txt
cat docker-compose.yml > docker_config.txt
```

### Support Channels

- **GitHub Issues**: [Project Repository Issues](https://github.com/your-repo/issues)
- **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)
- **Community**: [Discord/Slack Channel](https://your-community-link)

### Reporting Issues

When reporting issues, include:

1. **System Information**
   - OS version
   - Docker version
   - Available resources

2. **Error Details**
   - Exact error messages
   - Steps to reproduce
   - Expected vs actual behavior

3. **Logs**
   - Service logs
   - Error logs
   - Configuration files

4. **Environment**
   - Environment variables (sanitized)
   - Database configuration
   - Network setup

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Oracle Database Documentation](https://docs.oracle.com/en/database/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [N8N Documentation](https://docs.n8n.io/)
- [Nginx Documentation](https://nginx.org/en/docs/)

