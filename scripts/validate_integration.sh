#!/bin/bash
# Integration Validation Script
# Validates cross-references and integration points

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

echo "=================================================="
echo "Integration Validation Script"
echo "Repo: $REPO_ROOT"
echo "=================================================="
echo ""

# Helper functions
check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

# ================================================
# Check 1: Validate cross_references in skill.yaml files
# ================================================
echo "🔍 Check 1: Validating cross_references in skill.yaml files"
echo "────────────────────────────────────────────────"

# odoo-docker-claude skill
DOCKER_SKILL="$REPO_ROOT/skills/odoo-docker-claude/skill.yaml"
if [ -f "$DOCKER_SKILL" ]; then
    # Check if cross_references section exists
    if grep -q "cross_references:" "$DOCKER_SKILL"; then
        check_pass "odoo-docker-claude has cross_references section"

        # Check if ~/infra/odoo/ is referenced
        if grep -q "path: ~/infra/odoo/" "$DOCKER_SKILL"; then
            check_pass "odoo-docker-claude references ~/infra/odoo/"
        else
            check_fail "odoo-docker-claude missing reference to ~/infra/odoo/"
        fi

        # Check if integration doc is referenced
        if grep -q "comparison: knowledge/integration/docker_comparison.md" "$DOCKER_SKILL"; then
            check_pass "odoo-docker-claude references docker_comparison.md"
        else
            check_fail "odoo-docker-claude missing reference to docker_comparison.md"
        fi
    else
        check_fail "odoo-docker-claude missing cross_references section"
    fi
else
    check_fail "odoo-docker-claude/skill.yaml not found"
fi

# odoo-module-dev skill
MODULE_SKILL="$REPO_ROOT/skills/odoo-module-dev/skill.yaml"
if [ -f "$MODULE_SKILL" ]; then
    # Check if cross_references section exists
    if grep -q "cross_references:" "$MODULE_SKILL"; then
        check_pass "odoo-module-dev has cross_references section"

        # Check if sc_demo is referenced
        if grep -q "path: ~/custom_addons/sc_demo/" "$MODULE_SKILL"; then
            check_pass "odoo-module-dev references ~/custom_addons/sc_demo/"
        else
            check_fail "odoo-module-dev missing reference to sc_demo"
        fi

        # Check if deep-research-oca is referenced
        if grep -q "path: ~/.cline/skills/odoo/deep-research-oca/" "$MODULE_SKILL"; then
            check_pass "odoo-module-dev references deep-research-oca"
        else
            check_fail "odoo-module-dev missing reference to deep-research-oca"
        fi

        # Check if integration doc is referenced
        if grep -q "comparison: knowledge/integration/module_patterns_comparison.md" "$MODULE_SKILL"; then
            check_pass "odoo-module-dev references module_patterns_comparison.md"
        else
            check_fail "odoo-module-dev missing reference to module_patterns_comparison.md"
        fi
    else
        check_fail "odoo-module-dev missing cross_references section"
    fi
else
    check_fail "odoo-module-dev/skill.yaml not found"
fi

echo ""

# ================================================
# Check 2: Verify external paths exist
# ================================================
echo "🔍 Check 2: Verifying external infrastructure paths"
echo "────────────────────────────────────────────────"

# Existing Docker infrastructure
if [ -d "$HOME/infra/odoo" ]; then
    check_pass "~/infra/odoo/ directory exists"

    if [ -f "$HOME/infra/odoo/Dockerfile" ]; then
        check_pass "~/infra/odoo/Dockerfile exists"
    else
        check_fail "~/infra/odoo/Dockerfile missing"
    fi

    if [ -f "$HOME/infra/odoo/docker-compose.yml" ]; then
        check_pass "~/infra/odoo/docker-compose.yml exists"
    else
        check_warn "~/infra/odoo/docker-compose.yml missing (optional)"
    fi
else
    check_fail "~/infra/odoo/ directory not found"
fi

# Existing sample module
if [ -d "$HOME/custom_addons/sc_demo" ]; then
    check_pass "~/custom_addons/sc_demo/ directory exists"

    if [ -f "$HOME/custom_addons/sc_demo/__manifest__.py" ]; then
        check_pass "~/custom_addons/sc_demo/__manifest__.py exists"
    else
        check_fail "~/custom_addons/sc_demo/__manifest__.py missing"
    fi

    if [ -f "$HOME/custom_addons/sc_demo/models/sc_demo.py" ]; then
        check_pass "~/custom_addons/sc_demo/models/sc_demo.py exists"
    else
        check_fail "~/custom_addons/sc_demo/models/sc_demo.py missing"
    fi
