# Secrets Management for Open WebUI

This document provides best practices for managing secrets and sensitive information in Open WebUI deployments.

## Environment Variables

The Open WebUI project uses environment variables for configuration, including sensitive information like API keys and database credentials.

### Security Best Practices

1. **Never commit secrets to version control**
   - Use `.env.example` as a template, but never commit actual `.env` files with real credentials
   - The `.gitignore` file should include `.env` and other secret files

2. **Secret Generation**
   - Generate strong random secrets for production:
   ```bash
   # Generate a strong JWT secret
   openssl rand -hex 32
   
   # Generate a strong session secret
   openssl rand -hex 24
   ```

3. **Secret Rotation**
   - Regularly rotate sensitive secrets (JWT_SECRET, SESSION_SECRET) in production
   - Plan for key rotation without service disruption

4. **Access Control**
   - Limit access to production environment variables to essential personnel only
   - Use a secrets management tool for teams (see below)

## Deployment Methods

### Docker Deployment

When using Docker, set environment variables in one of the following ways:

1. **Docker Compose (recommended for production)**
   ```yaml
   services:
     open-webui:
       environment:
         - JWT_SECRET=your_secret_here
         - OPENAI_API_KEY=your_api_key_here
   ```

2. **Docker Run Command**
   ```bash
   docker run -d \
     -e JWT_SECRET=your_secret_here \
     -e OPENAI_API_KEY=your_api_key_here \
     ghcr.io/open-webui/open-webui:main
   ```

3. **Docker Environment File**
   ```bash
   docker run -d --env-file .env ghcr.io/open-webui/open-webui:main
   ```

### Kubernetes Deployment

For Kubernetes deployments, use one of these methods:

1. **Kubernetes Secrets**
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: open-webui-secrets
   type: Opaque
   data:
     jwt-secret: <base64-encoded-secret>
     openai-api-key: <base64-encoded-key>
   ```

2. **Secret Management Tools Integration**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager

## Recommended Secret Management Tools

For team environments, consider these secret management solutions:

1. **HashiCorp Vault** - Comprehensive secret management with rotation, encryption, and access control
2. **AWS Secrets Manager** - Integrated with AWS services, automatic rotation
3. **Azure Key Vault** - For Azure-based deployments
4. **Google Secret Manager** - For GCP-based deployments
5. **Bitwarden** - Self-hosted option for smaller teams

## Production Security Checklist

Before deploying to production, verify:

- [ ] JWT_SECRET and SESSION_SECRET are strong, random values
- [ ] Database credentials use strong, unique passwords
- [ ] API keys have appropriate permissions (read-only where possible)
- [ ] CORS_ORIGIN is set to specific allowed origins, not wildcard
- [ ] SSL/TLS is properly configured
- [ ] Rate limiting is enabled
- [ ] Monitoring for unusual authentication attempts is in place

## Secret Detection

Consider implementing automated secret detection in your CI/CD pipeline:

1. Use tools like `git-secrets` or `trufflehog` to prevent committing secrets
2. Run regular audits of your codebase and configuration files

## Incident Response

If secrets are accidentally exposed:

1. Immediately rotate all affected credentials
2. Assess impact and potential data exposure
3. Document the incident and implement preventive measures
