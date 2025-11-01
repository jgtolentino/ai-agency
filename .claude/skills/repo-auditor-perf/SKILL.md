---
name: repo-auditor-perf
description: Performance pass for Odoo and DevOps: n+1 queries, missing indexes, heavy crons, chatty RPC, image bloat.
version: 1.0.0
labels: [performance, odoo, docker]
inputs: [repo_tree, files]
outputs: [human_report_md, machine_json]
---
