# Quick Reference – Odoo Agent Expertise

**One-Page Cheat Sheet** for daily Odoo development with Cline CLI

---

## Essential Commands

```bash
# Generate OCA module
cline-odoo "Create module 'task_priority' with model task.priority, fields: name, level, color"

# Research before implementing
cline-odoo "Research OCA pattern for multi-level approval workflows"

# Validate module
cd custom_addons/your_module && pre-commit run --all-files

# Run tests
pytest tests/test_your_module.py -v

# Run all evals
cd evals && bash scripts/run_all_scenarios.sh

# Update knowledge base
cd knowledge/scripts && python3 auto_research.py --domain oca
```

---

## Skill Auto-Activation

| Keyword | Skill | Use Case |
|---------|-------|----------|
| "module", "model", "field" | odoo-module-dev | Generate OCA modules |
| "Studio", "change", "rollback" | odoo-studio-ops | Document Studio changes |
| "Odoo.sh", "deploy", "staging" | odoo-sh-devops | Create deployment plans |
| "Docker", "Dockerfile", "SDK" | odoo-docker-claude | Build Docker images |

---

## Model Routing Decision Matrix

| Task | Model | Cost | When to Use |
|------|-------|------|-------------|
| Module generation | DeepSeek v3.1 | ~$0.0001 | Default for all coding |
| Deployment planning | DeepSeek R1 | ~$0.001 | Complex reasoning needed |
| Repo-wide refactor | Claude Code | $0* | >10 files, git ops |

*Included in Claude Max subscription

---

## Daily Workflow

### Morning (10 min)
```bash
# 1. Check API keys
echo "DeepSeek: ${DEEPSEEK_API_KEY:+✅}"
echo "GitHub: ${GITHUB_TOKEN:+✅}"

# 2. Update knowledge base
cd knowledge/scripts && python3 auto_research.py --domain oca --limit 5

# 3. Review tasks
cat spec/tasks/TASKS.yaml | grep "in_progress"
```

### Development (per module)
```bash
# 1. Research pattern
cline-odoo "Research OCA pattern for [your feature]"

# 2. Generate module
cline-odoo "Create module with [specs]"

# 3. Validate
pre-commit run --all-files
pytest tests/ -v

# 4. Document
echo "## [Pattern Name]
- Link: [URL]
- Takeaway: [one-liner]
" >> knowledge/notes/$(date +%Y-%m-%d).md
```

### End of Day (5 min)
```bash
# Check costs
curl -s https://api.deepseek.com/v1/usage \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" | jq '.data.total_cost'

# Archive if >$2/month trending
```

---

## ORM Patterns Quick Reference

### Computed Fields (No N+1)
```python
@api.depends('line_ids', 'line_ids.amount')
def _compute_total(self):
    if not self:
        return
    data = self.env['model.line'].read_group(
        domain=[('parent_id', 'in', self.ids)],
        fields=['parent_id', 'amount:sum'],
        groupby=['parent_id']
    )
    mapping = {d['parent_id'][0]: d['amount'] for d in data}
    for rec in self:
        rec.total = mapping.get(rec.id, 0.0)
```

### Security (Access Rules)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model.user,model_model,base.group_user,1,0,0,0
access_model_manager,model.manager,model_model,base.group_system,1,1,1,1
```

### Tests (Query Count)
```python
def test_no_n1_query(self):
    records = self.Model.create([...] * 50)
    with self.assertQueryCount(1):
        records._compute_total()
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Skills not activating | Symlink broken | `ls ~/.cline/skills/odoo-expertise` |
| DeepSeek API error | Rate limit | Check: `curl https://api.deepseek.com/v1/rate-limit` |
| Pre-commit fails | Missing tools | `pip install black isort flake8 pylint-odoo` |
| Tests failing | Wrong dependencies | `@api.depends('field_id.sub_field')` not `'field_id'` |
| Eval timeout | Stuck process | `pkill -f pytest && rm -rf test_module_*` |

---

## Emergency Procedures

### Rollback Deployment
```bash
# Odoo.sh
git revert <commit> && git push origin production

# Docker self-hosted
docker-compose down && docker-compose up -d --build previous-tag
```

### Check System Health
```bash
# DO App Platform
doctl apps logs <app-id> --follow

# Supabase
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM task_queue WHERE status='processing';"

# Docker
docker-compose logs -f --tail=100
```

### Restore Database
```bash
# Supabase
psql "$POSTGRES_URL" < backups/latest.sql

# Odoo.sh
# Use web interface: Database Manager → Restore
```

---

## Performance Targets

