# How to Store .env Files Securely

## 🎯 Summary Table

| Method | Dev | Staging | Production | HIPAA Safe | Complexity |
|--------|-----|---------|------------|-----------|-----------|
| **GitHub Secrets** | ❌ | ✅ | ✅ | ✅ | Low |
| **Local .env** | ✅ | ❌ | ❌ | ✓ | Very Low |
| **AWS Secrets Manager** | ❌ | ✅ | ✅ | ✅ | High |
| **HashiCorp Vault** | ✅ | ✅ | ✅ | ✅ | High |
| **Encrypted .env file** | ⚠️ | ⚠️ | ⚠️ | Partial | Medium |
| **Environment Variables** | ✅ | ✅ | ✅ | ✅ | Low |

---

## ✅ RECOMMENDED APPROACH (For Your Project)

### **Tier 1: Local Development**

**Store .env locally (never committed):**

```bash
# Developer machine
apps/api/.env              ← Your machine only
apps/web/.env.local        ← Your machine only
packages/database/.env     ← Your machine only
```

**How to create:**
```bash
./setup.sh                 # Generates .env files automatically
# OR
cp apps/api/.env.example apps/api/.env
nano apps/api/.env         # Edit with your dev values
```

**Contents for local dev:**
```env
DATABASE_URL=postgresql://evijnar_dev:your_password@localhost:5432/evijnar_dev
SECRET_KEY=dev-key-any-value-works
JWT_SECRET=dev-jwt-key-any-value-works
ENCRYPTION_KEY_PATIENT_DATA=your-fernet-key-here
# (Use placeholder values for local development)
```

**Protection:**
- ✅ In `.gitignore` - never committed
- ✅ Only on your machine
- ✅ Pre-commit hooks prevent accidental commits

---

### **Tier 2: Staging/Production - GitHub Organization Secrets**

**Store in GitHub (encrypted by GitHub):**

```
GitHub Organization Settings
  → Secrets and variables
  → Actions
```

**Steps:**

1. **Go to Organization Settings**
   ```
   github.com/Evijnar/settings/secrets/actions
   ```

2. **Create Each Secret:**
   ```
   Name: DB_PASSWORD
   Value: your_actual_production_password
   Repositories: Evijnar-Health
   ```

3. **Reference in Workflows:**
   ```yaml
   # .github/workflows/deploy.yml
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Deploy
           env:
             DATABASE_URL: ${{ secrets.DATABASE_URL }}
             SECRET_KEY: ${{ secrets.SECRET_KEY }}
           run: |
             # Your deploy script
   ```

**What GitHub Secrets Provides:**
- ✅ Encrypted at rest (AES-256)
- ✅ Encrypted in transit (HTTPS/TLS)
- ✅ Access logs/audit trail
- ✅ Per-repository or org-wide
- ✅ Automatic masking in logs
- ✅ HIPAA compliant storage

---

## 📋 Complete Strategy (Recommended)

### **Development (Local Machine)**

```
✅ Store .env locally
✅ Never commit to git
✅ Use placeholder values that don't matter
✅ Regenerate encryption keys using setup.sh
```

**Example workflow:**
```bash
git clone https://github.com/Evijnar/Evijnar-Health.git
cd Evijnar-Health
./setup.sh                              # Auto-creates .env files
# Edit values for your local environment
nano apps/api/.env
# Start developing
docker-compose up -d
npm run dev
```

### **CI/CD Pipeline (GitHub Actions)**

```
✅ Store secrets in GitHub Organization Settings
✅ Reference with ${{ secrets.NAME }}
✅ Automatically masked in logs
✅ Full audit trail of access
```

**Example workflow file:**
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Test with secrets
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
          ENCRYPTION_KEY_PATIENT_DATA: ${{ secrets.ENCRYPTION_KEY_PATIENT_DATA }}
          ENCRYPTION_KEY_PHARMA_DATA: ${{ secrets.ENCRYPTION_KEY_PHARMA_DATA }}
        run: |
          cd apps/api
          pytest tests/
      
      - name: Build and Push Docker Image
        env:
          DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
        run: |
          docker build -t myregistry/evijnar-api:latest apps/api/
          docker push myregistry/evijnar-api:latest
      
      - name: Deploy to Production
        env:
          PROD_DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          ./scripts/deploy.sh
```

### **Production Server**

```
✅ Environment variables set by container orchestration
✅ Never stored in .env files on server
✅ Set via:
   - Docker environment variables
   - Kubernetes secrets
   - ECS task definitions
   - systemd environment files
```

**Examples:**

**Docker:**
```bash
docker run -e DATABASE_URL=$DATABASE_URL \
           -e SECRET_KEY=$SECRET_KEY \
           myimage:latest
```

**Docker Compose (production):**
```yaml
services:
  api:
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET: ${JWT_SECRET}
    # Never hardcode secrets!
```

**Kubernetes:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: evijnar-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@host/db
  SECRET_KEY: your-secret-key
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: evijnar-api
spec:
  template:
    spec:
      containers:
      - name: api
        envFrom:
        - secretRef:
            name: evijnar-secrets
```

---

## 🔒 Complete Local Setup Guide

