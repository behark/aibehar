# Open WebUI - Comprehensive Installation Guide

This guide provides detailed instructions for installing and configuring Open WebUI in various environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Advanced Docker Configuration](#advanced-docker-configuration)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Manual Installation](#manual-installation)
- [Configuration Options](#configuration-options)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing Open WebUI, ensure you have:

- **Hardware Requirements**:
  - Minimum: 4GB RAM, 2 CPU cores
  - Recommended: 8GB+ RAM, 4+ CPU cores
  - Storage: 10GB+ free space

- **Software Requirements**:
  - Docker and Docker Compose (for container-based installation)
  - Kubernetes (for Kubernetes-based installation)
  - Python 3.11+ (for manual installation)
  - Node.js 18+ (for manual installation)

- **Network Requirements**:
  - Open ports for web access (default: 3000)
  - Internet access for pulling containers and packages

## Quick Start with Docker

### 1. Install Docker and Docker Compose

**For Ubuntu/Debian**:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install -y docker-compose-plugin
```

**For macOS**:
- Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)

**For Windows**:
- Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
- Ensure WSL2 is installed and configured

### 2. Pull and Run Open WebUI

```bash
# Create a directory for Open WebUI
mkdir open-webui && cd open-webui

# Download the docker-compose.yaml
curl -O https://raw.githubusercontent.com/open-webui/open-webui/main/docker-compose.yaml

# Create an environment file
curl -O https://raw.githubusercontent.com/open-webui/open-webui/main/.env.example
mv .env.example .env

# Edit the environment file with your settings
# Generate a strong secret key:
# openssl rand -hex 32
nano .env

# Start Open WebUI
docker-compose up -d
```

### 3. Access Open WebUI

Open your browser and navigate to:
- http://localhost:3000

Default credentials:
- Username: admin
- Password: admin

**IMPORTANT**: Change the default admin password immediately after first login.

## Advanced Docker Configuration

### Using GPU Support

For NVIDIA GPU support:

1. Install NVIDIA Container Toolkit:
```bash
# Add the NVIDIA repository
curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update

# Install nvidia-container-runtime
sudo apt-get install -y nvidia-container-runtime
```

2. Use the GPU-enabled Docker Compose file:
```bash
curl -O https://raw.githubusercontent.com/open-webui/open-webui/main/docker-compose.gpu.yaml
docker-compose -f docker-compose.gpu.yaml up -d
```

### Custom Network Configuration

To use a custom network configuration:

```bash
# Create a custom Docker network
docker network create openwebui-network

# Update your docker-compose file with network settings
docker-compose -f docker-compose.yaml --network openwebui-network up -d
```

### Persistent Storage

Open WebUI uses Docker volumes for persistence. You can customize the volume locations:

```yaml
services:
  open-webui:
    volumes:
      - /path/on/host/webui-data:/app/backend/data
  
  ollama:
    volumes:
      - /path/on/host/ollama-data:/root/.ollama
```

## Kubernetes Deployment

### Deployment with Helm

1. Add the Open WebUI Helm repository:
```bash
helm repo add open-webui https://open-webui.github.io/helm-charts
helm repo update
```

2. Install the chart:
```bash
# Create a namespace
kubectl create namespace open-webui

# For CPU-only deployment
helm install open-webui open-webui/open-webui -n open-webui

# For GPU-enabled deployment
helm install open-webui open-webui/open-webui -n open-webui --set gpu.enabled=true
```

### Deployment with Kustomize

1. Clone the repository:
```bash
git clone https://github.com/open-webui/open-webui.git
cd open-webui
```

2. Apply the manifests:
```bash
# For CPU-only deployment
kubectl apply -f ./kubernetes/manifest/base

# For GPU-enabled deployment
kubectl apply -k ./kubernetes/manifest
```

## Manual Installation

### Backend Installation

1. Clone the repository:
```bash
git clone https://github.com/open-webui/open-webui.git
cd open-webui
```

2. Set up a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run the backend:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Frontend Installation

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Build the frontend:
```bash
npm run build
```

3. For development mode:
```bash
npm run dev
```

## Configuration Options

Open WebUI can be configured through environment variables:

### Core Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `OPEN_WEBUI_PORT` | Port for the web interface | `3000` |
| `OLLAMA_BASE_URL` | URL for the Ollama API | `http://ollama:11434` |
| `WEBUI_SECRET_KEY` | Secret key for encryption | Required |

### API Integration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `""` |
| `OPENAI_API_BASE_URL` | Custom OpenAI API endpoint | `""` |

### Security Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ALLOW_ORIGIN` | CORS allowed origins | `*` |
| `FORWARDED_ALLOW_IPS` | IPs allowed in forwarded headers | `*` |
| `AIOHTTP_CLIENT_TIMEOUT` | API timeout in seconds | `300` |

For a complete list of configuration options, see the [Configuration Documentation](https://docs.openwebui.com/configuration).

## Security Considerations

Before deploying in production, consider these security measures:

1. **Generate Strong Secrets**:
   ```bash
   # Generate a strong secret key
   openssl rand -hex 32
   ```

2. **Restrict CORS Settings**:
   Update `.env` to restrict CORS to your domain:
   ```
   CORS_ALLOW_ORIGIN='https://your-domain.com'
   ```

3. **Set Up HTTPS**:
   Configure a reverse proxy (Nginx, Traefik) with SSL certificates.
   
4. **User Authentication**:
   Change the default admin password immediately.
   
5. **Firewall Rules**:
   Restrict access to only necessary ports.

For complete security guidance, see [Security Documentation](https://docs.openwebui.com/security).

## Troubleshooting

### Common Issues and Solutions

#### Docker Connection Issues

**Problem**: Unable to connect to Ollama from Open WebUI.
**Solution**: Check that the `OLLAMA_BASE_URL` is correctly set in your `.env` file.

```bash
# Verify Ollama is running
docker ps | grep ollama

# Check Ollama logs
docker logs ollama

# Test Ollama API directly
curl http://localhost:11434/api/tags
```

#### Permission Issues

**Problem**: Permission denied errors in container logs.
**Solution**: Check volume permissions:

```bash
# Fix permissions
sudo chown -R 1000:1000 /path/to/your/volume
```

#### Memory Issues

**Problem**: Container crashes with OOM (Out of Memory) errors.
**Solution**: Increase Docker memory limits:

```bash
# Edit Docker daemon.json
nano /etc/docker/daemon.json

# Add or modify the following
{
  "default-shm-size": "1G"
}

# Restart Docker
sudo systemctl restart docker
```

For more troubleshooting help, see our [Troubleshooting Guide](https://docs.openwebui.com/troubleshooting) or join our [Discord community](https://discord.gg/5rJgQTnV4s).
