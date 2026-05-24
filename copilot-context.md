# Evijnar — Copilot Master Context

Use this file as the canonical Copilot context for working on the Evijnar repository. It summarizes the architecture, tech stack, project layout, core tables, coding rules, response formats, and data sources. Follow it when generating or modifying code in this workspace.

## Tech Stack
- Backend: FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic 2.5+, Alembic 1.12+, Python 3.11+
- Frontend: Next.js 15+ (App Router), TypeScript, Tailwind CSS, Zustand, Axios
- Database: PostgreSQL 16 (primary), Redis 7 (cache/sessions)
- DevOps: Docker, docker-compose, GitHub Actions (ci-fast.yml, ci-full.yml, coverage.yml)
- Testing: pytest 7.4+, pytest-asyncio 0.21+

## Project Layout (source of truth)
```
apps/api/app/
  routers/       → auth, hospitals, pricing, bookings, recovery, patients, financing, health
  services/data_ingestion/ → ingestion_engine, loaders (hhs/ehds/abdm/json), mappers
  services/utils/llm_client.py → Evijnar Health AI
  repositories/  → hospital, procedure, normalizer, audit
  models/database.py
  db/session.py
  config.py, middleware.py, main.py
apps/web/src/
  app/           → App Router pages
  components/    → React components
  lib/           → Client utilities
```

## Core Database Tables (PostgreSQL)
users, user_roles, global_hospitals, departments, surgeons, healthcare_providers,
recovery_providers, procedure_price, price_normalizer, clinical_categories,
patients, medical_records, hospital_bookings, recovery_sessions, recovery_vitals,
recovery_alerts, rural_financing, emi_schedules, audit_logs

## Key Coding Rules (required)
1. All FastAPI routes must use async/await.
2. All PHI access must write to `audit_logs` (HIPAA).
3. Patient PII encrypted at rest (AES-256); medical records zero-knowledge encrypted.
4. JWT tokens expire in 1 hour; refresh tokens in 7 days.
5. Rate limit: 100 req/min per user.
6. Use parameterized SQLAlchemy queries only (no raw SQL strings).
7. Pydantic v2 validators on all input models.
8. Type annotations required on every Python function.
9. Black (format) + ruff (lint) + mypy (types) must all pass.
10. All new features need pytest integration tests.

## Endpoint Response Format (required)
- Success:
```
{"status":"success","data":{...},"timestamp":"ISO8601","request_id":"uuid"}
```
- Error:
```
{"status":"error","error":{"code":"...","message":"...","details":{}},"timestamp":"...","request_id":"..."}
```

## Data Sources
- USA: HHS Price Transparency (hhs_loader.py) — JSON
- Europe: EHDS (ehds_loader.py) — JSON
- India: ABDM/UHI (abdm_loader.py) — JSON

All loaders normalize to: `NormalizedHospitalData`, `NormalizedProcedureData`, `NormalizedPriceNormalizerData`.

---

When making changes, always reference this file and the README as the single source of truth for product intent and technical constraints. If you need enforcement (pre-commit hooks, CI rules, or template PR checks), ask and I will scaffold them.
