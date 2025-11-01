# Odoo OCA Compliance Checklist

- __manifest__.py: version, license, depends, data vs demo separated
- Access: ir.model.access.csv present; record rules least-privilege
- ORM: avoid raw SQL; no unsafe eval; correct ondelete; compute/store usage
- Performance: indexes for heavy domains; avoid n+1 on compute/search
- Tests: deterministic; --test-enable; migration scripts where needed
- Pre-commit+pylint-odoo configured
