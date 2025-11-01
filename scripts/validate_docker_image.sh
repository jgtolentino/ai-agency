#!/bin/bash
# scripts/validate_docker_image.sh
# Validates Docker image meets production requirements (Eval 05)

set -e

IMAGE_NAME="${1:-odoo-production:latest}"

echo "🔨 Validating Docker image: $IMAGE_NAME"

# 1. Image exists
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "❌ Image not found: $IMAGE_NAME"
  echo "Build with: docker build --build-arg ODOO_VERSION=16.0 -t $IMAGE_NAME ."
  exit 1
fi

# 2. Image size check
SIZE=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
SIZE_BYTES=$(docker images "$IMAGE_NAME" --format "{{.Size}}" | sed 's/[^0-9.]//g')
echo "📏 Image size: $SIZE"

if [[ "$SIZE" == *"GB"* ]]; then
  SIZE_GB=$(echo "$SIZE" | sed 's/GB//g' | awk '{print $1}')
  if (( $(echo "$SIZE_GB > 3.0" | bc -l) )); then
    echo "❌ Image too large (>3GB): $SIZE"
    exit 1
  elif (( $(echo "$SIZE_GB > 2.0" | bc -l) )); then
    echo "⚠️  Warning: Image size >2GB: $SIZE"
  fi
fi

# 3. wkhtmltopdf check
echo "🖨️  Testing wkhtmltopdf..."
WKHTMLTOPDF_VERSION=$(docker run --rm "$IMAGE_NAME" wkhtmltopdf --version 2>&1 || echo "NOT_FOUND")
if [[ "$WKHTMLTOPDF_VERSION" == "NOT_FOUND" ]]; then
  echo "❌ wkhtmltopdf not installed"
  exit 1
fi
echo "wkhtmltopdf version: $(echo "$WKHTMLTOPDF_VERSION" | head -1)"

# Verify version 0.12.6
if ! echo "$WKHTMLTOPDF_VERSION" | grep -q "0.12.6"; then
  echo "⚠️  Warning: Expected wkhtmltopdf 0.12.6, got: $WKHTMLTOPDF_VERSION"
fi

# 4. PDF generation test
echo "📝 Testing PDF generation..."
docker run --rm "$IMAGE_NAME" sh -c "
  echo '<h1>Test PDF</h1><p>Hello World</p>' > /tmp/test.html && \
  wkhtmltopdf /tmp/test.html /tmp/test.pdf 2>/dev/null && \
  test -s /tmp/test.pdf && \
  ls -lh /tmp/test.pdf
" || {
  echo "❌ PDF generation failed"
  exit 1
}
echo "✓ PDF generated successfully"

# 5. Font check
echo "🔤 Checking fonts..."
FONTS=$(docker run --rm "$IMAGE_NAME" fc-list | grep -i "noto\|dejavu" | wc -l)
if [ "$FONTS" -lt 1 ]; then
  echo "❌ Fonts not found (Noto, DejaVu)"
  exit 1
fi
echo "Found $FONTS font families"

# Verify specific fonts
REQUIRED_FONTS=("Noto Sans" "DejaVu Sans" "Liberation Sans")
for FONT in "${REQUIRED_FONTS[@]}"; do
  if docker run --rm "$IMAGE_NAME" fc-list | grep -q "$FONT"; then
    echo "  ✓ $FONT"
  else
    echo "  ⚠️  $FONT not found"
  fi
done

# 6. Non-root user check
echo "👤 Verifying non-root user..."
USER_ID=$(docker run --rm "$IMAGE_NAME" id -u)
if [ "$USER_ID" != "1000" ]; then
  echo "❌ Running as root (uid: $USER_ID). Expected uid: 1000"
  exit 1
fi

USER_NAME=$(docker run --rm "$IMAGE_NAME" whoami)
if [ "$USER_NAME" != "odoo" ]; then
  echo "⚠️  Warning: User name is '$USER_NAME', expected 'odoo'"
fi

echo "Running as uid: $USER_ID ($USER_NAME) ✓"

# 7. Anthropic SDK check
echo "🤖 Checking Anthropic SDK..."
SDK_VERSION=$(docker run --rm "$IMAGE_NAME" python3 -c "
import anthropic
print(f'{anthropic.__version__}')
" 2>&1)

if [[ "$SDK_VERSION" == *"ModuleNotFoundError"* ]] || [[ "$SDK_VERSION" == *"ImportError"* ]]; then
  echo "❌ Anthropic SDK not installed"
  exit 1
fi

echo "SDK v${SDK_VERSION}"

# Verify minimum version (0.36.0)
SDK_MAJOR=$(echo "$SDK_VERSION" | cut -d. -f1)
SDK_MINOR=$(echo "$SDK_VERSION" | cut -d. -f2)
if [ "$SDK_MAJOR" -lt 0 ] || ([ "$SDK_MAJOR" -eq 0 ] && [ "$SDK_MINOR" -lt 36 ]); then
  echo "⚠️  Warning: SDK version <0.36.0: $SDK_VERSION"
fi

# 8. Environment variable handling check
echo "🔐 Checking environment variable handling..."
# Verify ANTHROPIC_API_KEY is not hardcoded in image
if docker inspect "$IMAGE_NAME" | grep -i "ANTHROPIC_API_KEY.*sk-ant"; then
  echo "❌ CRITICAL: Hardcoded API key found in image!"
  exit 1
fi
echo "✓ No hardcoded secrets in image"

echo ""
echo "=========================================="
echo "✅ Image validation complete"
echo "=========================================="
echo "Summary:"
echo "  Image: $IMAGE_NAME"
echo "  Size: $SIZE"
echo "  wkhtmltopdf: $(echo "$WKHTMLTOPDF_VERSION" | head -1 | awk '{print $2}')"
echo "  Fonts: $FONTS families"
echo "  User: $USER_NAME (uid: $USER_ID)"
echo "  Anthropic SDK: v${SDK_VERSION}"
echo "=========================================="
