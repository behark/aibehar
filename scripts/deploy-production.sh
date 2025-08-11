#!/bin/bash

# Production Deployment Script for Open WebUI
# This script handles secure production deployment with all necessary checks

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if running as root (not recommended for production)
if [[ $EUID -eq 0 ]]; then
    warning "Running as root is not recommended for production deployment"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Pre-deployment checks
log "🔍 Running pre-deployment checks..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    error "Docker Compose is not installed. Please install Docker Compose first."
fi

# Check available disk space (minimum 10GB)
AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
REQUIRED_SPACE=10485760  # 10GB in KB
if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    error "Insufficient disk space. At least 10GB required."
fi

# Check available memory (minimum 4GB)
AVAILABLE_RAM=$(free -m | awk 'NR==2{print $7}')
REQUIRED_RAM=4096  # 4GB in MB
if [ "$AVAILABLE_RAM" -lt "$REQUIRED_RAM" ]; then
    warning "Less than 4GB RAM available. Performance may be impacted."
fi

success "Pre-deployment checks passed!"

# Environment setup
log "📋 Setting up environment configuration..."

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.production ]; then
        cp .env.production .env
        log "Created .env from .env.production template"
    else
        error ".env.production template not found. Please create environment configuration."
    fi
fi

# Check for required environment variables
source .env

REQUIRED_VARS=("WEBUI_SECRET_KEY" "POSTGRES_PASSWORD" "POSTGRES_USER")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "CHANGE_THIS_SECURE_PASSWORD" ] || [ "${!var}" = "your-super-secure-secret-key-at-least-32-characters-long-change-this" ]; then
        error "Please set secure value for $var in .env file"
    fi
done

# Generate secure secrets if needed
if [ ${#WEBUI_SECRET_KEY} -lt 32 ]; then
    warning "WEBUI_SECRET_KEY is too short. Generating secure key..."
    SECURE_KEY=$(openssl rand -hex 32)
    sed -i "s/WEBUI_SECRET_KEY=.*/WEBUI_SECRET_KEY=$SECURE_KEY/" .env
    success "Generated secure WEBUI_SECRET_KEY"
fi

# Create necessary directories
log "📁 Creating necessary directories..."
mkdir -p logs backups nginx/ssl monitoring/grafana/{dashboards,datasources}

# Set proper permissions
chmod 700 backups
chmod 755 logs

# Pull latest images
log "📥 Pulling latest Docker images..."
docker-compose -f docker-compose.production.yml pull

# Build custom images
log "🔨 Building application images..."
docker-compose -f docker-compose.production.yml build --no-cache

# Database initialization
log "🗃️ Initializing database..."
docker-compose -f docker-compose.production.yml up -d db redis
sleep 10

# Wait for database to be ready
log "⏳ Waiting for database to be ready..."
for i in {1..30}; do
    if docker-compose -f docker-compose.production.yml exec -T db pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" &>/dev/null; then
        success "Database is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        error "Database failed to start after 5 minutes"
    fi
    sleep 10
done

# Start Ollama and download models
log "🤖 Starting Ollama and downloading models..."
docker-compose -f docker-compose.production.yml up -d ollama
sleep 30

# Download essential models
MODELS=("llama3.2:latest" "mistral:latest" "codellama:latest")
for model in "${MODELS[@]}"; do
    log "📥 Downloading model: $model"
    docker-compose -f docker-compose.production.yml exec ollama ollama pull "$model" || warning "Failed to download $model"
done

# Start main application
log "🚀 Starting Open WebUI application..."
docker-compose -f docker-compose.production.yml up -d openwebui

# Wait for application to be ready
log "⏳ Waiting for application to be ready..."
for i in {1..60}; do
    if curl -f http://localhost:8080/health &>/dev/null; then
        success "Open WebUI is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        error "Open WebUI failed to start after 10 minutes"
    fi
    sleep 10
done

# Setup SSL certificates (Let's Encrypt)
if [ "$ENABLE_HTTPS" = "true" ] && [ -n "$DOMAIN" ]; then
    log "🔒 Setting up SSL certificates..."

    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        apt-get update && apt-get install -y certbot
    fi

    # Generate certificates
    certbot certonly --standalone --non-interactive --agree-tos --email "$EMAIL" -d "$DOMAIN"

    # Copy certificates to nginx directory
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/

    # Start nginx with SSL
    docker-compose -f docker-compose.production.yml --profile production up -d nginx
fi

# Start monitoring if enabled
if [ "$ENABLE_MONITORING" = "true" ]; then
    log "📊 Starting monitoring services..."
    docker-compose -f docker-compose.production.yml --profile monitoring up -d
fi

# Setup backup if enabled
if [ "$ENABLE_BACKUP" = "true" ]; then
    log "💾 Setting up backup services..."
    docker-compose -f docker-compose.production.yml --profile backup up -d
fi

# Final health check
log "🏥 Running final health checks..."
sleep 10

SERVICES=("db:5432" "redis:6379" "ollama:11434" "openwebui:8080")
for service in "${SERVICES[@]}"; do
    SERVICE_NAME=$(echo "$service" | cut -d: -f1)
    SERVICE_PORT=$(echo "$service" | cut -d: -f2)

    if nc -z localhost "$SERVICE_PORT" 2>/dev/null; then
        success "$SERVICE_NAME is healthy"
    else
        error "$SERVICE_NAME is not responding on port $SERVICE_PORT"
    fi
done

# Display deployment summary
echo
echo "🎉 Open WebUI Production Deployment Complete!"
echo "=================================================="
echo
echo "📊 Service Status:"
echo "  🌐 Open WebUI:    http://localhost:8080"
echo "  🗃️ PostgreSQL:    localhost:5432"
echo "  🔄 Redis:         localhost:6379"
echo "  🤖 Ollama:        localhost:11434"

if [ "$ENABLE_HTTPS" = "true" ] && [ -n "$DOMAIN" ]; then
    echo "  🔒 HTTPS URL:     https://$DOMAIN"
fi

if [ "$ENABLE_MONITORING" = "true" ]; then
    echo "  📈 Prometheus:    http://localhost:9090"
    echo "  📊 Grafana:       http://localhost:3001"
fi

echo
echo "🔐 Security Recommendations:"
echo "  ✅ Change default passwords"
echo "  ✅ Setup firewall rules"
echo "  ✅ Enable automatic updates"
echo "  ✅ Setup SSL/HTTPS"
echo "  ✅ Configure backup strategy"
echo
echo "📚 Next Steps:"
echo "  1. Access Open WebUI at http://localhost:8080"
echo "  2. Create your admin account"
echo "  3. Test AI model functionality"
echo "  4. Configure domain and SSL (if needed)"
echo "  5. Setup monitoring alerts"
echo
echo "📖 Logs location: ./logs/"
echo "💾 Backups location: ./backups/"
echo
success "Deployment completed successfully!"
