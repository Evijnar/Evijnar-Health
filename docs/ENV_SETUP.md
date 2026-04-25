# Environment Configuration Guide

## 📁 File Structure

Each environment has its own configuration:

```
apps/api/
  ├── .env.example   ← Template (COMMIT THIS)
  └── .env           ← Actual values (NEVER COMMIT - in .gitignore)

apps/web/
  ├── .env.example   ← Template (COMMIT THIS)
  └── .env.local     ← Actual values (NEVER COMMIT - in .gitignore)

packages/database/
  ├── .env.example   ← Template (COMMIT THIS)
  └── .env           ← Actual values (NEVER COMMIT - in .gitignore)
```

---

## 🚀 Setup Instructions

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/evijnar.git
cd evijnar
```

### Step 2: Create `.env` Files

#### For API (`apps/api/.env`)

```bash
# Copy template
cp apps/api/.env.example apps/api/.env

# Edit with your values
nano apps/api/.env
```

**Configuration Example:**

```env
# API Configuration
APP_ENV=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=v1

# Database (local development)
DATABASE_URL=postgresql://evijnar_dev:evijnar_password@localhost:5432/evijnar_dev

# Security Keys - FOR DEVELOPMENT ONLY
# Generate new keys: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-development-secret-key-here
JWT_SECRET=your-development-jwt-secret-here

# Encryption Keys - FOR DEVELOPMENT ONLY
# Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY_PATIENT_DATA=your-32-byte-base64-fernet-key-here
ENCRYPTION_KEY_PHARMA_DATA=your-32-byte-base64-fernet-key-here

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Redis
REDIS_URL=redis://localhost:6379

# Evijnar Health AI knowledge base (optional for development)
EVIJNAR_AI_KB_URL=

# HIPAA
HIPAA_AUDIT_LOG_ENABLED=true
```

#### For Frontend (`apps/web/.env.local`)

```bash
cp apps/web/.env.example apps/web/.env.local
nano apps/web/.env.local
```

**Configuration Example:**

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

#### For Database (`packages/database/.env`)

```bash
cp packages/database/.env.example packages/database/.env
nano packages/database/.env
```

**Configuration Example:**

```env
DATABASE_URL=postgresql://user:password@localhost:5432/evijnar_dev
```

### Step 3: Generate Encryption Keys

For development, you need Fernet encryption keys:

```bash
cd apps/api

# Generate patient data key
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY_PATIENT_DATA=' + Fernet.generate_key().decode())"

# Generate pharma data key
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY_PHARMA_DATA=' + Fernet.generate_key().decode())"
```

Update your `.env` with these values.

### Step 4: Install Dependencies

```bash
# Install Node dependencies
pnpm install

# Install Python dependencies
cd apps/api
pip install -r requirements.txt
```

### Step 5: Set Up Database

```bash
# Start Docker containers
docker-compose up -d

# Run migrations
cd apps/api
alembic upgrade head

# Seed database (optional)
python -m scripts.seed_data
```

### Step 6: Verify Setup

```bash
# Check API health
curl http://localhost:8000/health

# Check frontend
open http://localhost:3000
```

---

## 🔐 Production Setup

### Using GitHub Secrets

All production secrets are stored in GitHub Organization Settings:

```
Settings → Secrets and variables → Actions
```

### Required Secrets

```
- DATABASE_URL        (production database)
- SECRET_KEY          (production secret)
- JWT_SECRET          (production JWT secret)
- ENCRYPTION_KEY_*    (production encryption keys)
- EVIJNAR_AI_KB_URL   (optional remote knowledge base for Evijnar Health AI)
- TWILIO_*           (SMS service credentials)
```

See `docs/GITHUB_SECRETS_SETUP.md` for detailed instructions.

---

## ⚠️ Common Issues

### Error: `DATABASE_URL` not set

```
❌ Error: DATABASE_URL environment variable not set
```

**Solution:**
```bash
# Ensure .env file exists
ls -la apps/api/.env

# Check value is set
grep DATABASE_URL apps/api/.env

# Reload environment
source apps/api/.env
```

### Error: `encryption_key_patient_data` is not valid

```
❌ Error: encryption_key_patient_data value length must be 44
```

**Solution:**
```bash
# Generate valid Fernet key (must be 44 characters)
python -c "from cryptography.fernet import Fernet; key = Fernet.generate_key(); print(f'Length: {len(key.decode())}'); print(f'Value: {key.decode()}')"

# Must output exactly 44 characters
```

### Error: Cannot connect to PostgreSQL

```
❌ Error: could not connect to server: Connection refused
```

**Solution:**
```bash
# Start Docker containers
docker-compose up -d

# Wait for health check
docker ps

# Check logs
docker-compose logs postgres
```

---

## 🔄 Environment Variables Reference

### Development

```env
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql://user:pass@localhost:5432/evijnar_dev
SECRET_KEY=dev-key
JWT_SECRET=dev-jwt-key
```

### Testing

```env
APP_ENV=test
DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost:5432/evijnar_test
SECRET_KEY=test-key
```

### Production

```env
APP_ENV=production
DEBUG=false
DATABASE_URL=<from GitHub Secrets>
SECRET_KEY=<from GitHub Secrets>
JWT_SECRET=<from GitHub Secrets>
# All other sensitive vars from GitHub Secrets
```

---

## 🛡️ Security Checklist

Before committing, verify:

- [ ] `.env` is in `.gitignore`
- [ ] No secrets in `.env.example`
- [ ] `.env` files are never committed
- [ ] All `.env.example` files are up-to-date
- [ ] No hardcoded API keys in code
- [ ] Database credentials only in environment variables

---

## 📚 Related Documentation

- [SECURITY.md](../SECURITY.md) - Security policies
- [GITHUB_SECRETS_SETUP.md](./GITHUB_SECRETS_SETUP.md) - GitHub secrets configuration
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Project architecture

---

Last Updated: 2026-04-09
