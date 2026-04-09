# Evijnar Architecture Documentation

## System Design Overview

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
│  ├─ Booking UI       │                     │  ├─ Price Engine   │
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

## Data Flow Architecture

### 1. Hospital Search & Ranking Flow
```
User Query (Procedure + Location)
    ↓
[Frontend] Next.js Search UI
    ↓ HTTP GET
[API] /hospitals/search endpoint
    ↓
[Service] Hospital Ranking Engine
    ├─ Query PostgreSQL (Geo-spatial index)
    ├─ Retrieve prices (normalizer mapping)
    ├─ Calculate Success-Adjusted Value:
    │   Value = (Cost Component) + (Risk Component) + (Quality Component)
    ├─ Cache results in Redis (5 min TTL)
    └─ Return ranked results
    ↓
[Frontend] Display ranked hospitals with comparison
```

### 2. Booking & Recovery Bridge Flow
```
Patient Creates Booking
    ↓
[API] POST /bookings
    ├─ Validate patient consent (HIPAA)
    ├─ Create booking record
    ├─ Initialize 30-day Recovery Session
    └─ Assign surgeon & local clinic
    ↓
Post-Op: Recovery Monitoring Begins
    ├─ IoMT Wearables → AWS IoT Core (or custom)
    ├─ Vitals data → Recovery Bridge API
    ├─ [Service] Alert Engine
    │   ├─ Compare vitals to normal ranges
    │   ├─ Trigger alerts if critical
    │   └─ Notify surgeon & clinic
    └─ Visualization in dashboard
    ↓
Day 30: Session auto-closes
    └─ Post-op summary generated
```

### 3. Rural Financing Flow
```
Patient Selects Financing
    ↓
[API] POST /financing
    ├─ Validate eligibility (Tier 2/3 only for micro-loans)
    ├─ Calculate EMI based on:
    │   ├─ Principal amount
    │   ├─ Interest rate (subsidized for rural: 0-4%)
    │   ├─ Tenure (3/6/12/24 months)
    │   └─ Prepayment incentives
    ├─ Generate EMI schedule
    └─ Create payment records
    ↓
UPI Integration (NPCI 2.0)
    ├─ Generate UPI string (via Razorpay/Stripe bridge)
    ├─ Patient scans QR or clicks link
    ├─ Payment routed to escrow account
    ├─ Webhook confirms payment
    └─ Update financing status
```

## Authorization & Access Control

### Role-Based Access Control (RBAC)
```
Patient
├─ View own profile & records
├─ Search hospitals & procedures
├─ Create/manage bookings
├─ View recovery vitals (own)
└─ View financing details (own)

Surgeon
├─ View assigned patients
├─ View recovery sessions & alerts
├─ Acknowledge/respond to alerts
├─ Update post-op notes
└─ Access surgical team tools

Healthcare Provider (Clinic)
├─ View assigned recovery patients
├─ Update vitals on behalf of wearables
├─ Manage local clinic inventory
└─ View patient outcomes

Admin
├─ Manage hospitals & departments
├─ Update price transparency data
├─ View analytics dashboard
├─ Manage user roles & permissions
└─ Export audit logs
```

## Security & Compliance Layers

### Layer 1: Network Security
- **TLS 1.3** for all client-server communication
- **WAF** (Web Application Firewall) blocks SQL injection, XSS
- **Rate Limiting** per IP (100 req/min for non-auth, 1000/min for auth)
- **DDoS Protection** via Cloudflare or AWS Shield

### Layer 2: Application Security
- **Input Validation**: Pydantic schemas on all endpoints
- **CSRF Protection**: SameSite cookies, CSRF tokens
- **SQL Injection Prevention**: Parameterized queries (SQLAlchemy)
- **XSS Prevention**: CSP headers, sanitized outputs

### Layer 3: Data Security
- **Encryption at Rest**: PostgreSQL TDE (Transparent Data Encryption)
- **Encryption in Transit**: TLS 1.3
- **Field-Level Encryption**: Patient PII encrypted with FernetSymmetric
- **Key Rotation**: Quarterly via AWS Secrets Manager

### Layer 4: HIPAA Compliance
```
Audit Logging
├─ All PHI access logged
├─ Timestamp, user, IP, action
├─ Immutable audit trail (stored in separate DB)
└─ 6-year retention policy

Access Logs
├─ Failed login attempts (temp lock after 5 attempts)
├─ Permission denied events
├─ Data export requests
└─ Cross-border access flags

Incident Response
├─ Breach detection rules (PII exfiltration patterns)
├─ Auto-notification to security team
├─ Breach impact assessment
└─ Patient notification within 60 days
```

## Database Schema Highlights

### Global Hospitals Table
```sql
GlobalHospital
├─ Accreditation (JCI, NABH status)
├─ Geographic (lat/long with GiST index)
├─ Quality Metrics (success_rate, complication_rate, readmission_rate)
├─ Price Data Source (HHS, EHDS, ABDM, self-report)
└─ Full-text search index on (name, city, specialization)
```

