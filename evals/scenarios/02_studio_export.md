# Eval Scenario 02: Studio XML Export Validation

**Skill**: odoo-studio-ops
**Complexity**: Medium
**Estimated Time**: 4-6 minutes

---

## Objective

Validate Studio change documentation workflow:
- Apply Studio field customization to standard model
- Export changes to XML format
- Verify XML structure and xpath validity
- Ensure changes are reversible with documented rollback
- Validate migration-safe implementation

---

## Scenario

**Task**: "Document a Studio change to add custom field 'estimated_hours' (Float) to project.task model with:
- Export XML artifacts showing the customization
- Valid xpath expressions for field placement
- Rollback procedure with SQL/XML revert steps
- Migration notes for reproducing in code
- Change plan documentation following odoo-studio-ops format"

---

## Pass Criteria

### Change Plan Documentation
```
knowledge/playbooks/studio/project_task_estimated_hours.md

Required sections:
- Change Summary: What field is being added and why
- Before/After: Model structure comparison
- Studio Steps: Click-by-click procedure
- XML Export: Complete XML artifacts
- Rollback Plan: Step-by-step revert procedure
- Migration Notes: Code equivalent for permanent implementation
- Testing Plan: Validation steps post-change
```

### XML Export Structure
```xml
<!-- knowledge/playbooks/studio/exports/project_task_estimated_hours.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="studio_field_estimated_hours" model="ir.model.fields">
        <field name="name">x_studio_estimated_hours</field>
        <field name="model">project.task</field>
        <field name="field_description">Estimated Hours</field>
        <field name="ttype">float</field>
        <field name="store" eval="True"/>
    </record>

    <!-- View inheritance with xpath -->
    <record id="studio_view_task_form_estimated_hours" model="ir.ui.view">
        <field name="name">project.task.form.estimated_hours</field>
        <field name="model">project.task</field>
        <field name="inherit_id" ref="project.view_task_form2"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='planned_hours']" position="after">
                <field name="x_studio_estimated_hours"/>
            </xpath>
        </field>
    </record>
</odoo>
```

### XML Validation
```bash
# Syntax validation
xmllint --noout knowledge/playbooks/studio/exports/project_task_estimated_hours.xml
# Exit code 0 = valid XML

# Xpath validation (check position attributes)
grep -E "position=\"(before|after|inside|replace|attributes)\"" \
  knowledge/playbooks/studio/exports/project_task_estimated_hours.xml
# Must use valid position values
```

### Rollback Documentation
```markdown
## Rollback Procedure

### Option 1: Via Studio UI
1. Open Studio for project.task model
2. Select custom field "Estimated Hours"
3. Click "Delete" → Confirm deletion
4. Clear browser cache and refresh

### Option 2: Via SQL (Emergency)
```sql
-- Remove field definition
DELETE FROM ir_model_fields
WHERE model = 'project.task'
  AND name = 'x_studio_estimated_hours';

-- Remove view inheritance
DELETE FROM ir_ui_view
WHERE name = 'project.task.form.estimated_hours';

-- Drop column from database (if exists)
ALTER TABLE project_task DROP COLUMN IF EXISTS x_studio_estimated_hours;
```

### Option 3: Via XML Data File
```xml
<!-- rollback_project_task_estimated_hours.xml -->
<odoo noupdate="1">
    <delete model="ir.model.fields"
            search="[('model','=','project.task'),
                     ('name','=','x_studio_estimated_hours')]"/>
    <delete model="ir.ui.view"
            search="[('name','=','project.task.form.estimated_hours')]"/>
</odoo>
```

**Execution**: `odoo-bin -d production -i rollback_module --stop-after-init`
```

### Migration Notes Validation
```markdown
## Code-Equivalent Implementation

### Model Extension (addons/project_estimated/models/project_task.py)
```python
from odoo import models, fields

class ProjectTaskEstimated(models.Model):
    _inherit = 'project.task'

    estimated_hours = fields.Float(
        string='Estimated Hours',
        help='Initial time estimate for task completion',
        tracking=True
    )
```

### View Inheritance (addons/project_estimated/views/project_task_views.xml)
```xml
<record id="view_task_form_estimated" model="ir.ui.view">
    <field name="name">project.task.form.estimated</field>
    <field name="model">project.task</field>
    <field name="inherit_id" ref="project.view_task_form2"/>
    <field name="arch" type="xml">
        <field name="planned_hours" position="after">
            <field name="estimated_hours"/>
        </field>
    </field>
</record>
```

### Migration Path
- Studio prototype → Development module → Code review → Production deployment
- Data preservation: Studio field data can be migrated to code field
```

---

## Execution Script