| Metric | Target (P95) | Check Command |
|--------|--------------|---------------|
| OCR Processing | <30s | `bash scripts/benchmark_ocr.sh` |
| Module Scaffolding | <5s | `bash scripts/benchmark_scaffolding.sh` |
| Eval Suite | <2min | `cd evals && time bash scripts/run_all_scenarios.sh` |
| Research | <10min | `time python3 auto_research.py --domain oca` |

---

## Cost Monitoring

```bash
# Daily check
curl -s https://api.deepseek.com/v1/usage \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" | jq

# Weekly report
bash scripts/weekly_cost_report.sh

# Target: <$20/month
# Typical: $8/month (DeepSeek $1-2 + DO $5 + Supabase $0)
```

---

## Knowledge Base Workflow

### Add Citation
```bash
cat >> knowledge/notes/$(date +%Y-%m-%d).md <<'EOF'
## [Pattern Name]
- Link: [URL]
- Takeaway: [one-liner]
- Application: odoo-module-dev
- Quality Score: [60-100]
- Date: $(date +%Y-%m-%d)
EOF
```

### Update ORM Library
```bash
# Add to knowledge/patterns/orm_library.md
# Use existing patterns as template
```

### Run Research Automation
```bash
cd knowledge/scripts
python3 auto_research.py --domain oca --query "your query" --limit 5
```

---

## Eval Scenarios

```bash
# Run specific scenario
cd evals && bash scripts/01_oca_scaffolding.sh

# Run all scenarios
bash scripts/run_all_scenarios.sh

# Expected: ≥95% pass rate
```

---

## File Locations

| File | Path |
|------|------|
| Skills | `~/.cline/skills/odoo-expertise/` |
| Knowledge Base | `~/ai-agency/agents/odoo-expertise/knowledge/` |
| Evals | `~/ai-agency/agents/odoo-expertise/evals/` |
| Custom Modules | `~/ai-agency/agents/odoo-expertise/custom_addons/` |
| Scripts | `~/ai-agency/agents/odoo-expertise/scripts/` |
| Spec-Kit | `~/ai-agency/agents/odoo-expertise/spec/` |

---

## Key URLs

| Resource | URL |
|----------|-----|
| OCA Guidelines | https://github.com/OCA/odoo-community.org |
| Odoo 16 Docs | https://www.odoo.com/documentation/16.0/ |
| Odoo 17 Docs | https://www.odoo.com/documentation/17.0/ |
| Odoo 19 Docs | https://www.odoo.com/documentation/19.0/ |
| Reddit r/odoo | https://www.reddit.com/r/odoo/ |
| Stack Overflow | https://stackoverflow.com/questions/tagged/odoo |
| DeepSeek API | https://api.deepseek.com/ |

---

## Checklist Templates

### Daily
- [ ] Morning startup (10 min)
- [ ] Update knowledge base (5 min)
- [ ] Development workflow (per module)
- [ ] Document discoveries (10 min)
- [ ] Run local evals (10 min)
- [ ] Check API costs (2 min)

### Weekly
- [ ] Knowledge base review (30 min)
- [ ] Update ORM library (20 min)
- [ ] Review eval pass rates (10 min)
- [ ] Run full benchmark suite (30 min)
- [ ] Check API spending (5 min)

### Monthly
- [ ] Generate cost report (15 min)
- [ ] Review performance metrics (20 min)
- [ ] Update documentation (30 min)
- [ ] Archive old database records (10 min)
- [ ] Plan optimizations (1 hour)

---

## Common Pitfalls

❌ **Don't**:
- Access `record.line_ids` in loops (N+1 query)
- Use `search_count()` in computed fields
- Forget `if not self: return` in @api.depends
- Hardcode secrets in Dockerfile or code
- Skip pre-commit hooks before pushing
- Use DeepSeek R1 for simple operations

✅ **Do**:
- Use `read_group()` for aggregations
- Always validate with `assertQueryCount`
- Add `if not self: return` to all compute methods
- Store secrets in environment variables
- Run `pre-commit run --all-files` before commit
- Default to DeepSeek v3.1, escalate to R1 only for planning

---

## Support & Resources

- **Full Documentation**: See `README.md` and `docs/*.md`
- **Research**: `cline-odoo "research odoo [question]"`
- **Troubleshooting**: See `README.md` troubleshooting section
- **Cost Details**: See `docs/COST_ANALYSIS.md`
- **Performance**: See `docs/PERFORMANCE_BENCHMARKS.md`
- **Workflows**: See `docs/DAILY_USAGE.md`

---

**Print this page and keep it handy! ⚡**

**Generated**: 2025-11-01 | **Framework**: Cline CLI + DeepSeek API + Claude Code
