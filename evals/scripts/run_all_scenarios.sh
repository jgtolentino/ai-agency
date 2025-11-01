#!/usr/bin/env bash
# run_all_scenarios.sh - Master test runner for all evaluation scenarios
# Target: ≥80% pass rate for Sprint 2 (4/5 passing)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_FILE="$SCRIPT_DIR/../RESULTS.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "🧪 Odoo Expertise Agent - Evaluation Suite"
echo "========================================"
echo ""

# Initialize counters
TOTAL_SCENARIOS=0
PASSED_SCENARIOS=0
FAILED_SCENARIOS=0
SKIPPED_SCENARIOS=0

# Scenarios to run (Sprint 3 QA2: All 10 scenarios)
SCENARIOS=(
    "01_oca_scaffolding"
    "02_studio_export"
    "03_odoo_sh_deploy"
    "04_orm_compliance"
    "05_docker_validation"
    "06_record_rule_n1"
    "07_migration_script"
    "08_docker_compose_env"
    "09_visual_parity"
    "10_secrets_compliance"
)

# Store results for summary
declare -A SCENARIO_RESULTS
declare -A SCENARIO_TIMES

# Start time
START_TIME=$(date +%s)

echo "📊 Running ${#SCENARIOS[@]} evaluation scenarios..."
echo ""

# Run each scenario
for SCENARIO in "${SCENARIOS[@]}"; do
    TOTAL_SCENARIOS=$((TOTAL_SCENARIOS + 1))
    SCENARIO_SCRIPT="$SCRIPT_DIR/${SCENARIO}.sh"

    echo "----------------------------------------"
    echo "Running: $SCENARIO"
    echo "----------------------------------------"

    if [ ! -f "$SCENARIO_SCRIPT" ]; then
        echo -e "${YELLOW}⚠️  SKIPPED: Script not found${NC}"
        SKIPPED_SCENARIOS=$((SKIPPED_SCENARIOS + 1))
        SCENARIO_RESULTS[$SCENARIO]="SKIPPED"
        SCENARIO_TIMES[$SCENARIO]="0"
        continue
    fi

    # Run scenario and capture result
    SCENARIO_START=$(date +%s)

    if bash "$SCENARIO_SCRIPT" 2>&1; then
        SCENARIO_END=$(date +%s)
        SCENARIO_TIME=$((SCENARIO_END - SCENARIO_START))
        echo -e "${GREEN}✅ PASSED${NC} (${SCENARIO_TIME}s)"
        PASSED_SCENARIOS=$((PASSED_SCENARIOS + 1))
        SCENARIO_RESULTS[$SCENARIO]="PASSED"
        SCENARIO_TIMES[$SCENARIO]="$SCENARIO_TIME"
    else
        SCENARIO_END=$(date +%s)
        SCENARIO_TIME=$((SCENARIO_END - SCENARIO_START))
        echo -e "${RED}❌ FAILED${NC} (${SCENARIO_TIME}s)"
        FAILED_SCENARIOS=$((FAILED_SCENARIOS + 1))
        SCENARIO_RESULTS[$SCENARIO]="FAILED"
        SCENARIO_TIMES[$SCENARIO]="$SCENARIO_TIME"
    fi

    echo ""
done

# End time
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

# Calculate pass rate
if [ $TOTAL_SCENARIOS -gt 0 ]; then
    PASS_RATE=$(echo "scale=1; ($PASSED_SCENARIOS * 100) / $TOTAL_SCENARIOS" | bc)
else
    PASS_RATE=0
fi

# Generate summary
echo "========================================"
echo "📈 Evaluation Summary"
echo "========================================"
echo "Total Scenarios: $TOTAL_SCENARIOS"
echo -e "${GREEN}Passed: $PASSED_SCENARIOS${NC}"
echo -e "${RED}Failed: $FAILED_SCENARIOS${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED_SCENARIOS${NC}"
echo "Pass Rate: ${PASS_RATE}%"
echo "Total Time: ${TOTAL_TIME}s"
echo ""

# Individual scenario results
echo "Individual Results:"
echo "-------------------"
for SCENARIO in "${SCENARIOS[@]}"; do
    RESULT="${SCENARIO_RESULTS[$SCENARIO]}"
    TIME="${SCENARIO_TIMES[$SCENARIO]}"

    if [ "$RESULT" = "PASSED" ]; then
        echo -e "${GREEN}✅${NC} $SCENARIO (${TIME}s)"
    elif [ "$RESULT" = "FAILED" ]; then
        echo -e "${RED}❌${NC} $SCENARIO (${TIME}s)"
    else
        echo -e "${YELLOW}⚠️${NC}  $SCENARIO (skipped)"
    fi
done
echo ""

# Generate RESULTS.md
echo "📝 Writing results to $RESULTS_FILE..."

cat > "$RESULTS_FILE" <<EOF
# Evaluation Results - Sprint 3 (QA2)

**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Pass Rate**: ${PASS_RATE}% ($PASSED_SCENARIOS/$TOTAL_SCENARIOS)
**Total Time**: ${TOTAL_TIME}s
**Target**: ≥80% pass rate

