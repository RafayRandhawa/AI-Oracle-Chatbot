# Oracle AI Chatbot Deployment Script for Windows PowerShell
# This script handles the complete deployment of the Oracle AI Chatbot application

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "logs", "status", "clean")]
    [string]$Action = "start"
)

# Configuration
$PROJECT_NAME = "oracle-ai-chatbot"
$DOCKER_COMPOSE_FILE = "docker-compose.yml"
$ENV_FILE = ".env"

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is installed
function Test-Docker {
    Write-Info "Checking Docker installation..."
    
    try {
        $dockerVersion = docker --version
        $composeVersion = docker-compose --version
        Write-Success "Docker and Docker Compose are installed"
        Write-Host "Docker: $dockerVersion" -ForegroundColor Gray
        Write-Host "Compose: $composeVersion" -ForegroundColor Gray
    }
    catch {
        Write-Error "Docker or Docker Compose is not installed. Please install Docker Desktop first."
        exit 1
    }
}

# Check if .env file exists
function Test-EnvFile {
    Write-Info "Checking environment configuration..."
    
    if (-not (Test-Path $ENV_FILE)) {
        Write-Warning ".env file not found. Creating from template..."
        New-EnvFile
    }
    else {
        Write-Success "Environment file found"
    }
}

# Create .env file from template
function New-EnvFile {
    $envContent = @"
# Database Configuration
DB_HOST=your_oracle_host
DB_PORT=1521
DB_SERVICE_NAME=your_service_name
DB_USERNAME=your_username
DB_PASSWORD=your_password

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# N8N Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/03e650c2-18be-4c37-903a-4e99bddcc8b1

# Pinecone Configuration (if using)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# Google AI Configuration (if using)
GOOGLE_AI_API_KEY=your_google_ai_api_key

# OpenAI Configuration (if using)
OPENAI_API_KEY=your_openai_api_key

# Application Configuration
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
"@
    
    $envContent | Out-File -FilePath $ENV_FILE -Encoding UTF8
    Write-Warning "Please update the .env file with your actual configuration values"
}

# Build and start services
function Start-Services {
    Write-Info "Building and starting services..."
    
    # Stop existing containers
    Write-Info "Stopping existing containers..."
    docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans
    
    # Build and start services
    Write-Info "Building Docker images..."
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    Write-Info "Starting services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    Write-Success "Services started successfully"
}

# Check service health
function Test-Health {
    Write-Info "Checking service health..."
    
    # Wait for services to be ready
    Start-Sleep -Seconds 10
    
    # Check backend health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend is healthy"
        }
    }
    catch {
        Write-Warning "Backend health check failed"
    }
    
    # Check frontend health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Frontend is healthy"
        }
    }
    catch {
        Write-Warning "Frontend health check failed"
    }
    
    # Check nginx health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Nginx is healthy"
        }
    }
    catch {
        Write-Warning "Nginx health check failed"
    }
}

# Show deployment status
function Show-Status {
    Write-Info "Deployment Status:"
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Cyan
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost" -ForegroundColor White
    Write-Host "  Backend API: http://localhost/api" -ForegroundColor White
    Write-Host "  N8N (if enabled): http://localhost/n8n" -ForegroundColor White
    Write-Host ""
    Write-Host "Logs:" -ForegroundColor Cyan
    Write-Host "  View all logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f" -ForegroundColor White
    Write-Host "  Backend logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f backend" -ForegroundColor White
    Write-Host "  Frontend logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f frontend" -ForegroundColor White
    Write-Host "  Nginx logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f nginx" -ForegroundColor White
}

# Main deployment function
function Start-Deployment {
    Write-Info "Starting Oracle AI Chatbot deployment..."
    
    Test-Docker
    Test-EnvFile
    Start-Services
    Test-Health
    Show-Status
    
    Write-Success "Deployment completed successfully!"
    Write-Info "You can now access the application at http://localhost"
}

# Handle different actions
switch ($Action) {
    "start" {
        Start-Deployment
    }
    "stop" {
        Write-Info "Stopping services..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
        Write-Success "Services stopped"
    }
    "restart" {
        Write-Info "Restarting services..."
        docker-compose -f $DOCKER_COMPOSE_FILE restart
        Write-Success "Services restarted"
    }
    "logs" {
        docker-compose -f $DOCKER_COMPOSE_FILE logs -f
    }
    "status" {
        Show-Status
    }
    "clean" {
        Write-Info "Cleaning up Docker resources..."
        docker-compose -f $DOCKER_COMPOSE_FILE down --volumes --remove-orphans
        docker system prune -f
        Write-Success "Cleanup completed"
    }
}
