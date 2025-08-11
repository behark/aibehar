# Open WebUI - Production Deployment Guide

## 🚀 Quick Start

Your Open WebUI project is now production-ready! Here's how to deploy:

### Option 1: Automated Production Deployment (Recommended)
```bash
# Make deployment script executable
chmod +x scripts/deploy-production.sh

# Run production deployment
./scripts/deploy-production.sh
```

### Option 2: Manual Docker Compose Deployment
```bash
# Copy environment configuration
cp .env.production .env

# Edit .env with your secure passwords and settings
nano .env

# Start production services
docker-compose -f docker-compose.production.yml up -d

# Optional: Start with monitoring
docker-compose -f docker-compose.production.yml --profile monitoring up -d
```

## 📋 Pre-Deployment Checklist

- [ ] **Environment Variables**: Edit `.env` with secure passwords
- [ ] **Domain Configuration**: Set your domain in environment variables
- [ ] **SSL Certificates**: Configure SSL for production (automated with Let's Encrypt)
- [ ] **Firewall Rules**: Configure firewall to allow necessary ports
- [ ] **Backup Strategy**: Enable automated backups
- [ ] **Monitoring**: Enable Prometheus & Grafana monitoring

## 🔧 Configuration Files Created

### Core Files
- `docker-compose.production.yml` - Production Docker Compose with all services
- `.env.production` - Production environment template
- `nginx/nginx.conf` - Production Nginx configuration with SSL

### Scripts
- `scripts/deploy-production.sh` - Automated deployment script
- `scripts/backup.sh` - Automated backup script

### Monitoring
- `monitoring/prometheus.yml` - Prometheus monitoring configuration

## 🌐 Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Open WebUI | 8080 | Main application |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Caching |
| Ollama | 11434 | AI Models |
| Nginx | 80/443 | Reverse proxy with SSL |
| Prometheus | 9090 | Monitoring |
| Grafana | 3001 | Dashboards |

## 🔐 Security Features

✅ **Implemented Security Measures:**
- Secure environment variable management
- Rate limiting and DDoS protection
- SSL/HTTPS with automatic certificate generation
- Security headers (HSTS, XSS protection, etc.)
- Database connection security
- Container isolation and resource limits
- Automated backup encryption

## 📊 Monitoring & Health Checks

- **Health Checks**: All services have automated health monitoring
- **Prometheus Metrics**: System and application metrics collection
- **Grafana Dashboards**: Visual monitoring interface
- **Log Aggregation**: Centralized logging in `./logs/`

## 💾 Backup Strategy

- **Automated Backups**: Daily PostgreSQL, Redis, and file system backups
- **Retention Policy**: Configurable backup retention (default 30 days)
- **Backup Location**: `./backups/` directory
- **Backup Types**: Database dumps, Redis snapshots, application data

## 🚀 Deployment Options

### Cloud Platforms
1. **AWS EC2/ECS** - Use provided Docker Compose
2. **Google Cloud Run** - Container-ready configuration
3. **Azure Container Instances** - Direct deployment
4. **DigitalOcean Droplets** - VPS deployment
5. **Railway** - Git-based deployment (existing config)

### On-Premises
1. **VPS Deployment** - Complete with Nginx reverse proxy
2. **Kubernetes** - Container orchestration ready
3. **Local Network** - Internal company deployment

## 📈 Performance Optimizations

- **Resource Limits**: Optimized container resource allocation
- **Connection Pooling**: Database connection optimization
- **Caching**: Redis caching for improved performance
- **Gzip Compression**: Nginx compression for faster loading
- **Static File Caching**: Optimized static asset delivery

## 🔧 Environment Variables Reference

### Required Variables
```bash
WEBUI_SECRET_KEY=your-32-char-secret-key
POSTGRES_PASSWORD=your-secure-database-password
POSTGRES_USER=openwebui_user
POSTGRES_DB=openwebui_prod
```

### Optional Variables
```bash
DOMAIN=your-domain.com
EMAIL=your-email@domain.com
ENABLE_HTTPS=true
ENABLE_MONITORING=true
ENABLE_BACKUP=true
```

## 🆘 Troubleshooting

### Common Issues
1. **Port Conflicts**: Check if ports 8080, 5432, 6379, 11434 are available
2. **Memory Issues**: Ensure at least 4GB RAM available
3. **Disk Space**: Require minimum 10GB free space
4. **SSL Issues**: Check domain DNS configuration

### Logs Location
- Application logs: `./logs/`
- Nginx logs: `./logs/nginx/`
- Container logs: `docker-compose logs [service_name]`

## 📞 Support

For issues or questions:
1. Check logs in `./logs/` directory
2. Run health checks: `docker-compose ps`
3. Review deployment logs
4. Check Open WebUI documentation

---

🎉 **Your Open WebUI platform is now production-ready!**
