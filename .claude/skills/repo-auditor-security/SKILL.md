---
name: repo-auditor-security
description: Fast, top-10 exploitable risks across Odoo ACLs, sudo misuse, SQLi, secrets in CI, root containers, open firewalls, unencrypted backups.
version: 1.0.0
labels: [security, odoo, docker, ci, terraform]
inputs: [repo_tree, files]
outputs: [human_report_md, machine_json]
---

Return only the 10 most dangerous issues with proofs-of-risk and minimal patches.