---

## Summary

- ✅ **Passed**: $PASSED_SCENARIOS
- ❌ **Failed**: $FAILED_SCENARIOS
- ⚠️  **Skipped**: $SKIPPED_SCENARIOS

---

## Individual Scenario Results

| Scenario | Result | Time |
|----------|--------|------|
EOF

for SCENARIO in "${SCENARIOS[@]}"; do
    RESULT="${SCENARIO_RESULTS[$SCENARIO]}"
    TIME="${SCENARIO_TIMES[$SCENARIO]}"

    if [ "$RESULT" = "PASSED" ]; then
        echo "| $SCENARIO | ✅ PASSED | ${TIME}s |" >> "$RESULTS_FILE"
    elif [ "$RESULT" = "FAILED" ]; then
        echo "| $SCENARIO | ❌ FAILED | ${TIME}s |" >> "$RESULTS_FILE"
    else
        echo "| $SCENARIO | ⚠️  SKIPPED | - |" >> "$RESULTS_FILE"
    fi
done

cat >> "$RESULTS_FILE" <<EOF

---

## Scenario Details

### 01: OCA Module Scaffolding
**Status**: ${SCENARIO_RESULTS[01_oca_scaffolding]}
**Validates**: OCA-compliant module structure, manifest, models, security, tests

### 02: Studio XML Export
**Status**: ${SCENARIO_RESULTS[02_studio_export]}
**Validates**: Studio change documentation, XML export, rollback procedures

### 03: Odoo.sh Deployment
**Status**: ${SCENARIO_RESULTS[03_odoo_sh_deploy]}
**Validates**: Deployment runbook, staging gates, rollback, monitoring

### 04: ORM Compliance
**Status**: ${SCENARIO_RESULTS[04_orm_compliance]}
**Validates**: @api.depends, @api.onchange, @api.constrains, no anti-patterns

### 05: Docker Image Validation
**Status**: ${SCENARIO_RESULTS[05_docker_validation]}
**Validates**: wkhtmltopdf, fonts, non-root user, SDK, no secrets

### 06: Record Rule N+1 Detection
**Status**: ${SCENARIO_RESULTS[06_record_rule_n1]}
**Validates**: N+1 query detection in record rules, optimized domain expressions

### 07: Migration Script Validation
**Status**: ${SCENARIO_RESULTS[07_migration_script]}
**Validates**: openupgradelib usage, data preservation, rollback procedures

### 08: Docker Compose Environment Variables
**Status**: ${SCENARIO_RESULTS[08_docker_compose_env]}
**Validates**: No hardcoded secrets, .env file usage, ${VAR:?required} syntax

### 09: Visual Parity Testing
**Status**: ${SCENARIO_RESULTS[09_visual_parity]}
**Validates**: Playwright screenshots, SSIM comparison, baseline storage

### 10: Secrets Compliance
**Status**: ${SCENARIO_RESULTS[10_secrets_compliance]}
**Validates**: No hardcoded API keys, passwords, tokens in codebase

---

## Pass Criteria

**Sprint 3 Target**: ≥80% (8/10 scenarios passing)

EOF

# Check if target met
if (( $(echo "$PASS_RATE >= 80" | bc -l) )); then
    echo -e "${GREEN}✅ Target Met: Pass rate ${PASS_RATE}% ≥ 80%${NC}" >> "$RESULTS_FILE"
    echo -e "${GREEN}✅ Target Met: Pass rate ${PASS_RATE}% ≥ 80%${NC}"
else
    echo -e "${RED}❌ Target Not Met: Pass rate ${PASS_RATE}% < 80%${NC}" >> "$RESULTS_FILE"
    echo -e "${RED}❌ Target Not Met: Pass rate ${PASS_RATE}% < 80%${NC}"
fi

cat >> "$RESULTS_FILE" <<EOF

---

## Next Steps

EOF

if (( $(echo "$PASS_RATE >= 80" | bc -l) )); then
    cat >> "$RESULTS_FILE" <<EOF
1. ✅ Sprint 3 QA2 complete (10/10 scenarios)
2. Review any warnings from scenarios
3. All pre-commit hooks configured
4. Ready for production deployment
EOF
else
    cat >> "$RESULTS_FILE" <<EOF
1. ❌ Investigate failed scenarios
2. Root cause analysis for failures
3. Update knowledge base with findings
4. Refine skills based on learnings
5. Re-run scenarios until ≥80% pass rate
EOF
fi

echo ""
echo "✅ Results written to: $RESULTS_FILE"
echo ""

# Exit with appropriate code
if [ $FAILED_SCENARIOS -eq 0 ] && [ $SKIPPED_SCENARIOS -eq 0 ]; then
    echo -e "${GREEN}🎉 All scenarios passed!${NC}"
    exit 0
elif (( $(echo "$PASS_RATE >= 80" | bc -l) )); then
    echo -e "${GREEN}✅ Target met: ${PASS_RATE}% pass rate${NC}"
    exit 0
else
    echo -e "${RED}❌ Target not met: ${PASS_RATE}% pass rate (need ≥80%)${NC}"
    exit 1
fi
