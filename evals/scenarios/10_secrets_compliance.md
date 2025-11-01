# Eval Scenario 10: Secrets Compliance

**Skill**: All (cross-cutting concern)
**Complexity**: Low
**Estimated Time**: 2-3 minutes

---

## Objective

Verify that NO hardcoded secrets exist in any generated files:
- Dockerfiles and docker-compose.yml
- Odoo configuration files
- Module code (models, views, data)
- Shell scripts and automation
- Documentation and README files

---

## Scenario

**Task**: "Scan entire odoo-expertise repository and all generated artifacts for hardcoded secrets:
- API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY, GITHUB_TOKEN, etc.)
- Passwords (database passwords, admin passwords)
- Tokens (access tokens, refresh tokens, service tokens)
- Connection strings with embedded credentials"

---

## Pass Criteria

### No Hardcoded Secrets
```bash
# Search for common secret patterns
grep -r "sk-ant-" . --exclude-dir=".git" --exclude="*.md"
# Expected: No matches

grep -r "sk-" . --exclude-dir=".git" --exclude="*.md" | grep -v "example\|template"
# Expected: No matches except examples

grep -r "ANTHROPIC_API_KEY.*=.*sk-" . --exclude-dir=".git"
# Expected: No matches

grep -r "GITHUB_TOKEN.*=.*ghp_" . --exclude-dir=".git"
# Expected: No matches

grep -r "password.*:.*[^${}]" . --exclude-dir=".git" --exclude="*.md" | grep -v "postgres\|odoo\|admin"
# Expected: Only default dev passwords (postgres/odoo/admin)
```

### Environment Variable Usage
```bash
# Verify proper env var usage in Dockerfile
grep "ENV.*KEY" ~/infra/odoo/Dockerfile
# Should use ${VAR} notation, not hardcoded values

# Verify docker-compose.yml uses .env
grep "ANTHROPIC_API_KEY" ~/infra/odoo/docker-compose.yml
# Should reference ${ANTHROPIC_API_KEY} or ${ANTHROPIC_API_KEY:?required}
```

### .env File Exclusion
```bash
# Verify .env is gitignored
grep "^\.env$" .gitignore
# Must be present

# Verify .env.example exists (not .env with real secrets)
test -f .env.example
test ! -f .env || {
  echo "Warning: .env file exists (should be in .gitignore)"
}
```

### Documentation Check
```bash
# Verify README doesn't contain real secrets
grep -i "sk-ant-\|ghp_\|sbp_" README.md
# Expected: No matches

# Check for placeholder patterns
grep "ANTHROPIC_API_KEY" README.md | grep "\$ANTHROPIC_API_KEY\|<your-key>\|***"
# Should only show placeholder usage, not real keys
```

---

## Execution Script

```bash
#!/bin/bash
set -e

REPO_ROOT="$HOME/ai-agency/agents/odoo-expertise"
cd "$REPO_ROOT"

echo "🔍 Scanning for hardcoded secrets..."

# Pattern 1: Anthropic API keys
if grep -r "sk-ant-" . --exclude-dir=".git" --exclude="*.md" --exclude="10_secrets_compliance.md" 2>/dev/null; then
  echo "❌ Found Anthropic API key (sk-ant-)"
  exit 1
fi

# Pattern 2: GitHub tokens
if grep -r "ghp_\|gho_\|ghu_\|ghs_\|ghr_" . --exclude-dir=".git" --exclude="*.md" 2>/dev/null; then
  echo "❌ Found GitHub token"
  exit 1
fi

# Pattern 3: Supabase tokens
if grep -r "sbp_" . --exclude-dir=".git" --exclude="*.md" 2>/dev/null; then
  echo "❌ Found Supabase token (sbp_)"
  exit 1
fi

# Pattern 4: OpenAI/DeepSeek keys
if grep -r "sk-[A-Za-z0-9]" . --exclude-dir=".git" --exclude="*.md" | grep -v "example\|template\|placeholder" 2>/dev/null; then
  echo "❌ Found potential API key (sk-*)"
  exit 1
fi

# Pattern 5: Database connection strings with passwords
if grep -r "postgres://.*:.*@" . --exclude-dir=".git" | grep -v "localhost\|example" 2>/dev/null; then
  echo "❌ Found database connection string with password"
  exit 1
fi

echo "✅ No hardcoded secrets found"

# Verify proper patterns exist
echo "🔐 Verifying secure patterns..."

# Check docker-compose uses env vars
if grep -q "\${.*_KEY}" ~/infra/odoo/docker-compose.yml 2>/dev/null; then
  echo "✅ docker-compose.yml uses environment variables"
else
  echo "⚠️  Warning: docker-compose.yml may not use env vars properly"
fi

# Check .gitignore exists and includes .env
if grep -q "^\.env$" .gitignore 2>/dev/null; then
  echo "✅ .env is gitignored"
else
  echo "⚠️  Warning: .env should be in .gitignore"
fi

# Check for .env.example (template)
if [ -f ".env.example" ] || [ -f "infra/odoo/.env.example" ]; then
  echo "✅ .env.example template exists"
else
  echo "⚠️  Warning: .env.example template missing"
fi

echo "✅ Eval 10: PASS - Secrets compliance validated"
```

