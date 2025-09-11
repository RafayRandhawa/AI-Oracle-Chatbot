#!/bin/bash

# Oracle AI Chatbot Deployment Script
# This script handles the complete deployment of the Oracle AI Chatbot application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="oracle-ai-chatbot"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    log_info "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env_file() {
    log_info "Checking environment configuration..."
    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found. Creating from template..."
        create_env_file
    else
        log_success "Environment file found"
    fi
}

# Create .env file from template
create_env_file() {
    cat > .env << EOF
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
EOF
    log_warning "Please update the .env file with your actual configuration values"
}

# Build and start services
deploy_services() {
    log_info "Building and starting services..."
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans
    
    # Build and start services
    log_info "Building Docker images..."
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    log_info "Starting services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    log_success "Services started successfully"
}

# Check service health
check_health() {
    log_info "Checking service health..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Backend is healthy"
    else
        log_warning "Backend health check failed"
    fi
    
    # Check frontend health
    if curl -f http://localhost:3000/health &> /dev/null; then
        log_success "Frontend is healthy"
    else
        log_warning "Frontend health check failed"
    fi
    
    # Check nginx health
    if curl -f http://localhost/health &> /dev/null; then
        log_success "Nginx is healthy"
    else
        log_warning "Nginx health check failed"
    fi
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo ""
    echo "Services:"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    echo ""
    echo "Access URLs:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost/api"
    echo "  N8N (if enabled): http://localhost/n8n"
    echo ""
    echo "Logs:"
    echo "  View all logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "  Backend logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f backend"
    echo "  Frontend logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f frontend"
    echo "  Nginx logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f nginx"
}

# Main deployment function
main() {
    log_info "Starting Oracle AI Chatbot deployment..."
    
    check_docker
    check_env_file
    deploy_services
    check_health
    show_status
    
    log_success "Deployment completed successfully!"
    log_info "You can now access the application at http://localhost"
}

# Handle command line arguments
case "${1:-}" in
    "stop")
        log_info "Stopping services..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose -f $DOCKER_COMPOSE_FILE restart
        log_success "Services restarted"
        ;;
    "logs")
        docker-compose -f $DOCKER_COMPOSE_FILE logs -f
        ;;
    "status")
        show_status
        ;;
    "clean")
        log_info "Cleaning up Docker resources..."
        docker-compose -f $DOCKER_COMPOSE_FILE down --volumes --remove-orphans
        docker system prune -f
        log_success "Cleanup completed"
        ;;
    *)
        main
        ;;
esac