```bash
#!/bin/bash
set -e

PLAYBOOK_DIR="knowledge/playbooks/studio"
EXPORTS_DIR="$PLAYBOOK_DIR/exports"
CHANGE_PLAN="$PLAYBOOK_DIR/project_task_estimated_hours.md"
XML_EXPORT="$EXPORTS_DIR/project_task_estimated_hours.xml"

echo "📋 Validating Studio change documentation..."

# Structure check
test -d "$PLAYBOOK_DIR" || {
    echo "❌ Playbooks directory missing"
    exit 1
}

test -d "$EXPORTS_DIR" || {
    echo "❌ Exports directory missing"
    exit 1
}

# Change plan validation
test -f "$CHANGE_PLAN" || {
    echo "❌ Change plan not found: $CHANGE_PLAN"
    exit 1
}

echo "✓ Change plan exists"

# Check required sections
for SECTION in "Change Summary" "Before/After" "Studio Steps" "XML Export" "Rollback Plan" "Migration Notes" "Testing Plan"; do
    grep -qi "$SECTION" "$CHANGE_PLAN" || {
        echo "❌ Missing required section: $SECTION"
        exit 1
    }
done

echo "✓ All required sections present"

# XML export validation
test -f "$XML_EXPORT" || {
    echo "❌ XML export not found: $XML_EXPORT"
    exit 1
}

echo "✓ XML export exists"

# XML syntax validation
if command -v xmllint &> /dev/null; then
    xmllint --noout "$XML_EXPORT" 2>&1 || {
        echo "❌ Invalid XML syntax"
        exit 1
    }
    echo "✓ XML syntax valid"
else
    echo "⚠️  xmllint not installed (skipping XML validation)"
fi

# Check for required XML elements
grep -q "ir.model.fields" "$XML_EXPORT" || {
    echo "❌ Missing field definition in XML"
    exit 1
}

grep -q "ir.ui.view" "$XML_EXPORT" || {
    echo "❌ Missing view inheritance in XML"
    exit 1
}

grep -q "xpath" "$XML_EXPORT" || {
    echo "❌ Missing xpath expression"
    exit 1
}

echo "✓ Required XML elements present"

# Validate xpath position attribute
if grep -E "position=\"(before|after|inside|replace|attributes)\"" "$XML_EXPORT" > /dev/null; then
    echo "✓ Valid xpath position found"
else
    echo "❌ Invalid or missing xpath position attribute"
    exit 1
fi

# Check rollback documentation
if grep -qi "rollback" "$CHANGE_PLAN" && \
   grep -qi "delete\|drop" "$CHANGE_PLAN"; then
    echo "✓ Rollback procedure documented"
else
    echo "❌ Incomplete rollback documentation"
    exit 1
fi

# Check migration notes
if grep -qi "migration" "$CHANGE_PLAN" && \
   grep -qi "models.Model\|_inherit" "$CHANGE_PLAN"; then
    echo "✓ Migration notes with code equivalent"
else
    echo "❌ Missing migration notes or code equivalent"
    exit 1
fi

# Verify no hardcoded secrets in XML
if grep -E "sk-ant-|ghp_|password.*=" "$XML_EXPORT" > /dev/null; then
    echo "❌ Hardcoded secrets found in XML"
    exit 1
fi

echo "✓ No hardcoded secrets"

echo "✅ Eval 02: PASS - Studio XML export validation complete"
```

---

## Expected Output

```
📋 Validating Studio change documentation...
✓ Change plan exists
✓ All required sections present
✓ XML export exists
✓ XML syntax valid
✓ Required XML elements present
✓ Valid xpath position found
✓ Rollback procedure documented
✓ Migration notes with code equivalent
✓ No hardcoded secrets

✅ Eval 02: PASS - Studio XML export validation complete
```

---

## Failure Modes

### Common Failures
1. **Missing sections**: Incomplete change plan documentation
2. **Invalid XML**: Syntax errors or malformed structure
3. **Wrong xpath**: Invalid position attribute (e.g., "append" instead of "after")
4. **No rollback**: Missing revert procedure
5. **No migration path**: Missing code equivalent for permanent implementation
6. **Hardcoded values**: Secrets or environment-specific data in XML

### Remediation Steps

**Invalid XML Syntax**:
```bash
# Use xmllint to identify issues
xmllint --noout knowledge/playbooks/studio/exports/project_task_estimated_hours.xml

# Common fixes:
# - Unclosed tags: <field name="test"/> or <field name="test"></field>
# - Missing xmlns: Add xmlns to root element if needed
# - Special characters: Escape &, <, > in text content
```

**Wrong Xpath Position**:
```xml
<!-- ❌ Invalid positions -->
<xpath expr="//field[@name='planned_hours']" position="append">
<xpath expr="//field[@name='planned_hours']" position="below">

<!-- ✅ Valid positions -->
<xpath expr="//field[@name='planned_hours']" position="after">
<xpath expr="//field[@name='planned_hours']" position="before">
<xpath expr="//field[@name='planned_hours']" position="inside">
<xpath expr="//field[@name='planned_hours']" position="replace">
<xpath expr="//field[@name='planned_hours']" position="attributes">
```

**Missing Rollback Documentation**:
```markdown
## Rollback Plan

**REQUIRED ELEMENTS**:
1. UI-based revert (Studio delete)
2. SQL emergency revert (DELETE + ALTER TABLE)
3. XML-based data file revert (<delete> elements)
4. Verification steps post-rollback
```

**Incomplete Migration Notes**:
```markdown
## Migration Notes

**REQUIRED ELEMENTS**:
1. Python model class with _inherit
2. Field definition with proper type and attributes
3. XML view inheritance with xpath
4. Data migration strategy (if Studio field has data)
5. Testing approach for code equivalent
```

---

## Integration with Knowledge Base

### Studio Patterns Reference
- `knowledge/notes/studio_best_practices.md` - Studio workflow patterns
- `knowledge/notes/xpath_patterns.md` - Valid xpath expressions
- `knowledge/playbooks/studio/` - Change plan templates

### OCA Compliance
- Studio fields use `x_studio_` prefix (Studio convention)
- Code equivalents use standard field names (no prefix)
- Migration path: Studio → Custom module → OCA submission

---

## Reference

- **Odoo Studio Documentation**: https://www.odoo.com/documentation/17.0/applications/studio.html
- **XML View Inheritance**: https://www.odoo.com/documentation/17.0/developer/reference/backend/views.html#inheritance
- **Xpath Position Values**: before, after, inside, replace, attributes
- **Sample Change Plan**: knowledge/playbooks/studio/template_change_plan.md
