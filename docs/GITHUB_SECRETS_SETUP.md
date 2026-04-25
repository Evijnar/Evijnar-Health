# GitHub Organization Secrets Setup Guide

This guide explains how to configure secrets for the Evijnar project in GitHub Organization Settings.

---

## 📋 Required Secrets

These secrets must be configured in your GitHub Organization for CI/CD pipelines to work properly.

### Step 1: Access Organization Secrets

1. Navigate to your GitHub Organization
2. Go to **Settings** (organization-level, not repository)
3. Select **Secrets and variables** → **Actions**

### Step 2: Create Each Secret

For each secret below, click **New organization secret** and fill in:

```
Name: [SECRET_NAME]
Value: [actual-secret-value]
Repositories: Select "Evijnar" (or all repositories)
```

---

## 🔑 Environment Variables to Add

### Database Configuration

#### `DB_PASSWORD`
```
Value: Your production PostgreSQL password
Example: super_secure_db_password_123
```

#### `DATABASE_URL`
```
Value: Full PostgreSQL connection string
Example: postgresql://evijnar_prod:PASSWORD@prod-db.example.com:5432/evijnar_prod
```

### Security Keys

#### `SECRET_KEY`
```
Value: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
Example: kB5x8jN3mP2qR7sT9uV1wX4yZ6aB8cD_E
```

#### `JWT_SECRET`
```
Value: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
Example: xK9p2mL5nQ3rS6tU8vW1yX4zB7cD0eF_H
```

### Patient Data Encryption

#### `ENCRYPTION_KEY_PATIENT_DATA`
```
Value: Generate with:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
Example: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop1Q=
```

#### `ENCRYPTION_KEY_PHARMA_DATA`
```
Value: Generate with:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
Example: XYZabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLM2R=
```

### External APIs

#### `EVIJNAR_AI_KB_URL`
```
Value: Optional JSON knowledge base endpoint for Evijnar Health AI
Example: https://example.com/evijnar-ai-kb.json
```

#### `TWILIO_ACCOUNT_SID`
```
Value: Your Twilio Account SID
Example: ACaa1234567890bbb1234567890ccccdd
```

#### `TWILIO_AUTH_TOKEN`
```
Value: Your Twilio Auth Token
Example: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

#### `GOOGLE_MAPS_API_KEY`
```
Value: Your Google Maps API key
Example: AIzaSyDmyQP7_A8Z7k9L-m0nOpQrStUvWxYzAbCdEfG
```

### HIPAA Compliance

#### `HIPAA_AUDIT_WEBHOOK_URL`
```
Value: External audit logging webhook endpoint
Example: https://audit.complianceprovider.com/webhook/evijnar
```

---

## 🔄 Environment-Specific Secrets

For different environments, create secrets with prefixes:

### Development Environment
```
DEV_DATABASE_URL
DEV_SECRET_KEY
DEV_JWT_SECRET
DEV_EVIJNAR_AI_KB_URL
```

### Staging Environment
```
STAGING_DATABASE_URL
STAGING_SECRET_KEY
STAGING_JWT_SECRET
STAGING_EVIJNAR_AI_KB_URL
```

### Production Environment
```
PROD_DATABASE_URL
PROD_SECRET_KEY
PROD_JWT_SECRET
PROD_EVIJNAR_AI_KB_URL
PROD_ENCRYPTION_KEY_PATIENT_DATA
PROD_ENCRYPTION_KEY_PHARMA_DATA
```

---

## 🔗 Using Secrets in GitHub Actions

### In Workflow Files

```yaml
name: Build and Deploy

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run API Tests
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
          EVIJNAR_AI_KB_URL: ${{ secrets.EVIJNAR_AI_KB_URL }}
        run: |
          cd apps/api
          pip install -r requirements.txt
          pytest tests/
      
      - name: Deploy to Production
        env:
          PROD_DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
          PROD_SECRET_KEY: ${{ secrets.PROD_SECRET_KEY }}
        run: |
          # Your deploy script here
          ./scripts/deploy.sh
```

### Example: .github/workflows/deploy.yml

```yaml
name: Deploy Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker Image
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
        run: |
          docker build -t evijnar-api:latest apps/api/
      
      - name: Push to Registry
        run: |
          docker push evijnar-api:latest
      
      - name: Deploy
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
          PROD_DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
        run: |
          echo "${{ secrets.DEPLOY_KEY }}" > /tmp/deploy_key
          chmod 600 /tmp/deploy_key
          ssh -i /tmp/deploy_key deploy@prod.example.com './deploy.sh'
```

---

## ✅ Verification Checklist

After setting up secrets:

- [ ] All 10+ required secrets are in Organization Settings
- [ ] No secrets are hardcoded in `.env` files committed to repo
- [ ] GitHub Actions workflows reference secrets correctly
- [ ] Local `.env` files use `.env.example` as template
- [ ] CI/CD pipeline builds and deploys successfully
- [ ] No "Secret value is undefined" errors in logs

---

## 🔒 Security Best Practices

1. **Rotate Secrets Quarterly**
   - Update each secret value in Organization Settings
   - Redeploy services after rotation
   - Keep audit trail of rotations

2. **Limit Secret Access**
   - Only assign to required repositories
   - Use branch protection rules
   - Require reviews before merge

3. **Audit Secret Usage**
   - Review GitHub Actions logs regularly
   - Check who accessed secrets
   - Monitor for unauthorized deployments

4. **Never Log Secrets**
   - Configure GitHub Actions to mask secrets in logs
   - Don't echo or print secret values
   - Use `::add-mask::` for custom secret masking

---

## 🐛 Troubleshooting

### Secret Not Found in Workflow

```
❌ Error: The secret `MY_SECRET` was not found
```

**Solution:**
- Verify secret name matches exactly (case-sensitive)
- Ensure secret is assigned to the repository
- Use `${{ secrets.SECRET_NAME }}` syntax

### Workflow Fails with Missing Env Var

```
❌ Error: DATABASE_URL environment variable is undefined
```

**Solution:**
- Add secret to organization settings
- Reference in workflow: `env: DATABASE_URL: ${{ secrets.DATABASE_URL }}`
- Re-run workflow after creating secret

### Secret Leaked in Logs

```
❌ Secret value visible in GitHub Action logs
```

**Solution:**
- GitHub automatically masks known secrets
- Use `::add-mask::` for custom masking:
  ```yaml
  - run: echo "::add-mask::${{ secrets.MY_SECRET }}"
  ```

---

## 📞 Support

For questions or issues with GitHub secrets:
1. Check [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
2. Review GitHub Actions logs for error messages
3. Contact organization administrator

---

## 📅 Maintenance Schedule

- **Weekly**: Monitor GitHub Actions for failures
- **Monthly**: Review secret access logs
- **Quarterly**: Rotate all secrets
- **Annually**: Audit entire secrets infrastructure

Last Updated: 2026-04-09
