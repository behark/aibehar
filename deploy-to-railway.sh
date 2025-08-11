#!/bin/bash

# AI Behar Platform - Railway Deployment Script
# This script automates the Railway deployment process

set -e

echo "🚀 AI Behar Platform - Railway Deployment"
echo "=========================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "🔐 Please complete Railway authentication..."
echo "This will open your browser to login to Railway"
railway login

echo "📋 Creating Railway project..."
railway init

echo "🗃️ Adding PostgreSQL database..."
railway add --database postgresql

echo "🔄 Adding Redis cache..."
railway add --database redis

echo "⚙️ Setting up environment variables..."
railway variables set WEBUI_SECRET_KEY="behar-ai-platform-super-secure-secret-key-2025-production"
railway variables set CORS_ALLOW_ORIGIN="*"
railway variables set DATA_DIR="/app/backend/data"
railway variables set ENABLE_SIGNUP="true"
railway variables set ENABLE_LOGIN_FORM="true"
railway variables set ENABLE_WEB_SEARCH="true"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"

echo "🚀 Deploying to Railway..."
railway up

echo "🌐 Getting your Railway URL..."
RAILWAY_URL=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4)

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "🌐 Your AI Behar Platform URL: $RAILWAY_URL"
echo "📊 Railway Dashboard: https://railway.app/dashboard"
echo ""
echo "📝 Next Steps:"
echo "1. Visit your Railway URL above"
echo "2. Create your admin account"
echo "3. Test the AI models"
echo "4. Configure your custom domain (optional)"
echo ""