else
    check_fail "~/custom_addons/sc_demo/ directory not found"
fi

# Existing deep research skill
if [ -f "$HOME/.cline/skills/odoo/deep-research-oca/SKILL.md" ]; then
    check_pass "~/.cline/skills/odoo/deep-research-oca/SKILL.md exists"
else
    check_fail "~/.cline/skills/odoo/deep-research-oca/SKILL.md not found"
fi

echo ""

# ================================================
# Check 3: Validate integration documentation exists
# ================================================
echo "🔍 Check 3: Validating integration documentation"
echo "────────────────────────────────────────────────"

INTEGRATION_DIR="$REPO_ROOT/knowledge/integration"
if [ -d "$INTEGRATION_DIR" ]; then
    check_pass "knowledge/integration/ directory exists"

    # Docker comparison
    if [ -f "$INTEGRATION_DIR/docker_comparison.md" ]; then
        check_pass "docker_comparison.md exists"

        # Check for required sections
        if grep -q "## Side-by-Side Comparison" "$INTEGRATION_DIR/docker_comparison.md"; then
            check_pass "docker_comparison.md has comparison section"
        else
            check_fail "docker_comparison.md missing comparison section"
        fi

        if grep -q "## Migration Path" "$INTEGRATION_DIR/docker_comparison.md"; then
            check_pass "docker_comparison.md has migration path"
        else
            check_fail "docker_comparison.md missing migration path"
        fi
    else
        check_fail "docker_comparison.md missing"
    fi

    # Module patterns comparison
    if [ -f "$INTEGRATION_DIR/module_patterns_comparison.md" ]; then
        check_pass "module_patterns_comparison.md exists"

        # Check for required sections
        if grep -q "## Feature-by-Feature Comparison" "$INTEGRATION_DIR/module_patterns_comparison.md"; then
            check_pass "module_patterns_comparison.md has feature comparison"
        else
            check_fail "module_patterns_comparison.md missing feature comparison"
        fi

        if grep -q "## Migration Path from sc_demo to Production" "$INTEGRATION_DIR/module_patterns_comparison.md"; then
            check_pass "module_patterns_comparison.md has migration path"
        else
            check_fail "module_patterns_comparison.md missing migration path"
        fi
    else
        check_fail "module_patterns_comparison.md missing"
    fi

    # Research coordination
    if [ -f "$INTEGRATION_DIR/research_coordination.md" ]; then
        check_pass "research_coordination.md exists"

        # Check for required sections
        if grep -q "## Query Set Coordination" "$INTEGRATION_DIR/research_coordination.md"; then
            check_pass "research_coordination.md has query coordination"
        else
            check_fail "research_coordination.md missing query coordination"
        fi

        if grep -q "## Citation Format Validation" "$INTEGRATION_DIR/research_coordination.md"; then
            check_pass "research_coordination.md has citation format section"
        else
            check_fail "research_coordination.md missing citation format section"
        fi
    else
        check_fail "research_coordination.md missing"
    fi
else
    check_fail "knowledge/integration/ directory not found"
fi

# Main integration points doc
if [ -f "$REPO_ROOT/knowledge/INTEGRATION_POINTS.md" ]; then
    check_pass "knowledge/INTEGRATION_POINTS.md exists"

    # Check for required sections
    if grep -q "## Cross-Reference Map" "$REPO_ROOT/knowledge/INTEGRATION_POINTS.md"; then
        check_pass "INTEGRATION_POINTS.md has cross-reference map"
    else
        check_fail "INTEGRATION_POINTS.md missing cross-reference map"
    fi

    if grep -q "## Dependency Graph" "$REPO_ROOT/knowledge/INTEGRATION_POINTS.md"; then
        check_pass "INTEGRATION_POINTS.md has dependency graph"
    else
        check_fail "INTEGRATION_POINTS.md missing dependency graph"
    fi
else
    check_fail "knowledge/INTEGRATION_POINTS.md missing"
fi

echo ""

# ================================================
# Check 4: Validate no duplicate Dockerfiles
# ================================================
echo "🔍 Check 4: Checking for duplicate Dockerfiles"
echo "────────────────────────────────────────────────"

# Count Dockerfiles in repo (should be 0 - only runbooks/docs)
DOCKERFILE_COUNT=$(find "$REPO_ROOT" -name "Dockerfile" -type f 2>/dev/null | wc -l | tr -d ' ')

if [ "$DOCKERFILE_COUNT" -eq 0 ]; then
    check_pass "No duplicate Dockerfiles in repo (enhancements documented separately)"
