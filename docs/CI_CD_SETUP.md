# GitHub Actions CI/CD Integration Guide

## Overview

Evijnar's CI/CD pipeline automatically runs Phase 3 integration tests, code quality checks, and coverage reports using GitHub Actions. The pipeline uses a **hybrid strategy**:

- **Fast CI (ci-fast.yml)**: Runs on every push - lint, type check, format validation (~2 min)
- **Full CI (ci-full.yml)**: Runs on PRs to main and main branch - Phase 3 tests with PostgreSQL (~10 min)
- **Coverage (coverage.yml)**: Runs on main merges - uploads to Codecov (~2 min)

## Workflows

### 1. Fast CI Workflow (ci-fast.yml)

**Trigger**: Every push to any branch

**What it does**:
```
On push:
├── Lint with ruff (catches syntax/import issues)
├── Type check with mypy (catches type errors)
└── Format check with black (ensures consistent style)
```

**Duration**: ~2 minutes

**Why**: Give developers immediate feedback before full test suite runs

**Failure**: PR shows ❌ on GitHub, but doesn't block merging (informational)

### 2. Full CI Workflow (ci-full.yml)

**Trigger**: 
- Pull request to `main` branch
- Push to `main` branch

**What it does**:
```
On PR/push to main:
├── Set up Python 3.11
├── Start PostgreSQL 16 service (GitHub Actions managed)
├── Install dependencies from pyproject.toml
├── Run Alembic migrations (set up schema)
├── Run Phase 3 integration tests
│   ├── TestIntegrationEndToEnd (5 tests)
│   ├── TestIdempotency (2 tests)
│   ├── TestTransactionAtomicity (1 test)
│   └── TestConcurrentIngestion (2 tests)
├── Run database verification (verify_data.py)
├── Generate coverage report (HTML + XML)
├── Upload coverage to Codecov
└── Archive coverage artifacts (7 day retention)
```

**Duration**: ~10-15 minutes

**Why**: Real PostgreSQL ensures data layer works, full test suite validates entire ingestion pipeline

**Failure**: PR shows ❌, blocks merging (required status check)

**Success Output**:
- ✅ All 10+ tests passed
- Coverage report in artifacts
- Codecov comment on PR showing coverage %

### 3. Coverage Workflow (coverage.yml)

**Trigger**: Push to `main` branch only

**What it does**:
```
On main merge:
├── Download coverage artifacts from ci-full
├── Generate coverage badge (SVG)
├── Upload to Codecov
└── Comment on related PRs with coverage impact
```

**Duration**: ~2 minutes

**Why**: Track coverage over time, inform reviewers of coverage changes

## PostgreSQL Service Configuration

The full CI workflow starts a PostgreSQL 16 service automatically:

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: evijnar_test
    options:
      --health-cmd pg_isready          # Health check
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432
```

**Connection String**: `postgresql+asyncpg://postgres:postgres@localhost:5432/evijnar_test`

## Configuration Files

### pytest.ini

```ini
[pytest]
testpaths = tests
asyncio_mode = auto
timeout = 300
```

Configures pytest to:
- Discover tests in `tests/` directory
- Enable async test support (pytest-asyncio)
- Set 5-minute timeout per test
- Generate coverage reports

### pyproject.toml

Added sections:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
timeout = 300

[tool.coverage.run]
source = ["app"]

[tool.coverage.report]
precision = 2
```

## Setting Up GitHub Secrets

For the workflows to work, configure these GitHub Secrets in your repository:

### Required Secrets

1. **CODECOV_TOKEN** (optional but recommended)
   - Get from https://codecov.io/gh/your-org/Evijnar
   - Used for coverage report uploads
   - Leave empty to skip Codecov upload

### Optional Secrets

These are not required for Phase 3 tests but may be needed later:

- `EVIJNAR_AI_KB_URL` - Optional remote knowledge base for Evijnar Health AI mapping
- `SECRET_KEY` - JWT secret for authentication tests
- `DATABASE_URL` - Custom database URL (default provided in workflow)

**To add secrets**:
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Enter name (e.g., `CODECOV_TOKEN`) and value
4. Save

## How the Pipeline Works

### On Every Push (Branch)
```mermaid
push → ci-fast.yml
          ├── Lint ✅
          ├── Type check ✅
          └── Format check ✅
          
Result: ~2 min, shows on PR but doesn't block
```

### On PR to Main
```mermaid
PR → ci-fast.yml (runs) ✅
   ↓
PR → ci-full.yml (runs)
     ├── PostgreSQL starts
     ├── Migrations run
     ├── Phase 3 tests run
     ├── Coverage generated
     └── Codecov upload
     
