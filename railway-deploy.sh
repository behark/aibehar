#!/bin/bash
# Railway Deployment Script for Open WebUI

echo "🚀 Starting Open WebUI Railway Deployment..."

# Check if we're in Railway environment
if [ "$RAILWAY_ENVIRONMENT" = "production" ]; then
    echo "✅ Railway production environment detected"
    
    # Set production environment variables
    export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
    export WEBUI_SECRET_KEY="${WEBUI_SECRET_KEY:-$(openssl rand -base64 32)}"
    export CORS_ALLOW_ORIGIN="${CORS_ALLOW_ORIGIN:-*}"
    export DATA_DIR="${DATA_DIR:-/app/backend/data}"
    
    echo "🔧 Environment configured for Railway"
else
    echo "ℹ️  Local development environment"
fi

# Start the application
echo "🎯 Starting Open WebUI..."
exec python -m uvicorn open_webui.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
