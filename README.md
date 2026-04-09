# Evijnar - Global Health Arbitrage Exchange

> **Solving the Hidden Price Crisis in Healthcare**
>
> A decentralized global healthcare access platform that aggregates and normalizes hospital price transparency data from USA, Europe, and India using AI-powered mapping and outcome-driven ranking.

---

## 📑 Table of Contents

- [Vision](#-project-vision)
- [Status](#-current-status)
- [Features](#-core-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Testing & CI/CD](#-testing--cicd)
- [Development](#-development-workflow)
- [Security](#-security--compliance)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Documentation](#-documentation)
- [License](#-license)

---

## 🌍 Project Vision

**Problem**: Patients lack transparent access to hospital prices and quality metrics across global healthcare markets. Price discovery is manual, trust-based, and inefficient.

**Solution**: Evijnar creates a unified global marketplace where patients can:
- 🔍 Search hospitals by procedure, quality, and cost across borders
- 💰 Compare success-adjusted pricing (not just lowest cost)
- 🏥 Access real-time recovery monitoring (IoMT)
- 💳 Secure micro-financing for affordable care
- 📊 Make informed decisions backed by outcome data

**Mission**: Democratize global healthcare access through transparency, equity, and technology.

---

## 📊 Current Status

| Component | Status | Phase |
|-----------|--------|-------|
| **Data Ingestion Engine** | ✅ Complete | Sprint 2 |
| **Phase 3 Integration Tests** | ✅ Complete | Phase 3 |
| **GitHub Actions CI/CD** | ✅ Complete | Phase 3 |
| **Authentication System** | ⏳ In Progress | Sprint 2 |
| **Hospital Search & Ranking** | ⏳ Planned | Sprint 2 |
| **Recovery Bridge (IoMT)** | ⏳ Planned | Sprint 3 |
| **Rural Financing (UPI)** | ⏳ Planned | Sprint 3 |

**Latest Release**: Phase 3 - Integration Testing & CI/CD (2026-04-08)

---

## ✨ Core Features

### 1. **Success-Adjusted Value Ranking** 🏆
- Ranks hospitals by Cost + Risk + Quality
- AI-powered analysis using Claude API
- Outcome-driven decision support
- Real-time price/quality scoring

### 2. **Global Data Aggregation** 🌐
- **USA**: HHS Price Transparency data
- **Europe**: EHDS (European Health Data Space)
- **India**: ABDM/UHI (Ayushman Bharat Digital Mission)
- Unified schema across geographies

### 3. **Recovery Bridge (IoMT Monitoring)** 👁️
- 30-day post-operative monitoring
- Real-time vital tracking (HR, SpO2, Temp, BP)
- Automated alert escalation
- Cross-border safety coordination

### 4. **Rural Financing** 💚
- UPI 2.0 micro-financing
- Health-EMI with flexible payback
- Tier 2 city routing for affordability
- Zero-interest options for essential procedures

### 5. **HIPAA-Compliant Architecture** 🔒
- Audit logging for all PHI access
- Zero-knowledge encryption for records
- Client-side PII encryption
- Quarterly key rotation
- GDPR right-to-be-forgotten support

### 6. **Mobile-First Design** 📱
- Next.js responsive frontend
- Low-bandwidth UI for rural connectivity
- Progressive loading & code splitting
- Image optimization (AVIF, WebP)

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **Next.js** | React framework with App Router | 15+ |
| **TypeScript** | Type-safe development | Latest |
| **Tailwind CSS** | Utility-first styling | Latest |
| **Zustand** | Lightweight state management | Latest |
| **Axios** | HTTP client | Latest |

### Backend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **FastAPI** | Async Python web framework | 0.104+ |
| **SQLAlchemy** | ORM for database | 2.0+ |
| **Pydantic** | Data validation | 2.5+ |
| **Alembic** | Database migrations | 1.12+ |
| **Uvicorn** | ASGI server | 0.24+ |
| **Python** | Runtime | 3.11+ |

### Data & Infrastructure
| Technology | Purpose | Version |
|-----------|---------|---------|
| **PostgreSQL** | Primary database | 16+ |
| **Redis** | Caching & session store | 7+ |
| **Prisma** | Database ORM (packages) | Latest |
| **Docker** | Containerization | Latest |
| **docker-compose** | Local orchestration | Latest |

### DevOps & Testing
| Technology | Purpose | Version |
|-----------|---------|---------|
| **GitHub Actions** | CI/CD pipeline | Built-in |
| **pytest** | Python testing framework | 7.4+ |
| **pytest-asyncio** | Async test support | 0.21+ |
| **Codecov** | Coverage reporting | Cloud |
| **pnpm** | Package manager (monorepo) | Latest |

### AI & External Services
| Service | Purpose |
|---------|---------|
| **Claude API (Anthropic)** | Intelligent data mapping |
| **Razorpay / UPI 2.0** | Payment processing |
| **Twilio** | SMS notifications (planned) |
| **Google Maps** | Geographic routing |

---

## 🚀 Quick Start

### Prerequisites
```bash
# System requirements
- Node.js 20+
- Python 3.11+
- PostgreSQL 16 (or Docker)
- Docker & Docker Compose (recommended)
- Git
```

### Installation

**1. Clone and Navigate**
```bash
git clone <repository>
cd Evijnar
```

**2. Install Global Tools**
```bash
npm install -g pnpm
```

**3. Install Dependencies**
```bash
pnpm install
```

**4. Configure Environment**
```bash
# API
cp apps/api/.env.example apps/api/.env

# Database
cp packages/database/.env.example packages/database/.env

# Web
cp apps/web/.env.example apps/web/.env
```

**5. Start Services (Recommended)**
```bash
# Option A: Docker Compose (includes PostgreSQL + Redis)
docker-compose up -d

# Option B: Manual Setup
# Terminal 1 - PostgreSQL
docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16

# Terminal 2 - Redis
docker run -d -p 6379:6379 redis:7

# Terminal 3 - Backend
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -e .
python run.py

# Terminal 4 - Frontend
cd apps/web
pnpm dev
```

**6. Setup Database**
```bash
cd apps/api
alembic upgrade head
```

### Verify Installation
```bash
# API Health Check
curl http://localhost:8000/health

# Frontend
Open http://localhost:3000 in browser

# Database
psql -U postgres -d evijnar -c "SELECT version();"
```

### Common Commands

**Development**
```bash
pnpm dev              # Run all services
pnpm type-check       # TypeScript check
pnpm lint             # Run linters
```

**Testing**
```bash
cd apps/api
pytest tests/test_integration_phase3.py -v --cov=app
python scripts/verify_data.py
bash PHASE3_QUICKREF.sh
```

**Database**
```bash
cd apps/api
alembic upgrade head     # Run migrations
alembic downgrade -1     # Rollback one migration
```

**CI/CD**
```bash
# View GitHub Actions (after pushing)
git push origin main
# Check: GitHub repo → Actions tab

# Local CI simulation
cd apps/api
./run-local-ci.sh
```

**Docker**
```bash
docker-compose up -d       # Start all services
docker-compose logs -f     # View logs
docker-compose down        # Stop all services
docker-compose ps          # See running containers
```

---

## 🏗️ Project Structure

```
Evijnar/
│
├── 📁 apps/                                # Application layer
│   │
│   ├── 📁 api/                            # FastAPI Backend (Python)
│   │   ├── app/
│   │   │   ├── 📁 routers/                # API route handlers
│   │   │   │   ├── auth.py                # Authentication endpoints
│   │   │   │   ├── hospitals.py           # Hospital search & details
│   │   │   │   ├── pricing.py             # Pricing & normalization
│   │   │   │   ├── bookings.py            # Booking management
│   │   │   │   ├── recovery.py            # Recovery Bridge (IoMT)
│   │   │   │   ├── patients.py            # Patient profiles
│   │   │   │   ├── financing.py           # Rural financing
│   │   │   │   └── health.py              # Health checks
│   │   │   │
│   │   │   ├── 📁 services/               # Business logic
│   │   │   │   ├── 📁 data_ingestion/     # Data ingestion engine
│   │   │   │   │   ├── ingestion_engine.py
│   │   │   │   │   ├── 📁 loaders/        # Format-specific loaders
│   │   │   │   │   │   ├── hhs_loader.py
│   │   │   │   │   │   ├── ehds_loader.py
│   │   │   │   │   │   ├── abdm_loader.py
│   │   │   │   │   │   └── json_loader.py
│   │   │   │   │   ├── 📁 mappers/        # Claude-powered mappers
│   │   │   │   │   │   ├── hospital_mapper.py
│   │   │   │   │   │   ├── procedure_mapper.py
│   │   │   │   │   │   └── normalizer_mapper.py
│   │   │   │   │   ├── models.py          # Pydantic schemas
│   │   │   │   │   └── errors.py          # Custom exceptions
│   │   │   │   │
│   │   │   │   └── 📁 utils/              # Utilities
│   │   │   │       └── llm_client.py      # Claude API client
│   │   │   │
│   │   │   ├── 📁 repositories/           # Data access layer
│   │   │   │   ├── hospital.py
│   │   │   │   ├── procedure.py
│   │   │   │   ├── normalizer.py
│   │   │   │   └── audit.py
│   │   │   │
│   │   │   ├── 📁 models/                 # Database models
│   │   │   │   └── database.py
│   │   │   │
│   │   │   ├── 📁 db/                     # Database configuration
│   │   │   │   └── session.py
│   │   │   │
│   │   │   ├── config.py                  # Configuration
│   │   │   ├── middleware.py              # HIPAA, security
│   │   │   └── main.py                    # FastAPI app entry
│   │   │
│   │   ├── 📁 tests/                      # Test suite
│   │   │   ├── conftest.py                # Fixtures & setup
│   │   │   └── test_integration_phase3.py # Integration tests
│   │   │
│   │   ├── 📁 scripts/                    # Utility scripts
│   │   │   ├── ingest_data.py             # CLI ingestion tool
│   │   │   ├── verify_data.py             # Database verification
│   │   │   └── run_phase3_tests.py        # Test orchestrator
│   │   │
│   │   ├── 📁 alembic/                    # Database migrations
│   │   │   ├── env.py
│   │   │   └── 📁 versions/
│   │   │
│   │   ├── pyproject.toml                 # Python dependencies
│   │   ├── pytest.ini                     # Pytest configuration
│   │   ├── Dockerfile                     # Container image
│   │   ├── run.py                         # Entry point
│   │   └── .env.example                   # Environment template
│   │
│   └── 📁 web/                            # Next.js Frontend (TypeScript)
│       ├── 📁 src/
│       │   ├── 📁 app/                    # App router pages
│       │   ├── 📁 components/             # React components
│       │   ├── 📁 lib/                    # Client utilities
│       │   └── 📁 styles/                 # Tailwind CSS
│       │
│       ├── 📁 public/                     # Static assets
│       ├── next.config.js
│       ├── tsconfig.json
│       ├── tailwind.config.js
│       ├── Dockerfile
│       ├── package.json
│       └── .env.example
│
├── 📁 packages/                            # Shared packages
│   │
│   ├── 📁 database/                       # Prisma database package
│   │   ├── 📁 prisma/
│   │   │   ├── schema.prisma              # Database schema
│   │   │   ├── seed.ts                    # Seed data
│   │   │   └── 📁 migrations/
│   │   │
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── .env.example
│   │
│   ├── 📁 shared-types/                   # TypeScript types (planned)
│   └── 📁 utils/                          # Common utilities (planned)
│
├── 📁 docs/                                # Documentation
│   ├── ARCHITECTURE.md                    # System design & flows
│   ├── PHASE3_TESTING.md                  # Integration testing guide
│   ├── CI_CD_SETUP.md                     # GitHub Actions guide
│   ├── SPRINT2_IMPLEMENTATION.md          # Sprint 2 overview
│   ├── API.md                             # API reference (planned)
│   ├── DATABASE.md                        # Schema documentation (planned)
│   └── COMPLIANCE.md                      # HIPAA/GDPR guidelines (planned)
│
├── 📁 .github/                             # GitHub configuration
│   └── 📁 workflows/                      # GitHub Actions CI/CD
│       ├── ci-fast.yml                    # Lint on every push (~2 min)
│       ├── ci-full.yml                    # Tests on PR/main (~10 min)
│       └── coverage.yml                   # Coverage tracking (~2 min)
│
├── 📁 samples/                             # Sample data files
│   ├── hhs_2026_sample.json
│   ├── ehds_2026_sample.json
│   └── abdm_2026_sample.json
│
├── docker-compose.yml                     # Docker orchestration
├── pnpm-workspace.yaml                    # Monorepo configuration
├── package.json                           # Root package
├── .gitignore                             # Git exclusions
├── README.md                              # This file
├── PHASE3_QUICKREF.sh                     # Testing quick reference
├── CI_CD_QUICKSTART.sh                    # CI/CD quick reference
└── LICENSE                                # License file
```

---

## 🏛️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        EVIJNAR PLATFORM                         │
├──────────────────────┬─────────────────────┬────────────────────┤
│   FRONTEND LAYER     │    API GATEWAY      │   BACKEND LAYER    │
│                      │                     │                    │
│  Next.js 15          │  CORS & Auth        │  FastAPI + Uvicorn │
│  (Mobile-First)      │  Rate Limiting      │                    │
│                      │  Request Logging    │  Services:         │
│  ├─ Hospital Search  │  (HIPAA)            │  ├─ Hospital Mgmt  │
│  ├─ Booking UI       │                     │  ├─ Pricing Engine │
│  ├─ Recovery Monitor │                     │  ├─ Recovery Bridge│
│  └─ Payment Portal   │                     │  └─ Financing      │
│                      │                     │                    │
├──────────────────────┴─────────────────────┴────────────────────┤
│                        DATA LAYER                               │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  PostgreSQL 16  │  │  Redis 7     │  │  Elasticsearch  │   │
│  │  (Primary DB)   │  │  (Cache)     │  │  (Search Index) │   │
│  │                 │  │              │  │                 │   │
│  │ ├─ Users        │  │ ├─ Sessions  │  │ ├─ Hospitals    │   │
│  │ ├─ Hospitals    │  │ ├─ Cache     │  │ ├─ Procedures   │   │
│  │ ├─ Prices       │  │ │            │  │ └─ Doctors      │   │
│  │ ├─ Recovery     │  │ │            │  │                 │   │
│  │ └─ Financing    │  │ │            │  │                 │   │
│  └─────────────────┘  └──────────────┘  └─────────────────┘   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      EXTERNAL INTEGRATIONS                       │
├───────────────┬──────────────┬──────────────┬────────────────────┤
│ Health Data   │  Payments    │  Monitoring  │  Compliance        │
│               │              │              │                    │
│ ├─ HHS HPT    │ ├─ UPI 2.0   │ ├─ Grafana   │ ├─ HIPAA Audit Log │
│ ├─ EHDS       │ ├─ Razorpay  │ ├─ Datadog   │ ├─ GDPR Compliance │
│ ├─ ABDM/UHI   │ └─ Stripe    │ ├─ CloudWatch│ └─ SOC 2 Ready     │
│ └─ FHIR APIs  │              │ └─ Custom IoT│                    │
│               │              │   Dashboard  │                    │
└───────────────┴──────────────┴──────────────┴────────────────────┘
```

### Data Ingestion Flow

```
Raw Data Files           Loaders              Mapping              Database
(HHS/EHDS/ABDM)                                                    
    │                                                                
    ├─ HHS JSON ────→ HHSLoader ──→ RawHospitalData  │               
    ├─ EHDS JSON ───→ EHDSLoader ─→ RawHospitalData  ├──→ Claude API
    └─ ABDM JSON ───→ ABDMLoader ─→ RawHospitalData  │   Mappers
                                     │                
                      HospitalMapper  ├─→ NormalizedHospitalData
                      ProcedureMapper ├─→ NormalizedProcedureData
                      NormalizerMapper└─→ NormalizedPriceNormalizerData
                                     │
                            Database Writer (with HIPAA Logging)
                                     │
                              PostgreSQL Database
                                     │
                         ├─ global_hospitals
                         ├─ procedure_price
                         ├─ price_normalizer
                         └─ audit_log
```

### Hospital Search & Ranking Flow

```
User Query              Processing              Ranking             Results
(Procedure + Location)                                              
    │                                                                
    ├─ Parse request  ──→ Normalize codes (CPT/ICD-10/UHI)
    │                      │
    ├─ Search hospitals ─→ Filter by location, accreditation
    │                      │
    ├─ Fetch pricing ──→ Real-time from database
    │                      │
    ├─ Fetch outcomes ──→ Quality + complication + readmission rates
    │                      │
    └─ Rank & explain ──→ Success-Adjusted Value (Cost + Risk + Quality)
                          
                         Return:
                         • Top matches
                         • Price/quality comparison
                         • Recovery Bridge availability
                         • Financing options
```

---

## 📊 Database Schema

### Core Tables (15 total)

**Identity & Access**
```sql
-- Users & authentication
users                      -- User accounts, roles, credentials
user_roles                 -- Role assignments (patient, provider, admin)
```

**Hospital Domain**
```sql
-- Hospital & provider data
global_hospitals           -- Hospital metadata, accreditation, quality metrics
departments                -- Hospital departments (Cardiology, Oncology, etc.)
surgeons                   -- Surgeon profiles and specialties
healthcare_providers       -- Individual healthcare providers
recovery_providers         -- Post-operative monitoring providers
```

**Pricing & Procedures**
```sql
procedure_price            -- Hospital-specific procedure pricing
price_normalizer           -- CPT ↔ ICD-10 ↔ UHI code mappings
clinical_categories        -- Procedure classification
```

**Patient & Medical**
```sql
patients                   -- Patient profiles (with encrypted PII)
medical_records            -- Patient medical history (zero-knowledge encrypted)
```

**Business Domain**
```sql
hospital_bookings          -- Procedure bookings and appointments
recovery_sessions          -- 30-day post-op monitoring sessions
recovery_vitals            -- Time-series vital signs from wearables
recovery_alerts            -- Automated health alerts
rural_financing            -- UPI micro-loans and Health-EMI records
emi_schedules              -- Amortization schedules for financing
```

**Compliance**
```sql
audit_logs                 -- HIPAA audit trail (immutable)
```

### Key Features

| Feature | Benefit |
|---------|---------|
| **Encrypted PII** | Patient data protected with client-side keys |
| **Zero-Knowledge Encryption** | Medical records never readable by server |
| **Audit Logging** | Every PHI access tracked with timestamp |
| **Soft Deletes** | GDPR right-to-be-forgotten support |
| **Geo-Spatial Indexes** | Fast location-based hospital search |
| **Full-Text Search** | Hospital name and procedure search |
| **Time-Series Tables** | Recovery vitals (millions of data points) |
| **Foreign Keys + Cascade** | Data integrity and orphan prevention |

---

## 🔄 API Endpoints

### Authentication
```http
POST   /api/v1/auth/signup           # Register new user
POST   /api/v1/auth/login            # Login & get JWT token
POST   /api/v1/auth/refresh          # Refresh access token
POST   /api/v1/auth/logout           # Logout & invalidate token
POST   /api/v1/auth/mfa/setup        # Enable MFA
POST   /api/v1/auth/mfa/verify       # Verify MFA code
```

### Hospitals (Public)
```http
GET    /api/v1/hospitals/search?procedure_code=&country=&radius_km=
       # Search hospitals by procedure, location, radius

GET    /api/v1/hospitals/{hospital_id}
       # Get hospital details, accreditation, quality metrics

GET    /api/v1/hospitals/{hospital_id}/departments
       # Get hospital departments and specialties

GET    /api/v1/hospitals/{hospital_id}/procedures
       # Get procedures available at hospital with pricing
```

### Pricing & Normalization
```http
GET    /api/v1/pricing/normalize/{cpt_code}
       # Normalize CPT code to ICD-10 + UHI equivalents

GET    /api/v1/pricing/hospital/{hospital_id}/procedures
       # Get all procedures with pricing at hospital

GET    /api/v1/pricing/compare?procedure_code=&countries=US,DE,IN
       # Compare pricing across hospitals/countries

GET    /api/v1/pricing/success-adjusted-rank?procedure_code=&location=
       # Get ranked hospitals by success-adjusted value
```

### Bookings (Protected)
```http
POST   /api/v1/bookings
       # Create new booking

GET    /api/v1/bookings/{booking_id}
       # Get booking details

PUT    /api/v1/bookings/{booking_id}/cancel
       # Cancel booking with reason

GET    /api/v1/bookings/patient/{patient_id}
       # Get patient's booking history
```

### Recovery Bridge (Protected)
```http
GET    /api/v1/recovery/session/{booking_id}
       # Get 30-day recovery session details

POST   /api/v1/recovery/vitals
       # Record vital signs from wearable

GET    /api/v1/recovery/session/{session_id}/alerts
       # Get triggered alerts for session

POST   /api/v1/recovery/alerts/{alert_id}/acknowledge
       # Acknowledge alert receipt

PUT    /api/v1/recovery/alerts/{alert_id}/escalate
       # Escalate alert to doctor
```

### Rural Financing (Protected)
```http
POST   /api/v1/financing
       # Create financing request for procedure

GET    /api/v1/financing/{financing_id}
       # Get financing details and status

POST   /api/v1/financing/{financing_id}/payment
       # Record EMI payment

GET    /api/v1/financing/{financing_id}/emi-schedule
       # Get payment schedule

PUT    /api/v1/financing/{financing_id}/approve
       # Approve financing (admin)
```

### Patients (Protected)
```http
GET    /api/v1/patients/{patient_id}
       # Get patient profile (encrypted)

PUT    /api/v1/patients/{patient_id}
       # Update patient info

GET    /api/v1/patients/{patient_id}/records
       # Get medical records (zero-knowledge encrypted)

DELETE /api/v1/patients/{patient_id}
       # Request data deletion (GDPR)
```

### Health & Admin
```http
GET    /api/v1/health
       # Service health check

GET    /api/v1/admin/metrics
       # System metrics (admin only)

POST   /api/v1/admin/ingest/hhs
       # Trigger HHS data ingestion (admin)

POST   /api/v1/admin/audit/logs
       # Get audit logs (admin + HIPAA)
```

### Response Format
```json
{
  "status": "success",
  "data": { /* response payload */ },
  "timestamp": "2026-04-08T10:30:00Z",
  "request_id": "uuid-here"
}
```

### Error Handling
```json
{
  "status": "error",
  "error": {
    "code": "HOSPITAL_NOT_FOUND",
    "message": "Hospital with ID 123 not found",
    "details": {}
  },
  "timestamp": "2026-04-08T10:30:00Z",
  "request_id": "uuid-here"
}
```

---

## 🧪 Testing & CI/CD

### Phase 3 Integration Testing

**Test Coverage**: 10+ tests across 4 categories

| Category | Tests | Purpose |
|----------|-------|---------|
| **End-to-End** | 5 | HHS/EHDS/ABDM ingestion, data persistence |
| **Idempotency** | 2 | Duplicate handling, skipping |
| **Atomicity** | 1 | Partial failure rollback |
| **Concurrency** | 2 | Parallel processing, race conditions |

**Running Tests**
```bash
cd apps/api

# Run all Phase 3 tests
pytest tests/test_integration_phase3.py -v

# Run specific category
pytest tests/test_integration_phase3.py::TestIdempotency -v

# With coverage
pytest tests/test_integration_phase3.py --cov=app --cov-report=html

# Run quick reference
bash PHASE3_QUICKREF.sh
```

### GitHub Actions CI/CD

**Workflows**: 3 automated workflows

| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| **ci-fast.yml** | Every push | ~2 min | Lint, type check, format |
| **ci-full.yml** | PR to main | ~10 min | Full tests, coverage |
| **coverage.yml** | Main merge | ~2 min | Codecov upload |

**Pipeline Features**
- ✅ Automatic PostgreSQL provisioning
- ✅ Alembic migrations
- ✅ Codecov integration
- ✅ HTML coverage artifacts
- ✅ PR blocking on failures
- ✅ Fast feedback (2 min lint)

**Setup**
```bash
# Push to GitHub
git push origin main

# Set GitHub Secrets
# Settings → Secrets → Add CODECOV_TOKEN

# View workflows
# GitHub repo → Actions tab
```

**Local CI Testing**
```bash
cd apps/api

# Run like fast workflow
ruff check app/
black --check app/
mypy app/ --ignore-missing-imports

# Run like full workflow
pytest tests/test_integration_phase3.py -v --cov=app
python scripts/verify_data.py
```

---

## 👨‍💻 Development Workflow

### Branch Strategy

```
main (production-ready)
 ▲
 │ (PR with all checks passing)
 │
develop (integration branch)
 ▲
 │ (feature PRs)
 │
feature/* (feature development)
├─ feature/auth-system
├─ feature/hospital-search
├─ feature/recovery-bridge
└─ feature/rural-financing
```

### Making Changes

**1. Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

**2. Develop & Test Locally**
```bash
cd apps/api
pytest tests/ -v
mypy app/
black app/
ruff check app/
```

**3. Commit with Clear Messages**
```bash
git commit -m "Add feature: hospital search with geo-spatial filtering

- Implement haversine distance calculation
- Add radius parameter to /search endpoint
- Create database indexes for performance
- Add 5+ integration tests

Closes #123"
```

**4. Push & Create PR**
```bash
git push origin feature/your-feature-name
# Open PR on GitHub
```

**5. Wait for CI Checks**
- fast workflow runs (2 min)
- full workflow runs (10 min)
- coverage reported
- code review

**6. Merge After Approval**
```bash
# After code review + CI passing
# Click "Merge" on GitHub
```

**7. Delete Branch**
```bash
git branch -d feature/your-feature-name
```

### Code Style Guide

**Python**
- Use Black for formatting
- Use ruff for linting
- Use mypy for type checking
- Max line length: 88 characters
- Type annotations on all functions

**TypeScript/JavaScript**
- Use ESLint + Prettier
- Type annotations required
- Components in PascalCase
- Utilities in camelCase

**Commit Messages**
- Start with verb (Add/Fix/Update/Remove/Refactor)
- Reference issue numbers (#123)
- Include context in body
- Keep first line under 70 chars

---

## 🔐 Security & Compliance

### HIPAA Compliance ✅

**Audit Logging**
- Every API access logged with timestamp, user, IP
- Immutable audit table (no deletes)
- 7-year retention

**PHI Protection**
- Patient names, DOB encrypted at rest
- Medical records zero-knowledge encrypted
- Access control by role
- Encrypted TLS in transit

**Breach Notification**
- Automated detection of suspicious access
- 24-hour breach notification protocol
- Detailed incident response plan

### GDPR Compliance ✅

**Right to Be Forgotten**
- Soft delete flags on patient records
- Automatic data deletion workflow
- Minimal data retention (30 days cache)

**Consent Management**
- Explicit consent tracking
- Consent audit trail
- Opt-out mechanisms for all communications

**Data Portability**
- Export patient data in standard format
- FHIR API for data exchange

### Security Measures

**Authentication**
- JWT tokens with 1-hour expiration
- Refresh tokens (7 days)
- MFA support (TOTP)
- Rate limiting (100 req/min per user)

**Encryption**
- TLS 1.3+ for all transit
- AES-256 for at-rest encryption
- Quarterly key rotation
- Client-side encryption for sensitive data

**API Security**
- CORS configured per domain
- CSRF protection
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)

**Infrastructure**
- Regular security patches
- Vulnerability scanning
- Secrets management (GitHub Secrets only)
- Network isolation (VPC)

---

## 🚀 Deployment

### Local Development
```bash
docker-compose up -d
# Services available at:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Database: localhost:5432
# - Redis: localhost:6379
```

### Staging Deployment (Planned)
```bash
git push origin staging
# Automatic deployment to staging environment
# URL: staging.evijnar.com
```

### Production Deployment (Planned)
```bash
git tag v1.0.0
git push origin v1.0.0
# Automatic deployment to production
# URL: app.evijnar.com
# Requires manual approval
```

### Container Deployment

**Build Images**
```bash
# API
docker build -t evijnar-api:latest apps/api/

# Web
docker build -t evijnar-web:latest apps/web/

# Push to registry
docker push evijnar-api:latest
docker push evijnar-web:latest
```

**Run Containers**
```bash
docker run -d \
  -e DATABASE_URL=postgresql://... \
  -p 8000:8000 \
  evijnar-api:latest

docker run -d \
  -p 3000:3000 \
  evijnar-web:latest
```

---

## 🔧 Troubleshooting

### Common Issues

**"Database connection refused"**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Or start it
docker-compose up -d postgres

# Verify credentials in .env
cat apps/api/.env | grep DATABASE_URL
```

**"Port 8000 already in use"**
```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
FASTAPI_PORT=8001 python run.py
```

**"Module not found errors"**
```bash
# Reinstall dependencies
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e .
```

**"Tests failing locally but passing in CI"**
```bash
# Check environment differences
diff .env .env.test

# Run with test environment
pytest --env=test

# Check PostgreSQL version
psql --version
```

**"No such table: global_hospitals"**
```bash
# Run migrations
cd apps/api
alembic upgrade head

# Verify
alembic current
```

**"GitHub Actions workflow not running"**
```bash
# Verify workflows are committed
git log .github/workflows/

# Check branch protection rules
# Settings → Branches → main

# Trigger manual run
# GitHub Actions tab → Select workflow → Run workflow
```

---

## 🗓️ Roadmap

### Phase 1-2 ✅ (Completed)
- [x] Data ingestion engine (HHS/EHDS/ABDM)
- [x] Database schema & migrations
- [x] Basic API structure
- [x] Docker setup

### Phase 3 ✅ (Completed)
- [x] Integration tests (10+ tests)
- [x] GitHub Actions CI/CD (3 workflows)
- [x] Coverage reporting
- [x] Database verification

### Sprint 2 ⏳ (In Progress)
- [ ] Authentication (JWT + MFA)
- [ ] Hospital search with geo-spatial ranking
- [ ] Success-Adjusted Value algorithm
- [ ] IoMT vitals ingestion
- [ ] Alert escalation engine
- [ ] UPI 2.0 integration

### Sprint 3 ⏳ (Planned)
- [ ] Recovery Bridge (30-day monitoring)
- [ ] Rural financing EMI system
- [ ] Mobile app (React Native)
- [ ] Payment processing (Razorpay/Stripe)
- [ ] Notification system (SMS/Email/Push)
- [ ] Analytics & reporting dashboard

### Future 🚀 (Planned)
- [ ] AI-powered doctor recommendations
- [ ] Insurance coverage integration
- [ ] Telemedicine consultations
- [ ] Medical records marketplace
- [ ] Quality benchmarking
- [ ] Telehealth integration
- [ ] International expansion

---

## 🤝 Contributing

### Code of Conduct
We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Contribution Process
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow branch strategy (feature/* branches)
4. Write tests for new code
5. Ensure all tests pass locally: `pytest tests/ -v`
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request with description
9. Respond to code review feedback
10. Merge after approval

### Reporting Issues
- Use GitHub Issues
- Include reproduction steps
- Provide environment details
- Attach relevant logs

### Security Concerns
- Do NOT create public GitHub issues for security vulnerabilities
- Report security issues by describing them in a private manner
- Allow 48 hours for response

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design & data flows |
| [PHASE3_TESTING.md](docs/PHASE3_TESTING.md) | Integration testing guide |
| [CI_CD_SETUP.md](docs/CI_CD_SETUP.md) | GitHub Actions CI/CD guide |
| [SPRINT2_IMPLEMENTATION.md](docs/SPRINT2_IMPLEMENTATION.md) | Sprint 2 overview |

**Quick References**
- [PHASE3_QUICKREF.sh](PHASE3_QUICKREF.sh) - Testing quick guide
- [CI_CD_QUICKSTART.sh](CI_CD_QUICKSTART.sh) - CI/CD quick guide

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [Next.js](https://nextjs.org/), and [PostgreSQL](https://www.postgresql.org/)
- Data mapping powered by [Claude API](https://anthropic.com/)
- Infrastructure powered by [Docker](https://www.docker.com/) and [GitHub Actions](https://github.com/features/actions)
- Inspiration from global healthcare transparency initiatives (HHS, EHDS, ABDM)