Result: ~10-15 min, shows on PR, BLOCKS merge if fails
```

### On Merge to Main
```mermaid
merge → ci-full.yml ✅
     ↓
merge → coverage.yml
        ├── Codecov upload
        ├── Badge generated
        └── Summary comment
        
Result: Coverage tracked over time
```

## Viewing Results

### GitHub Actions Tab
1. Go to repository → "Actions" tab
2. See all workflow runs
3. Click on a run to see details
4. Click on a job to see logs

### On Pull Requests
1. Go to pull request page
2. Scroll to "Checks" section
3. See status of all workflows
4. Click "Details" to see full output
5. Codecov posts comment: "Coverage is 85% (↑2%)"

### Coverage Reports
1. Download "coverage-report" artifact from ci-full job
2. Extract and open `htmlcov/index.html` in browser
3. View line-by-line coverage

## Troubleshooting

### Tests Fail with "Database connection refused"
**Cause**: PostgreSQL service didn't start properly
**Fix**: 
- Check if PostgreSQL startup logs show errors
- Increase health check timeout in workflow
- Verify database credentials match in test code

### Tests Timeout
**Cause**: Tests taking longer than 300 seconds
**Fix**:
- Increase timeout in pytest.ini
- Optimize slow tests
- Run individual test groups to isolate slow tests

### Coverage Not Uploading to Codecov
**Cause**: CODECOV_TOKEN not set or invalid
**Fix**:
- Set CODECOV_TOKEN secret in GitHub repo settings
- Verify token matches at https://codecov.io

### Workflow Errors with "Permission denied"
**Cause**: Git permissions issue
**Fix**:
- Ensure GitHub token has `contents: write` permission
- Check `.github/workflows/` directory exists and is committed

### Environment Variables Not Found
**Cause**: Secrets not set or typo in secret name
**Fix**:
```bash
# Verify secret exists in GitHub Settings → Secrets
# Check workflow uses correct secret name:
env:
  CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

## Customization

### Disable Codecov Upload
Edit `.github/workflows/ci-full.yml`:
```yaml
- name: Upload coverage reports to Codecov
  if: false  # Disable
```

### Change Trigger Events
Edit workflow file, change `on:` section:
```yaml
on:
  push:
    branches: ["develop", "staging"]  # Add more branches
  pull_request:
    branches: ["main"]
```

### Add Custom Environment Variables
Edit workflow, add to `env:` section:
```yaml
env:
  CUSTOM_VAR: value
  ANOTHER_VAR: ${{ secrets.SECRET_NAME }}
```

### Increase Build Timeout
Edit `.github/workflows/ci-full.yml`:
```yaml
jobs:
  integration-tests:
    timeout-minutes: 30  # Default is 360 (6 hours)
```

## Best Practices

1. **Branch Protection**: Enable "Require status checks to pass" for ci-full workflow on main branch
2. **Code Review**: Require PR approval after tests pass
3. **Coverage Targets**: Set minimum coverage % requirement (e.g., 80%)
4. **Logs**: Keep workflow runs for debugging (default: 90 days)
5. **Secrets**: Rotate tokens regularly, never commit secrets

## Monitoring & Alerts

### Set Up Email Notifications
1. Go to GitHub repo → Settings → Notifications
2. Enable "Email notification for workflow runs"
3. Choose when to be notified (always, on failure, etc.)

### Slack Integration
1. Create Slack workflow in your workspace
2. Add GitHub integration
3. Subscribe to repository notifications

### Badge in README
Add coverage badge to README:
```markdown
[![codecov](https://codecov.io/gh/your-org/Evijnar/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/Evijnar)
```

## Performance

| Workflow | Duration | Trigger | Cost |
|----------|----------|---------|------|
| ci-fast | ~2 min | Every push | Fast feedback |
| ci-full | ~10 min | PR/main | Full validation |
| coverage | ~2 min | Main only | Tracking |

**Total**: ~14 min worst case (all three run on main merge)

**Cost**: GitHub Actions free tier includes 2,000 minutes/month for private repos

## Deployment Integration (Future)

These workflows can trigger deployment to staging/production:
```yaml
deploy-staging:
  needs: [ci-full]  # Wait for tests to pass
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  # ... deployment steps
```

## Related Documentation

- [Phase 3 Testing Guide](docs/PHASE3_TESTING.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.io/)

## Support

For CI/CD issues:
1. Check GitHub Actions logs for error messages
2. Review workflow YAML syntax
3. Test locally with `pytest tests/test_integration_phase3.py -v`
4. Verify PostgreSQL is running: `psql -U postgres -c "SELECT version();"`