### **Step 1: Clone Repository**
```bash
git clone https://github.com/Evijnar/Evijnar-Health.git
cd Evijnar-Health
```

### **Step 2: Run Automated Setup**
```bash
./setup.sh

# This will:
# ✅ Create .env files from .env.example
# ✅ Generate encryption keys
# ✅ Install dependencies
# ✅ Start Docker containers
# ✅ Run database migrations
```

### **Step 3: Verify .env Files Created**
```bash
ls -la apps/api/.env          # Should exist
cat apps/api/.env             # Review values
```

### **Step 4: Update with Your Values**
```bash
nano apps/api/.env

# Add your local values:
DATABASE_URL=postgresql://evijnar_dev:your_dev_password@localhost:5432/evijnar_dev
```

### **Step 5: Verify Not Committed**
```bash
git status | grep "\.env"    # Should show nothing
git ls-files | grep "\.env$" # Should show nothing
```

---

## 🚀 GitHub Secrets Setup (For Deployment)

### **Required 11 Secrets:**

Go to: `github.com/Evijnar/settings/secrets/actions`

```
1. DB_PASSWORD              → postgresql password
2. DATABASE_URL             → postgresql://user:PASSWORD@host:5432/db
3. SECRET_KEY               → Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
4. JWT_SECRET               → Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
5. ENCRYPTION_KEY_PATIENT_DATA    → Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
6. ENCRYPTION_KEY_PHARMA_DATA     → Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
7. ANTHROPIC_API_KEY        → sk-ant-...
8. TWILIO_ACCOUNT_SID       → AC...
9. TWILIO_AUTH_TOKEN        → your-token
10. GOOGLE_MAPS_API_KEY     → AIzaSy...
11. HIPAA_AUDIT_WEBHOOK_URL → https://...
```

---

## 🛡️ Security Checklist

### **Local Development**
- [ ] .env files created from .env.example
- [ ] .env files in .gitignore
- [ ] Pre-commit hooks installed
- [ ] No .env files committed
- [ ] Placeholder values used (no real credentials)

### **GitHub Repository**
- [ ] 11 secrets added to Organization Settings
- [ ] Only .env.example files committed (no actual values)
- [ ] .gitignore properly configured
- [ ] Pre-commit hooks deployed
- [ ] Branch protection enabled

### **Deployment**
- [ ] Secrets loaded from environment
- [ ] No .env files in Docker images
- [ ] No secrets in docker-compose (uses ${VAR})
- [ ] Audit logging enabled
- [ ] Key rotation scheduled

---

## ⚠️ Common Mistakes (AVOID!)

### ❌ WRONG:
```dockerfile
# Never do this!
ENV SECRET_KEY=my-secret-key
ENV DATABASE_PASSWORD=password123
```

### ✅ RIGHT:
```dockerfile
# Use build args or pass at runtime
ARG SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

# Or pass at runtime:
docker run -e SECRET_KEY=$SECRET_KEY myimage
```

### ❌ WRONG:
```yaml
# Never do this in docker-compose!
environment:
  DATABASE_URL: postgresql://user:password@host/db
```

### ✅ RIGHT:
```yaml
# Always use variables
environment:
  DATABASE_URL: ${DATABASE_URL}
```

---

## 🔄 Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│ Developer Clones Repository                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Runs: ./setup.sh                                            │
│ • Creates .env files from templates                         │
│ • Generates encryption keys                                 │
│ • Installs pre-commit hooks                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Developer Edits .env with Local/Dev Values                  │
│ (.env stays on machine, never committed)                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Developer Makes Changes & Commits                           │
│ Pre-commit hooks verify no secrets are committed            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Push to GitHub                                              │
│ • Public files pushed                                       │
│ • .env files NOT pushed (in .gitignore)                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions CI/CD Pipeline                               │
│ • Loads secrets from Organization Settings                  │
│ • Runs tests with actual credentials                        │
│ • Builds Docker images                                      │
│ • Deploys to production                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Production Server                                           │
│ • Secrets injected at runtime                               │
│ • No .env files stored on server                            │
│ • Environment variables only                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📞 Quick Reference

**For local development:**
```bash
./setup.sh              # One command setup
```

**For GitHub Actions:**
```yaml
env:
  SECRET_NAME: ${{ secrets.SECRET_NAME }}
```

**For Docker:**
```bash
docker run -e SECRET_NAME=$SECRET_NAME myimage
```

**For Kubernetes:**
```yaml
envFrom:
  - secretRef:
      name: evijnar-secrets
```

---

## ✅ Summary

| Environment | Where to Store | How |
|-------------|----------------|-----|
| **Development** | Local machine | .env file (never commit) |
| **GitHub CI/CD** | GitHub Secrets | Organization Settings |
| **Production** | Environment vars | Docker/K8s injected at runtime |

**Never commit .env files. Ever.** ✅

This way you get:
- ✅ Security (no credentials in git)
- ✅ Flexibility (different values per environment)
- ✅ Audit trail (GitHub logs who accessed secrets)
- ✅ Easy rotation (update GitHub Secrets, redeploy)
- ✅ HIPAA compliant (no PHI in version control)

---

**Your current setup is already configured for this!** 🎉

Last Updated: April 9, 2026
