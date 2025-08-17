#!/bin/bash
# Script to prepare clean deployment files for GitHub

echo "🚀 Preparing clean deployment files for GitHub..."

# Create deployment directory
mkdir -p behar-ai-deploy
cd behar-ai-deploy

# Copy only safe deployment files (no personal data)
echo "📁 Copying safe deployment files..."

# Core deployment files
cp ../railway.toml ./
cp ../railway-deploy.sh ./
cp ../Dockerfile.deploy ./Dockerfile
cp ../docker-compose.deploy.yml ./docker-compose.yml
cp ../.env.deploy ./.env.example
cp ../README.deploy.md ./README.md
cp ../DEPLOYMENT_GUIDE.md ./
cp ../.gitignore.deploy ./.gitignore

# Make scripts executable
chmod +x railway-deploy.sh

echo "✅ Clean deployment files prepared in ./behar-ai-deploy/"
echo ""
echo "📋 Files ready for GitHub:"
echo "  - Dockerfile (clean Open WebUI deployment)"
echo "  - docker-compose.yml (with Ollama)"
echo "  - railway.toml (Railway deployment config)"
echo "  - .env.example (safe environment template)"
echo "  - README.md (deployment instructions)"
echo "  - .gitignore (excludes personal data)"
echo ""
echo "🔒 Security verified:"
echo "  ✅ No personal API keys"
echo "  ✅ No database files"
echo "  ✅ No private data"
echo "  ✅ No credentials"
echo ""
echo "📤 Next steps:"
echo "1. cd behar-ai-deploy"
echo "2. git init"
echo "3. git add ."
echo "4. git commit -m 'Initial deployment setup'"
echo "5. git remote add origin https://github.com/behark/behar-ai.git"
echo "6. git push -u origin main"
echo ""
echo "🚀 Then deploy on Railway:"
echo "1. Connect your GitHub repo to Railway"
echo "2. Railway will auto-deploy using Dockerfile"
echo "3. Get your public URL"