else
    check_fail "Found $DOCKERFILE_COUNT Dockerfile(s) in repo - should document enhancements instead of duplicating"
    find "$REPO_ROOT" -name "Dockerfile" -type f
fi

echo ""

# ================================================
# Check 5: Validate research query coordination
# ================================================
echo "🔍 Check 5: Validating research query coordination"
echo "────────────────────────────────────────────────"

AUTO_RESEARCH="$REPO_ROOT/knowledge/scripts/auto_research.py"
if [ -f "$AUTO_RESEARCH" ]; then
    check_pass "auto_research.py exists"

    # Check for quality scoring
    if grep -q "class QualityScorer:" "$AUTO_RESEARCH"; then
        check_pass "auto_research.py has QualityScorer class"
    else
        check_fail "auto_research.py missing QualityScorer class"
    fi

    # Check for citation formatting
    if grep -q "class CitationFormatter:" "$AUTO_RESEARCH"; then
        check_pass "auto_research.py has CitationFormatter class"
    else
        check_fail "auto_research.py missing CitationFormatter class"
    fi

    # Check for OCA crawler
    if grep -q "class OCAGitHubCrawler:" "$AUTO_RESEARCH"; then
        check_pass "auto_research.py has OCAGitHubCrawler class"
    else
        check_fail "auto_research.py missing OCAGitHubCrawler class"
    fi

    # Check for minimum quality score threshold
    if grep -q "MIN_ACCEPTABLE_SCORE = 60" "$AUTO_RESEARCH"; then
        check_pass "auto_research.py has quality threshold (60)"
    else
        check_fail "auto_research.py missing or incorrect quality threshold"
    fi

    # Check for complementary query domains
    if grep -q "'module_dev':" "$AUTO_RESEARCH" && grep -q "'docker':" "$AUTO_RESEARCH"; then
        check_pass "auto_research.py has module_dev and docker query domains"
    else
        check_fail "auto_research.py missing expected query domains"
    fi
else
    check_fail "auto_research.py not found"
fi

# Check if deep-research-oca is referenced in research_coordination.md
if [ -f "$INTEGRATION_DIR/research_coordination.md" ]; then
    if grep -q "~/.cline/skills/odoo/deep-research-oca/" "$INTEGRATION_DIR/research_coordination.md"; then
        check_pass "research_coordination.md references deep-research-oca skill"
    else
        check_fail "research_coordination.md missing reference to deep-research-oca"
    fi
fi

echo ""

# ================================================
# Check 6: Validate sc_demo not replaced
# ================================================
echo "🔍 Check 6: Validating sc_demo used as reference (not replaced)"
echo "────────────────────────────────────────────────"

# Check odoo-module-dev skill uses sc_demo as reference
if [ -f "$MODULE_SKILL" ]; then
    if grep -q "when_to_use_sc_demo:" "$MODULE_SKILL"; then
        check_pass "odoo-module-dev documents when to use sc_demo"
    else
        check_fail "odoo-module-dev missing guidance on sc_demo usage"
    fi

    if grep -q "when_to_use_this_skill:" "$MODULE_SKILL"; then
        check_pass "odoo-module-dev documents when to use production patterns"
    else
        check_fail "odoo-module-dev missing guidance on production pattern usage"
    fi

    # Ensure "EXTENDS" relationship documented
    if grep -q "EXTENDS" "$MODULE_SKILL"; then
        check_pass "odoo-module-dev documents EXTENDS relationship with sc_demo"
    else
        check_fail "odoo-module-dev missing EXTENDS relationship documentation"
    fi
fi

# Check module_patterns_comparison.md doesn't suggest replacing sc_demo
if [ -f "$INTEGRATION_DIR/module_patterns_comparison.md" ]; then
    if grep -q "Keep sc_demo" "$INTEGRATION_DIR/module_patterns_comparison.md"; then
        check_pass "module_patterns_comparison.md preserves sc_demo"
    else
        check_warn "module_patterns_comparison.md should explicitly preserve sc_demo"
    fi
fi

echo ""

# ================================================
# Summary
# ================================================
echo "=================================================="
echo "Validation Summary"
echo "=================================================="
echo -e "Total Checks:  $TOTAL_CHECKS"
echo -e "${GREEN}Passed:        $PASSED_CHECKS${NC}"
echo -e "${RED}Failed:        $FAILED_CHECKS${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✅ All integration validation checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Integration validation failed with $FAILED_CHECKS errors.${NC}"
    echo ""
    echo "Review the errors above and fix integration issues before proceeding."
    exit 1
fi
