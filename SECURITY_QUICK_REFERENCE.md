# Evijnar Security Quick Reference

## 🔐 For Developers

### Setup New Dev Environment
```bash
git clone https://github.com/org/evijnar.git
cd evijnar
./setup.sh
pre-commit install
```

### Before Committing
```bash
# Pre-commit hooks run automatically
# These commands verify everything:
pre-commit run --all-files
npm audit
pip audit
```

### ⛔ NEVER Commit
```
.env (actual values)
.env.production
*.pem, *.key files
*-credentials.json
service-account-key.json
docker-compose.override.yml
```

### ✅ DO Commit
```
.env.example (template only)
.pre-commit-config.yaml
.github/workflows/
SECURITY.md
docs/ENV_SETUP.md
```

### If You See Secret in Commit
```bash
# 1. DO NOT PUSH
# 2. Report to security team immediately
# 3. Secret must be rotated
# 4. Force push (only after security approval)
```

---

## 🔑 For DevOps/Admins

### Create GitHub Organization Secrets
```
GitHub Settings → Secrets and variables → Actions

Required secrets (11):
✓ DB_PASSWORD
✓ DATABASE_URL
✓ SECRET_KEY
✓ JWT_SECRET
✓ ENCRYPTION_KEY_PATIENT_DATA
✓ ENCRYPTION_KEY_PHARMA_DATA
✓ ANTHROPIC_API_KEY
✓ TWILIO_ACCOUNT_SID
✓ TWILIO_AUTH_TOKEN
✓ GOOGLE_MAPS_API_KEY
✓ HIPAA_AUDIT_WEBHOOK_URL
```

### Set Up Branch Protection
```
Settings → Branches → Add Rule (main)

✓ Require 2 pull request reviews
✓ Require signed commits
✓ Require status checks to pass
✓ Include administrators
✓ Restrict push access
```

### Enable Security Features
```
Settings → Code security and analysis

✓ Dependabot alerts: ON
✓ Secret scanning: ON
✓ Secret scanning (push protection): ON
✓ CodeQL analysis: ON
```

---

## 🚨 Security Events Response

### If Secret Leaked
```
1. 🛑 STOP all work
2. 📞 Call security team
3. 🔄 Rotate compromised secret immediately
4. 🔍 Audit logs for unauthorized access
5. 📝 Document incident
6. 🚀 Patch & deploy fix
```

### If Security Scan Fails
```
1. Review GitHub Actions logs
2. Check Bandit/CodeQL findings
3. Fix issues locally
4. Re-run: pre-commit run --all-files
5. Push fix + retry CI/CD
```

### If Deployment Blocked
```
1. Check required status checks
2. All security jobs must pass
3. Require 2 reviews + signed commits
4. Contact security team if stuck
```

---

## 📋 Monthly Checklist

- [ ] Review GitHub Actions logs
- [ ] Check Dependabot alerts
- [ ] Verify no secrets in recent commits
- [ ] Audit GitHub access logs
- [ ] Review branch protection settings

---

## 📅 Quarterly Tasks

- [ ] Rotate all API keys & database passwords
- [ ] Rotate JWT/Secret keys
- [ ] Rotate encryption keys
- [ ] Security training for team
- [ ] Audit log review & analysis

---

## 🔗 Documentation Links

- **Setup**: `docs/ENV_SETUP.md`
- **Secrets**: `docs/GITHUB_SECRETS_SETUP.md`
- **GitHub**: `docs/GITHUB_SECURITY_CONFIG.md`
- **Policies**: `SECURITY.md`
- **Implementation**: `SECURITY_IMPLEMENTATION.md`

---

## 🆘 Quick Troubleshooting

**Q: Pre-commit hook fails**
```
A: Run: pre-commit run --all-files
   Fix issues locally, then retry commit
```

**Q: CI/CD fails with "secret not found"**
```
A: Check GitHub Organization Secrets
   Ensure secret name matches exactly
   Wait 1 minute for caching to clear
```

**Q: Can't commit due to pre-commit**
```
A: Normal! Hooks prevent secrets
   Fix detected issues
   If bypass needed: git commit --no-verify
   (But why? Check SECURITY.md first)
```

**Q: .env file accidentally committed**
```
A: 🚨 EMERGENCY PROCEDURE
   1. Don't push!
   2. Rotate all secrets immediately
   3. Contact security team
   4. Force push after cleanup
```

---

## 📞 Contact

- **Security Issues**: [security@org.com]
- **On-Call**: [pagerduty link]
- **Slack**: #security-team

---

**Last Updated**: April 9, 2026  
**Next Review**: July 9, 2026
