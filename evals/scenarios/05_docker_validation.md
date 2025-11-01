# Eval Scenario 05: Docker Image Validation

**Skill**: odoo-docker-claude
**Complexity**: High
**Estimated Time**: 5-8 minutes (includes build time)

---

## Objective

Validate Docker image meets production requirements:
- Multi-stage build with minimal size
- wkhtmltopdf rendering works correctly
- Fonts installed (Noto, DejaVu)
- Non-root user (uid 1000)
- Anthropic Python SDK installed
- No hardcoded secrets

---

## Scenario

**Task**: "Build the Odoo Docker image from ~/infra/odoo/Dockerfile and validate:
1. Image builds successfully
2. wkhtmltopdf can render a test PDF
3. Fonts render correctly in PDF
4. Image runs as non-root user
5. Anthropic SDK is importable
6. No secrets hardcoded in image"

---

## Pass Criteria

### Build Success
```bash
cd ~/infra/odoo
docker build -t odoo-test:latest -f Dockerfile .
# Exit code 0 = pass
```

### Image Size Check
```bash
IMAGE_SIZE=$(docker images odoo-test:latest --format "{{.Size}}")
# Should be <2GB for production viability
# Warning if >2GB, fail if >3GB
```

### wkhtmltopdf Validation
```bash
# Run container and test wkhtmltopdf
docker run --rm odoo-test:latest wkhtmltopdf --version
# Output should show version (e.g., "wkhtmltopdf 0.12.6")

# Test PDF generation
docker run --rm odoo-test:latest sh -c "
  echo '<h1>Test PDF</h1><p>Hello World</p>' > /tmp/test.html
  wkhtmltopdf /tmp/test.html /tmp/test.pdf
  ls -lh /tmp/test.pdf
"
# Should create non-zero size PDF file
```

### Font Rendering Check
```bash
# Verify fonts are installed
docker run --rm odoo-test:latest fc-list | grep -i "noto\|dejavu"
# Should show multiple font families

# Test font rendering in PDF
docker run --rm odoo-test:latest sh -c "
  echo '<html><body style=\"font-family: Noto Sans\"><h1>Unicode: 你好 العالم ┼─┤</h1></body></html>' > /tmp/test_fonts.html
  wkhtmltopdf /tmp/test_fonts.html /tmp/test_fonts.pdf
  ls -lh /tmp/test_fonts.pdf
"
# PDF should be created and contain unicode characters
```

### Non-Root User Check
```bash
# Verify image runs as non-root
USER_ID=$(docker run --rm odoo-test:latest id -u)
test "$USER_ID" = "1000"
# Must return uid 1000 (odoo user)

# Verify user name
USER_NAME=$(docker run --rm odoo-test:latest whoami)
test "$USER_NAME" = "odoo"
```

### Anthropic SDK Check
```bash
# Verify SDK is installed and importable
docker run --rm odoo-test:latest python3 -c "
import anthropic
print(f'Anthropic SDK version: {anthropic.__version__}')
assert anthropic.__version__ >= '0.36.0'
"
# Should print version and not raise ImportError
```

### Secrets Compliance Check
```bash
# Scan Dockerfile for hardcoded secrets
grep -i "api.key\|password\|secret\|token" ~/infra/odoo/Dockerfile
# Should find NO matches (empty result = pass)

# Verify ENV vars are not hardcoded
grep -E "ENV.*(KEY|PASSWORD|SECRET|TOKEN)" ~/infra/odoo/Dockerfile | grep -v "ENV DEBIAN_FRONTEND"
# Should find NO matches except whitelisted vars

# Check docker-compose.yml
grep -i "api.key\|password.*:" ~/infra/odoo/docker-compose.yml | grep -v "POSTGRES_PASSWORD: odoo"
# Should only find POSTGRES_PASSWORD (dev default), no API keys
```

---

## Execution Script

```bash
#!/bin/bash
set -e

echo "🔨 Building Docker image..."
cd ~/infra/odoo
docker build -t odoo-test:latest -f Dockerfile . --quiet

echo "📏 Checking image size..."
SIZE=$(docker images odoo-test:latest --format "{{.Size}}")
echo "Image size: $SIZE"

echo "🖨️  Testing wkhtmltopdf..."
docker run --rm odoo-test:latest wkhtmltopdf --version

echo "📝 Testing PDF generation..."
docker run --rm odoo-test:latest sh -c "
  echo '<h1>Test</h1>' > /tmp/test.html && \
  wkhtmltopdf /tmp/test.html /tmp/test.pdf && \
  test -s /tmp/test.pdf
"

echo "🔤 Checking fonts..."
FONTS=$(docker run --rm odoo-test:latest fc-list | grep -i "noto\|dejavu" | wc -l)
test "$FONTS" -gt 0
echo "Found $FONTS font families"

echo "👤 Verifying non-root user..."
USER_ID=$(docker run --rm odoo-test:latest id -u)
test "$USER_ID" = "1000"
echo "Running as uid: $USER_ID ✓"

echo "🤖 Checking Anthropic SDK..."
docker run --rm odoo-test:latest python3 -c "import anthropic; print(f'SDK v{anthropic.__version__}')"

echo "🔒 Scanning for hardcoded secrets..."
! grep -i "api.key\|password\|secret\|token" ~/infra/odoo/Dockerfile || {
  echo "❌ Found potential hardcoded secrets in Dockerfile"
  exit 1
}

echo "✅ Eval 05: PASS - Docker image validation complete"
```

---

## Expected Output

```
🔨 Building Docker image...
📏 Checking image size...
Image size: 1.8GB
🖨️  Testing wkhtmltopdf...
wkhtmltopdf 0.12.6
📝 Testing PDF generation...
✓ PDF created: /tmp/test.pdf (5.2K)
🔤 Checking fonts...
Found 42 font families
👤 Verifying non-root user...
Running as uid: 1000 ✓
🤖 Checking Anthropic SDK...
SDK v0.36.0
🔒 Scanning for hardcoded secrets...
✅ No secrets found

✅ Eval 05: PASS - Docker image validation complete
```

---

## Failure Modes

### Common Failures
1. **wkhtmltopdf missing**: Package not installed or wrong architecture
2. **Font rendering broken**: Fonts not installed or fc-cache not run
3. **Running as root**: Dockerfile missing USER directive
4. **SDK import fails**: anthropic package not in requirements.txt
5. **Secrets detected**: Hardcoded API keys or passwords in Dockerfile

### Remediation Steps

**wkhtmltopdf Issues**:
```dockerfile
# Ensure in Dockerfile:
RUN apt-get update && apt-get install -y wkhtmltopdf
```

**Font Issues**:
```dockerfile
RUN apt-get install -y fonts-noto fonts-dejavu-core \
 && fc-cache -fv
```

**Non-Root User**:
```dockerfile
RUN useradd -m -u 1000 odoo
USER odoo
```

**SDK Missing**:
```requirements.txt
anthropic>=0.36.0
```

**Secrets Compliance**:
```dockerfile
# ❌ NEVER do this
ENV ANTHROPIC_API_KEY=sk-ant-...

# ✅ Correct approach
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
# Then pass at runtime: docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

---

## Reference

- Existing Dockerfile: ~/infra/odoo/Dockerfile
- Docker best practices: knowledge/playbooks/docker/
- OCA Docker patterns: https://github.com/OCA/docker
