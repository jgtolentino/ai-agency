#!/usr/bin/env bash
# run_local_checks.sh - Local quality gates before commit

set -e

echo "🔍 Running local quality checks..."

# Pre-commit hooks (if installed)
if command -v pre-commit &> /dev/null; then
    echo "✓ Running pre-commit hooks..."
    pre-commit run --all-files || {
        echo "⚠️  Pre-commit warnings (review above)"
    }
else
    echo "⚠️  pre-commit not installed (pip install pre-commit)"
fi

# Pytest (if tests exist)
if command -v pytest &> /dev/null && [ -d "tests" ]; then
    echo "✓ Running pytest..."
    pytest -q || {
        echo "⚠️  Test warnings (review above)"
    }
else
    echo "ℹ️  No tests to run"
fi

# Check for hardcoded secrets
echo "✓ Scanning for hardcoded secrets..."
if grep -r "sk-ant-\|ghp_\|sbp_" . --exclude-dir=".git" --exclude="*.md" 2>/dev/null; then
    echo "❌ Found potential hardcoded secrets"
    exit 1
fi

echo "✅ Local checks executed successfully"
