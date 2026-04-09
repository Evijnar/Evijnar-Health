# GitHub Branch Protection & Repository Security Configuration

This guide explains how to configure GitHub repository settings for maximum security.

---

## 📋 Branch Protection Rules

### Setup Instructions

1. Navigate to: **Settings → Branches → Add rule**
2. Branch name pattern: `main` (or `master`)
3. Enable the following:

### Required Settings

#### ✅ Require a Pull Request Before Merging

- [x] **Require pull request reviews before merging**
  - Number of approvals: `2` (minimum for production)
- [x] **Require approval of the most recent reviewable push**
- [x] **Dismiss stale pull request approvals when new commits are pushed**
- [x] **Require review from Code Owners**

#### ✅ Require Status Checks to Pass

- [x] **Require branches to be up to date before merging**
- [x] **Require status checks to pass before merging**

**Status Checks to Enable:**
- `build` (CI/CD pipeline)
- `test` (unit & integration tests)
- `security-scan` (Bandit, Trivy, SAST)
- `dependencies` (npm audit, pip audit)

#### ✅ Require Code Scanning Results

- [x] **Require code scanning results before merging**
- [x] **Require security scanning results before merging**

#### ✅ Enforce Restrictions

- [x] **Include administrators**
- [x] **Restrict who can push to matching branches**
  - Only allow: `Main Development Team`
- [x] **Allow auto-merge**
  - Only: Rebase and merge (prevents merge commits)

#### ✅ Require Signed Commits

- [x] **Require commits to be signed and verified**

---

## 🔐 Repository General Settings

### Access Control

**Location:** Settings → Access → Collaborators and teams

1. **Add Team**
   - Team: `@org/developers`
   - Role: `Write`

2. **Add Team**
   - Team: `@org/security-team`
   - Role: `Admin`

3. **Restrict Push Access**
   - Only allow `main` branch pushes from security team

### Visibility

**Location:** Settings → General

- [x] **Make repository PRIVATE** (Recommended for healthcare data)
- Code visibility: `Private`
- Allow forking: `Disabled` (to prevent accidental public forks)

### Default Branch

**Location:** Settings → General

- Default branch: `main`
- Auto-rename old `master` branch: Yes

---

## 🛡️ Security Settings

### Vulnerability Management

**Location:** Security → Code security and analysis

- [x] **Enable Dependabot**
  - Alerts: On
  - Security updates: On
  - Version updates: On (optional)

- [x] **Enable Secret Scanning**
  - Push protection: On (prevents accidental commits)

- [x] **Enable Security Overview**
  - View all vulnerabilities across the org

### Code Scanning

**Location:** Security → Code security and analysis

- [x] **Enable CodeQL analysis**
  - Default configuration or custom `.github/workflows/codeql.yml`

---

## 🚀 GitHub Actions Permissions

**Location:** Settings → Actions → General

### Workflow Permissions

- [x] **GitHub Token Permissions**
  - Read and write: (default - allowed for deployments)

### Secrets and Variables

**Location:** Settings → Secrets and variables → Actions

**Important: Configure at ORGANIZATION level, not repository level**

See `docs/GITHUB_SECRETS_SETUP.md` for detailed secrets configuration.

---

## 📊 Webhook & Notifications

### Add Branch Protection Webhook

**Location:** Settings → Webhooks

Optional: Send notifications on branch protection violations

```json
{
  "Payload URL": "https://your-webhook.example.com/github",
  "Content type": "application/json",
  "Events": [
    "Push",
    "Pull request",
    "Status"
  ]
}
```

---

## ✅ Security Checklist

### Before Making Repository Public

- [ ] All secrets are in GitHub Organization Secrets
- [ ] No `.env` files with actual values are committed
- [ ] Branch protection rules are enforced
- [ ] Code scanning is enabled
- [ ] Dependabot is enabled
- [ ] Secret scanning is enabled
- [ ] CODEOWNERS file exists
- [ ] SECURITY.md is created
- [ ] All API keys are rotated
- [ ] Database credentials are not in code

### Before Each Release

- [ ] Run full security scan
- [ ] Review all dependencies for vulnerabilities
- [ ] Update security headers
- [ ] Check encryption keys are rotated
- [ ] Verify audit logging is enabled
- [ ] Test disaster recovery procedures

---

## 📄 CODEOWNERS File

Create `.github/CODEOWNERS` to automatically require specific teams to review code:

```
# Global owners
* @org/security-team

# API code
/apps/api/ @org/backend-team @org/security-team

# Frontend code
/apps/web/ @org/frontend-team

# Database schemas
/packages/database/ @org/database-team @org/security-team

# Security files
/.github/ @org/security-team
/SECURITY.md @org/security-team
/docs/ @org/documentation-team
```

---

## 🔄 Deployment Protection Rules

For production deployments, add additional requirements:

**Location:** Settings → Environments → Production

### Environment Protection Rules

- [x] **Required reviewers**
  - Number: `2`
  - Reviewers: `@org/deployment-team`

- [x] **Deployment branches**
  - Selected branches: `main` only

- [x] **Custom deployment protection rules**
  - Require successful security scan
  - Require signed commits
  - Require PR approval

---

## 🚨 Security Alerts

### Configure Branch Alerts

**Location:** Security → Code security analysis

Subscribe to:
- [ ] Dependabot alerts
- [ ] Secret scanning alerts
- [ ] CodeQL alerts
- [ ] Custom webhooks

### Alert Actions

Automatically:
- Create issues on vulnerabilities
- Assign to security team
- Set priority based on severity
- Link to JIRA/Linear tickets

---

## 📋 Audit Log Review

**Location:** Organization Settings → Audit log

Regular review schedule:
- [ ] Daily: Unusual access patterns
- [ ] Weekly: Security-related changes
- [ ] Monthly: Access review
- [ ] Quarterly: Full audit

Monitor for:
- Unauthorized access attempts
- Branch protection changes
- Secrets access
- Unusual deployments

---

## 🔐 GitHub App Integrations

### Recommended Security Apps

1. **Snyk**
   - Continuous vulnerability scanning
   - Automatic remediation PRs

2. **WhiteSource**
   - Dependency management
   - License compliance

3. **SonarQube**
   - Code quality analysis
   - Security issues detection

### Installation

1. Go to Organization Settings
2. Select GitHub Apps
3. Search for app name
4. Click "Install"
5. Configure permissions (principle of least privilege)

---

## 🚀 Auto-Remediation Workflow

Create `.github/workflows/security-auto-fix.yml`:

```yaml
name: Security Auto-Fix

on:
  push:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run security checks
        run: |
          bandit -r apps/api/
          npm audit
          pip audit
      
      - name: Create remediation PR
        if: failure()
        uses: peter-evans/create-pull-request@v4
        with:
          title: "[SECURITY] Auto-fix security issues"
          body: "This PR contains automatic security fixes"
          branch: security/auto-fix
```

---

## 📞 Support & Escalation

### Security Issue Found

1. Do NOT open public issue
2. Report to `@org/security-team`
3. Verify fix in staging
4. Deploy with expedited process
5. Document in post-mortem

### False Positives

If security tools flag false positives:

1. Verify finding manually
2. Document why it's a false positive
3. Suppress in configuration
4. Create test case

---

## 📅 Maintenance Schedule

- **Daily**: Review GitHub Actions logs
- **Weekly**: Check Dependabot alerts
- **Monthly**: Audit branch protection rules
- **Quarterly**: Security review and key rotation
- **Annually**: Complete security audit

---

Last Updated: 2026-04-09
