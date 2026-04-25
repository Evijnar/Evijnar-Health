# GitHub Organization Secrets - Setup Checklist

## 🔑 Quick Setup Guide

**Go to**: `github.com/Evijnar/settings/secrets/actions`

Click **"New organization secret"** 11 times and add:

### Checklist - Copy & Paste Names

```
☐ DB_PASSWORD
☐ DATABASE_URL
☐ SECRET_KEY
☐ JWT_SECRET
☐ ENCRYPTION_KEY_PATIENT_DATA
☐ ENCRYPTION_KEY_PHARMA_DATA
☐ EVIJNAR_AI_KB_URL
☐ TWILIO_ACCOUNT_SID
☐ TWILIO_AUTH_TOKEN
☐ GOOGLE_MAPS_API_KEY
☐ HIPAA_AUDIT_WEBHOOK_URL
```

## 📝 For Each Secret:

1. **Name**: Copy from list above (exactly)
2. **Value**: Get from your .env file or generate new
3. **Repository**: Select "Evijnar-Health"
4. **Click**: "Add secret"

## 🔄 Values to Use

| Secret Name | Where to Get Value |
|---|---|
| DB_PASSWORD | From your database admin / RDS settings |
| DATABASE_URL | PostgreSQL connection string |
| SECRET_KEY | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| JWT_SECRET | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| ENCRYPTION_KEY_PATIENT_DATA | Generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| ENCRYPTION_KEY_PHARMA_DATA | Generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| EVIJNAR_AI_KB_URL | Optional JSON knowledge base endpoint for Evijnar Health AI |
| TWILIO_ACCOUNT_SID | twilio.com (account settings) |
| TWILIO_AUTH_TOKEN | twilio.com (account settings) |
| GOOGLE_MAPS_API_KEY | console.cloud.google.com (API keys) |
| HIPAA_AUDIT_WEBHOOK_URL | Your audit log provider |

## ✅ After Adding All 11 Secrets

- [ ] All 11 secrets created
- [ ] Each shows in the list
- [ ] Repository is set to "Evijnar-Health"
- [ ] Values are secure (GitHub forces HTTPS)
- [ ] Ready for CI/CD pipelines

## 💡 Pro Tips

- Use **different values** for different environments (prod vs staging)
- **Never share** secret values
- Rotate secrets quarterly
- GitHub masks secrets in logs automatically