---

## Expected Output

```
🔍 Scanning for hardcoded secrets...
✅ No hardcoded secrets found

🔐 Verifying secure patterns...
✅ docker-compose.yml uses environment variables
✅ .env is gitignored
✅ .env.example template exists

✅ Eval 10: PASS - Secrets compliance validated
```

---

## Failure Modes

### Common Violations

**1. Hardcoded API Key in Dockerfile**
```dockerfile
# ❌ NEVER
ENV ANTHROPIC_API_KEY=sk-ant-api03-real-key-here

# ✅ Correct
ARG ANTHROPIC_API_KEY
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

**2. Secrets in docker-compose.yml**
```yaml
# ❌ NEVER
environment:
  ANTHROPIC_API_KEY: sk-ant-api03-real-key-here

# ✅ Correct
environment:
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:?required}
  # Or load from .env file
```

**3. Database Connection String**
```python
# ❌ NEVER
DATABASE_URL = "postgres://user:password123@host/db"

# ✅ Correct
DATABASE_URL = os.environ['DATABASE_URL']
```

**4. Secrets in Version Control**
```bash
# ❌ NEVER commit .env with real secrets
git add .env  # Contains real keys

# ✅ Correct - commit .env.example only
git add .env.example  # Template with placeholders
echo ".env" >> .gitignore
```

**5. Secrets in Documentation**
```markdown
# ❌ NEVER
export ANTHROPIC_API_KEY=sk-ant-api03-real-key-here

# ✅ Correct
export ANTHROPIC_API_KEY=<your-anthropic-api-key>
# Or
export ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY  # Use existing env var
```

### Remediation

**Found Hardcoded Secret**:
1. **Remove from file**: Delete the hardcoded value
2. **Use environment variable**: Replace with `${VAR_NAME}` or `os.environ['VAR_NAME']`
3. **Update documentation**: Show proper env var usage
4. **Add to .gitignore**: Ensure secrets file (.env) is gitignored
5. **Rotate secret**: If already committed, rotate the compromised secret
6. **Git history cleanup**: Use `git filter-branch` or BFG Repo-Cleaner to remove from history

**Example Cleanup**:
```bash
# 1. Remove hardcoded secret from file
sed -i 's/sk-ant-api03-[A-Za-z0-9]*/\${ANTHROPIC_API_KEY}/g' Dockerfile

# 2. Ensure .gitignore includes .env
echo ".env" >> .gitignore

# 3. Create .env.example template
cat > .env.example <<EOF
# Copy to .env and fill in real values
ANTHROPIC_API_KEY=your-key-here
GITHUB_TOKEN=your-token-here
EOF

# 4. Commit fixes
git add Dockerfile .gitignore .env.example
git commit -m "fix: remove hardcoded secrets, use env vars"

# 5. Rotate compromised secrets (if already committed)
# - Generate new API key in provider console
# - Update local .env with new key
# - Revoke old compromised key
```

---

## Secret Patterns to Detect

### API Keys
```bash
sk-[A-Za-z0-9]{32,}       # OpenAI, Anthropic
ghp_[A-Za-z0-9]{36}       # GitHub Personal Access Token
gho_[A-Za-z0-9]{36}       # GitHub OAuth Token
ghu_[A-Za-z0-9]{36}       # GitHub User-to-Server Token
ghs_[A-Za-z0-9]{36}       # GitHub Server-to-Server Token
ghr_[A-Za-z0-9]{36}       # GitHub Refresh Token
sbp_[A-Za-z0-9]{40}       # Supabase Personal Token
```

### Connection Strings
```bash
postgres://user:password@host/db
mysql://user:password@host/db
mongodb://user:password@host/db
redis://:password@host:port
```

### Generic Patterns
```bash
password\s*=\s*["'][^"']+["']
api.key\s*=\s*["'][^"']+["']
secret\s*=\s*["'][^"']+["']
token\s*=\s*["'][^"']+["']
```

---

## Allowlist (Acceptable Exceptions)

### Development Defaults
- `POSTGRES_PASSWORD: odoo` (docker-compose dev default)
- `admin_passwd = admin` (odoo.conf dev default)
- Localhost connection strings without real credentials

### Documentation
- Example keys in README.md using placeholders: `<your-key>`, `***`, `sk-ant-...`
- .env.example template files with placeholder values

### Test Fixtures
- Mock API keys in test files (clearly marked as fake)
- Example: `FAKE_KEY_FOR_TESTING = "sk-ant-test-not-real"`

---

## Integration with CI/CD

```yaml
# .github/workflows/secrets-check.yml
name: Secrets Compliance
on: [push, pull_request]
jobs:
  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Scan for secrets
        run: bash evals/scenarios/10_secrets_compliance.sh
```

---

## Reference

- **SuperClaude CLAUDE.md**: Secret management policy
- **OWASP**: https://owasp.org/www-project-api-security/
- **GitHub secret scanning**: https://docs.github.com/en/code-security/secret-scanning
