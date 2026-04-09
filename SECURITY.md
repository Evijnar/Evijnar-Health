# Security Policy & Guidelines

## 🔐 Overview

Evijnar handles sensitive healthcare data and must maintain HIPAA compliance. This document outlines our security practices, policies, and guidelines for all contributors and maintainers.

---

## 🚨 Security Issues

### Reporting a Vulnerability

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead:
1. Email security concerns to the project maintainers privately
2. Include steps to reproduce (if possible)
3. Allow 72 hours for initial response
4. Follow responsible disclosure practices

We take all security reports seriously and will:
- Acknowledge receipt within 48 hours
- Provide a timeline for the fix
- Credit the reporter (if desired)

---

## 🔑 Secrets Management

### ❌ NEVER Commit

These files **MUST NEVER** be committed to the repository:

```
.env (actual values)
.env.production
.env.local
*.pem, *.key files
service-account-key.json
*-credentials.json
docker-compose.override.yml (if contains secrets)
config.yml (if contains secrets)
```

### ✅ DO Commit

- `.env.example` - Template with placeholder values only
- Public configuration (non-sensitive)
- Sanitized examples

### 🔒 Secure Storage

Use GitHub Organization Secrets for:

```
DATABASE_PASSWORD
DATABASE_URL (production)
SECRET_KEY
JWT_SECRET
ENCRYPTION_KEY_PATIENT_DATA
ENCRYPTION_KEY_PHARMA_DATA
ANTHROPIC_API_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
GOOGLE_MAPS_API_KEY
HIPAA_AUDIT_WEBHOOK_URL
```

**Setup Instructions:**

1. Go to Organization Settings → Secrets and variables → Actions
2. Create new repository secret
3. Name: `SECRET_NAME`
4. Value: `actual-secret-value`
5. Reference in workflows: `${{ secrets.SECRET_NAME }}`

---

## 🛡️ HIPAA Compliance

### Patient Data Protection

- ✅ All patient data is encrypted at rest using Fernet encryption
- ✅ All patient data is encrypted in transit (HTTPS/TLS)
- ✅ Database credentials are never hardcoded
- ✅ Audit logging is enabled for all PHI access
- ✅ Access controls are enforced at the API level

### Encryption Keys

- **Location**: `/apps/api/app/utils/encryption.py`
- **Algorithm**: Fernet (symmetric encryption)
- **Key Management**: 
  - Development: Placeholder keys (DO NOT use in production)
  - Production: Load from `ENCRYPTION_KEY_*` environment variables
  - Rotation: Plan for quarterly key rotation

### Audit Logging

- All PHI access is logged to `audit` table
- Audit logs include: user, action, timestamp, IP address
- Webhook: Configure `HIPAA_AUDIT_WEBHOOK_URL` for external audit trail
- Retention: Keep audit logs for minimum 6 years

---

## 🔐 Authentication & Authorization

### JWT Tokens

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 24 hours (configurable)
- **Refresh Token**: 7 days
- **Storage**: Secure HttpOnly cookies (frontend) or localStorage with CSRF token

### Required Headers

All API requests require:
```
Authorization: Bearer <jwt_token>
```

### Multi-Factor Authentication (MFA)

- **Status**: Implemented in `app/utils/mfa.py`
- **Methods**: TOTP (Time-based One-Time Password)
- **Flow**: 
  1. User authenticates with username/password
  2. System prompts for MFA code
  3. User provides code from authenticator app
  4. JWT is issued only after successful MFA

---

## 🔒 Database Security

### Connection String

```
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}
```

**Never hardcode** credentials. Always use environment variables.

### Migrations

- Alembic manages schema changes
- Review migrations before running:
  ```bash
  alembic heads
  alembic current
  alembic upgrade head
  ```

### SQL Injection Prevention

- ✅ All queries use parameterized statements (SQLAlchemy ORM)
- ✅ No string concatenation in queries
- ✅ Input validation on all API endpoints

---

## 🌐 API Security

### CORS Configuration

```python
# Allowed origins (configure per environment)
CORS_ORIGINS=http://localhost:3000,https://app.evijnar.com
```

**Production**: Only allow trusted domains

### Rate Limiting

- Implement rate limits on public endpoints
- Recommended: 100 requests/minute per IP
- Location: `apps/api/app/middleware.py`

### Input Validation

- All user input is validated using Pydantic
- File uploads are scanned for malware
- Maximum file size: 10MB

---

## 🐳 Docker Security

### Image Security

```dockerfile
# Use minimal base images
FROM python:3.11-slim

# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

### Secrets in Docker Compose

```yaml
# ✅ GOOD - Use environment variables
environment:
  - DATABASE_URL=${DATABASE_URL}
  - SECRET_KEY=${SECRET_KEY}

# ❌ BAD - Never hardcode
environment:
  - DATABASE_URL=postgresql://user:password@host/db
```

### Docker Secrets (Production)

```yaml
secrets:
  db_password:
    external: true
services:
  api:
    secrets:
      - db_password
```

---

## 📋 Pre-commit Hooks

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Configuration (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

---

## 🔍 Code Review Checklist

Before approving PRs, verify:

- [ ] No secrets committed (check `.env*` files)
- [ ] All user input is validated
- [ ] SQL queries use parameterized statements
- [ ] Error messages don't leak sensitive info
- [ ] API endpoints have proper auth checks
- [ ] Database credentials are externalized
- [ ] No hardcoded API keys
- [ ] HTTPS is enforced (production)
- [ ] CORS is properly configured
- [ ] Audit logging is present for sensitive operations

---

## 🚀 Deployment Security

### Environment-Specific Configuration

```
Development:  .env (with placeholder values)
Staging:      GitHub Secrets (staging-*)
Production:   GitHub Secrets (prod-*)
```

### Production Deployment Checklist

- [ ] DEBUG=false
- [ ] All secrets loaded from environment variables
- [ ] HTTPS enforced
- [ ] CORS origins restricted
- [ ] Rate limiting enabled
- [ ] Audit logging enabled
- [ ] Database backups configured
- [ ] Monitoring/alerting enabled

### Secrets Rotation

- **Frequency**: Quarterly (minimum)
- **Process**:
  1. Generate new secret
  2. Update GitHub Secrets
  3. Redeploy services
  4. Monitor for issues
  5. Retire old secret

---

## 📊 Security Testing

### Dependency Scanning

```bash
# Check for vulnerable dependencies
pip audit
npm audit
```

### Static Analysis

```bash
# Python security linting
bandit -r apps/api/

# TypeScript linting
eslint apps/web/src/
```

### Dynamic Testing

```bash
# Run integration tests
pytest apps/api/tests/

# Check HIPAA compliance
pytest apps/api/tests/test_integration_phase3.py
```

---

## 🔄 Incident Response

### If a Secret is Leaked

1. **Immediately revoke** the compromised secret
2. **Rotate** all related secrets
3. **Audit logs** for any unauthorized access
4. **Report** to security team
5. **Document** the incident
6. **Prevent recurrence** with better tooling

### On Successful Attack

1. **Isolate** affected systems
2. **Assess** damage
3. **Patch** vulnerabilities
4. **Notify** affected users (if required by law)
5. **Conduct** post-mortem

---

## 📚 Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## 👥 Security Team

**Primary Contact**: [Add team member email]
**On-Call Security**: [Add on-call rotation]

---

## ✅ Acknowledgments

Thank you to all security researchers who responsibly report vulnerabilities.

Last Updated: 2026-04-09
