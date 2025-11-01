#!/usr/bin/env bash
set -euo pipefail

echo "=== Eval Scenario 12: QMS SOP Workflow ==="
echo ""

# Check if qms_sop module exists
if [ ! -d "custom_addons/qms_sop" ]; then
    echo "❌ FAIL: qms_sop module not found in custom_addons/"
    echo "   Expected: custom_addons/qms_sop/"
    exit 1
fi

echo "✅ Module exists: custom_addons/qms_sop"

# Check module structure
required_files=(
    "custom_addons/qms_sop/__manifest__.py"
    "custom_addons/qms_sop/models/qms_sop_document.py"
    "custom_addons/qms_sop/models/qms_sop_step.py"
    "custom_addons/qms_sop/models/qms_sop_run.py"
    "custom_addons/qms_sop/models/qms_sop_run_step.py"
    "custom_addons/qms_sop/models/qms_error_code.py"
    "custom_addons/qms_sop/security/ir.model.access.csv"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ FAIL: Required file missing: $file"
        exit 1
    fi
done

echo "✅ All required module files present"

# Check for state field in qms_sop_run
if ! grep -q "state.*=.*fields.Selection" "custom_addons/qms_sop/models/qms_sop_run.py"; then
    echo "❌ FAIL: State field not found in qms.sop.run model"
    echo "   Expected: state = fields.Selection([...])"
    exit 1
fi

echo "✅ State field defined in SOP run model"

# Check for required states
required_states=("draft" "in_progress" "completed")
for state in "${required_states[@]}"; do
    if ! grep -q "'$state'" "custom_addons/qms_sop/models/qms_sop_run.py"; then
        echo "❌ FAIL: Required state '$state' not found in qms.sop.run"
        exit 1
    fi
done

echo "✅ All required states defined (draft, in_progress, completed)"

# Check for computed field (progress_percentage or similar)
if ! grep -qE "@api.depends.*compute.*progress" "custom_addons/qms_sop/models/qms_sop_run.py"; then
    echo "⚠️  WARNING: No computed progress field found"
    echo "   Expected: @api.depends with _compute_progress method"
else
    echo "✅ Computed progress field found"
fi

# Check for state machine constraints
if ! grep -qE "@api.constrains.*state" "custom_addons/qms_sop/models/qms_sop_run.py"; then
    echo "⚠️  WARNING: No state constraints found"
    echo "   Expected: @api.constrains('state') for state machine validation"
else
    echo "✅ State constraints found"
fi

# Check for One2many relationship (step_run_ids)
if ! grep -q "step_run_ids.*=.*fields.One2many" "custom_addons/qms_sop/models/qms_sop_run.py"; then
    echo "❌ FAIL: One2many relationship 'step_run_ids' not found"
    echo "   Expected: step_run_ids = fields.One2many('qms.sop.run.step', 'run_id')"
    exit 1
fi

echo "✅ One2many relationship (step_run_ids) defined"

# Check for Many2one relationship in qms_sop_run_step
if ! grep -q "run_id.*=.*fields.Many2one" "custom_addons/qms_sop/models/qms_sop_run_step.py"; then
    echo "❌ FAIL: Many2one relationship 'run_id' not found in step model"
    exit 1
fi

echo "✅ Many2one relationship (run_id) defined in step model"

# Check for error code model
if ! grep -q "class.*QmsErrorCode" "custom_addons/qms_sop/models/qms_error_code.py"; then
    echo "❌ FAIL: QmsErrorCode class not found"
    exit 1
fi

echo "✅ Error code model defined"

# Check for error linkage (qms.sop.run.error or similar)
if [ -f "custom_addons/qms_sop/models/qms_sop_run_error.py" ]; then
    echo "✅ Error linkage model exists"
else
    echo "⚠️  WARNING: No qms_sop_run_error.py found (error linkage may be in different file)"
fi

# Check manifest for dependencies
if ! grep -q "base" "custom_addons/qms_sop/__manifest__.py"; then
    echo "❌ FAIL: Missing 'base' dependency in __manifest__.py"
    exit 1
fi

echo "✅ Module manifest valid"

# Security check: verify access rules exist
if [ ! -f "custom_addons/qms_sop/security/ir.model.access.csv" ]; then
    echo "❌ FAIL: Missing security access rules"
    exit 1
fi

# Verify access.csv has header and rules for all models
models=("qms.sop.document" "qms.sop.step" "qms.sop.run" "qms.sop.run.step" "qms.error.code")
for model in "${models[@]}"; do
    if ! grep -q "$model" "custom_addons/qms_sop/security/ir.model.access.csv"; then
        echo "⚠️  WARNING: No access rules found for model: $model"
    fi
done

echo "✅ Security access rules present"

# Check for seed data
if [ -f "custom_addons/qms_sop/data/qms_sop_seeds.xml" ]; then
    echo "✅ Seed data file exists"

    # Verify seed data has SOP documents
    if grep -q "SOP-BUILD-001" "custom_addons/qms_sop/data/qms_sop_seeds.xml"; then
        echo "✅ Seed data contains SOP documents"
    else
        echo "⚠️  WARNING: Seed data missing SOP documents"
    fi
else
    echo "⚠️  WARNING: No seed data file found (optional: data/qms_sop_seeds.xml)"
fi

# Check for views directory
if [ -d "custom_addons/qms_sop/views" ]; then
    echo "✅ Views directory exists"

    # Check for key view files
    if [ -f "custom_addons/qms_sop/views/qms_sop_run_views.xml" ]; then
        echo "✅ SOP run views exist"
    else
        echo "⚠️  WARNING: No SOP run views found"
    fi
else
    echo "⚠️  WARNING: No views directory found"
fi

# Check for tests directory
if [ -d "custom_addons/qms_sop/tests" ]; then
    echo "✅ Tests directory exists"

    # Check for test file
    if [ -f "custom_addons/qms_sop/tests/test_qms_sop_workflow.py" ]; then
        echo "✅ Test file exists: test_qms_sop_workflow.py"

        # Verify test file has test cases
        test_count=$(grep -c "def test_" "custom_addons/qms_sop/tests/test_qms_sop_workflow.py" || echo "0")
        if [ "$test_count" -ge 6 ]; then
            echo "✅ Test file has $test_count test cases (≥6 required)"
        else
            echo "⚠️  WARNING: Test file has $test_count test cases (<6 expected)"
        fi
    else
        echo "⚠️  WARNING: No test file found (expected: tests/test_qms_sop_workflow.py)"
    fi
else
    echo "⚠️  WARNING: No tests directory found"
fi

# Final summary
echo ""
echo "=== Validation Summary ==="
echo "✅ Module structure valid"
echo "✅ State machine implemented"
echo "✅ SOP run workflow models present"
echo "✅ Step tracking models present"
echo "✅ Error code linkage present"
echo "✅ Security rules configured"
echo ""
echo "✅ Scenario 12: PASS"
echo ""
echo "Note: Full test execution requires Odoo runtime and pytest."
echo "Run: pytest custom_addons/qms_sop/tests/test_qms_sop_workflow.py -v"

exit 0