### Price Normalizer (CPT ↔ ICD-10 ↔ UHI)
```sql
PriceNormalizer
├─ CPT Code (e.g., 27447 = Total Knee Replacement)
├─ ICD-10 Code (e.g., M17.11 = Primary OA, right knee)
├─ UHI Code (e.g., SURG-1001 for India)
├─ EHDS Identifier (for Europe)
└─ Complexity Score (1-10 for risk adjustment)

ProcedurePrice
├─ Hospital-specific pricing
├─ Base price + facility + anesthesia + surgeon fees
├─ Success/complication rates (outcome data)
└─ Source validation (verified_at, data_source)
```

### Recovery Bridge Schema
```sql
RecoverySession (30-day monitoring window)
├─ booking_id (FK to HospitalBooking)
├─ assigned_surgeon_id (FK to Surgeon)
├─ assigned_provider_id (FK to RecoveryProvider)
├─ start_date → end_date (auto +30 days)
└─ recovery_status (ACTIVE/PAUSED/COMPLETED/ESCALATED)

RecoveryVital (time-series wearable data)
├─ heart_rate, blood_oxygen_spo2, temperature, BP, RR
├─ device_id (anonymized wearable)
├─ alert_trigger (boolean, computed at ingestion)
└─ collected_at (measurement timestamp)

RecoveryAlert (triggered alerts)
├─ alert_type (HIGH_FEVER, RAPID_HR, LOW_SPO2, etc.)
├─ severity (INFO/WARNING/CRITICAL)
├─ patient_value vs normal_range
├─ recommendation (clinical guidance)
└─ escalation tracking (acknowledged_by, action_taken)
```

### Rural Financing Schema
```sql
RuralFinancing
├─ Financing Type (UPI_MICRO_LOAN, HEALTH_EMI, SUBSIDY_GRANT, INSURANCE)
├─ UPI Transaction ID (for NPCI reference)
├─ Principal Amount + Currency
├─ Interest Rate (rural subsidy: 0-4% vs urban: 8-12%)
├─ Tenure (3/6/12/24 months)
├─ EMI Schedule (JSON: [{due_date, amount, status}, ...])
├─ Payment Tracking (total_paid, next_due_date)
└─ Status Workflow (PENDING → APPROVED → DISBURSED → PAYING → COMPLETED)
```

## Performance Optimization

### Query Optimization
```sql
-- Hospital Search (geo-spatial + rating)
SELECT * FROM GlobalHospital
WHERE country_code = 'IN'
  AND ST_DWithin(
    ST_MakePoint(longitude, latitude)::geography,
    ST_MakePoint(-73.935242, 40.730610)::geography,
    50000  -- 50km radius
  )
  AND is_active = true
LIMIT 20;

-- Index: CREATE INDEX idx_hospital_geo ON GlobalHospital 
--        USING GIST(ST_MakePoint(longitude, latitude)::geography);
```

### Caching Strategy
- **5 min**: Hospital search results (user-specific)
- **1 hour**: Price comparisons (global)
- **1 day**: Hospital accreditation status
- **Real-time**: Recovery vitals (no caching)
- **Cache invalidation**: On price update or booking

### Connection Pooling
- **PgBouncer** (PostgreSQL): 100 client connections → 20 server connections
- **Redis connection pool**: Max 50 connections
- **API server threads**: 4 × CPU cores (auto-scaled)

## Monitoring & Observability

### Metrics Collected
```
Application Metrics
├─ Request latency (p50, p95, p99)
├─ Error rate (by endpoint)
├─ Database query performance
├─ Cache hit ratio
└─ Authorization failures

Business Metrics
├─ Booking conversion rate
├─ Average procedure cost (by hospital)
├─ Recovery completion rate
├─ Financing approval rate
└─ Patient satisfaction (NPS)

Compliance Metrics
├─ HIPAA audit log completeness
├─ Data encryption coverage (%)
├─ GDPR deletion requests processed
└─ Access control violations
```

### Alerting
```
Critical (Page Oncall)
├─ API error rate > 5%
├─ Database connection pool > 90%
├─ Recovery alert response time > 2 min
└─ PHI exposure detected

Warning (Slack #evijnar-alerts)
├─ API latency p99 > 500ms
├─ Cache hit ratio < 60%
├─ Slow queries (> 1s)
└─ Unauthorized access attempts > 10/min
```

## Deployment Architecture

### Environment Progression
```
Development
├─ docker-compose locally
├─ Postgres 16 + Redis 7
└─ Hot reload enabled

Staging
├─ AWS ECS on t3.medium
├─ RDS PostgreSQL (db.t3.small, Multi-AZ)
├─ ElastiCache Redis
└─ CloudFront CDN + WAF

Production
├─ AWS ECS Fargate (auto-scaling: 2-10 tasks)
├─ RDS PostgreSQL (db.r5.large, Multi-AZ + Read Replicas)
├─ ElastiCache Redis Cluster (3-node)
├─ S3 for static assets
├─ CloudFront for CDN
├─ Route53 for DNS
└─ Secrets Manager for sensitive configs
```

---

**Last Updated**: 2026-04-08  
**Version**: 0.1.0 (Sprint 1 Complete)
