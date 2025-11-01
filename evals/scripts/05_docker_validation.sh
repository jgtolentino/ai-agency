#!/usr/bin/env bash
# Eval Scenario 05: Docker Image Validation
# Validates Docker image meets production requirements

set -e

DOCKERFILE_DIR="$HOME/infra/odoo"
IMAGE_NAME="odoo-test:latest"

echo "🔍 Eval 05: Docker Image Validation"
echo "===================================="

# Check Dockerfile exists
echo "📁 Checking Dockerfile..."
test -f "$DOCKERFILE_DIR/Dockerfile" || {
    echo "❌ Dockerfile not found: $DOCKERFILE_DIR/Dockerfile"
    exit 1
}
echo "✓ Dockerfile exists"

# Build image
echo "🔨 Building Docker image..."
cd "$DOCKERFILE_DIR"
docker build -t "$IMAGE_NAME" -f Dockerfile . --quiet || {
    echo "❌ Docker build failed"
    exit 1
}
echo "✓ Image built successfully"

# Check image size
echo "📏 Checking image size..."
SIZE=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
echo "  Image size: $SIZE"
# Warning if >2GB, fail if >3GB (production viability)
SIZE_MB=$(docker images "$IMAGE_NAME" --format "{{.Size}}" | sed 's/GB/*1000/;s/MB//' | bc 2>/dev/null || echo "0")
if (( $(echo "$SIZE_MB > 3000" | bc -l 2>/dev/null || echo "0") )); then
    echo "❌ Image too large: $SIZE (>3GB)"
    exit 1
elif (( $(echo "$SIZE_MB > 2000" | bc -l 2>/dev/null || echo "0") )); then
    echo "⚠️  Image size warning: $SIZE (>2GB)"
fi

# Test wkhtmltopdf
echo "🖨️  Testing wkhtmltopdf..."
docker run --rm "$IMAGE_NAME" wkhtmltopdf --version > /dev/null 2>&1 || {
    echo "❌ wkhtmltopdf not available"
    exit 1
}
echo "✓ wkhtmltopdf installed"

# Test PDF generation
echo "📝 Testing PDF generation..."
docker run --rm "$IMAGE_NAME" sh -c "
    echo '<h1>Test</h1>' > /tmp/test.html && \
    wkhtmltopdf /tmp/test.html /tmp/test.pdf && \
    test -s /tmp/test.pdf
" > /dev/null 2>&1 || {
    echo "❌ PDF generation failed"
    exit 1
}
echo "✓ PDF generation works"

# Check fonts
echo "🔤 Checking fonts..."
FONTS=$(docker run --rm "$IMAGE_NAME" fc-list 2>/dev/null | grep -i "noto\|dejavu" | wc -l || echo "0")
if [ "$FONTS" -gt 0 ]; then
    echo "✓ Found $FONTS font families"
else
    echo "⚠️  No Noto/DejaVu fonts found"
fi

# Verify non-root user
echo "👤 Verifying non-root user..."
USER_ID=$(docker run --rm "$IMAGE_NAME" id -u)
if [ "$USER_ID" = "1000" ]; then
    echo "✓ Running as uid: $USER_ID"
else
    echo "⚠️  Running as uid: $USER_ID (expected 1000)"
fi

# Check Anthropic SDK
echo "🤖 Checking Anthropic SDK..."
docker run --rm "$IMAGE_NAME" python3 -c "import anthropic; print(f'SDK v{anthropic.__version__}')" 2>/dev/null || {
    echo "⚠️  Anthropic SDK not installed (optional)"
}

# Scan for hardcoded secrets
echo "🔒 Scanning for secrets..."
if grep -i "api.key\|password\|secret\|token" "$DOCKERFILE_DIR/Dockerfile" | grep -v "DEBIAN_FRONTEND" > /dev/null; then
    echo "❌ Found potential hardcoded secrets in Dockerfile"
    exit 1
fi

if grep -E "ENV.*(KEY|PASSWORD|SECRET|TOKEN)" "$DOCKERFILE_DIR/Dockerfile" | grep -v "ENV DEBIAN_FRONTEND" > /dev/null; then
    echo "❌ Found hardcoded env vars in Dockerfile"
    exit 1
fi

if [ -f "$DOCKERFILE_DIR/docker-compose.yml" ]; then
    if grep -i "api.key\|password.*:" "$DOCKERFILE_DIR/docker-compose.yml" | grep -v "POSTGRES_PASSWORD: odoo" > /dev/null; then
        echo "❌ Found hardcoded secrets in docker-compose.yml"
        exit 1
    fi
fi

echo "✓ No hardcoded secrets found"

echo ""
echo "✅ Eval 05: PASS - Docker image validation complete"
echo "===================================="
