# 🤖 AI Agency - Canonical Agent Runtime

**Standalone Pulser agent runtime for TBWA AI-powered platforms**

This repository serves as the **canonical root** for all AI agent configurations, orchestration logic, and runtime infrastructure used across TBWA's AI-powered platforms including Scout Analytics, CES Campaign Intelligence, and other client projects.

## 🏗️ Repository Structure

```bash
ai-agency/
├── agents/                     # Agent configurations
│   ├── ces/                   # CES Campaign Intelligence agents
│   ├── scout/                 # Scout Analytics agents  
│   └── shared/                # Cross-platform shared agents
├── prompts/                   # System prompts and templates
├── orchestration/            # Multi-agent workflow configurations
├── cli/                      # Pulser CLI commands and utilities
├── scripts/                  # Deployment and sync utilities
├── .pulserrc                 # Pulser runtime configuration
├── .pulser_memory.json      # Persistent agent memory
└── agent_manifest.yaml     # Central agent registry
```

## 🚀 Usage Patterns

### As Git Submodule

Add to any project:

```bash
cd ~/your-project
git submodule add git@github.com:jgtolentino/ai-agency.git ai-agency
```

### Project Configuration

In your project's `.pulserrc`:

```yaml
cwd_lock: ai-agency
agent_dir: ai-agency/agents
memory_file: ai-agency/.pulser_memory.json
```

### Sync Latest Agents

```bash
cd ai-agency
git pull origin main
echo "✅ Synced with latest agents and orchestration"
```

## 🤖 Available Agents

### Scout Analytics Combo
- **LearnBot v2.1** - Interactive dashboard tutorials
- **RetailBot v3.0** - FMCG analytics specialist  
- **Vibe TestBot v1.2** - TikTok-style AI code QA

### CES Campaign Intelligence
- **CESai v3.0** - Campaign analysis and optimization
- **Creative Analyzer** - Visual content intelligence
- **Performance Predictor** - ROI and KPI forecasting

### Shared Utilities
- **Context Manager** - Cross-session memory management
- **Sync Agent** - Multi-platform orchestration
- **QA Validator** - Code and data quality assurance

## 🔧 Integration Examples

### Scout Analytics Platform
```yaml
# scout-mvp/.pulserrc
agents:
  - scout/learnbot.yaml
  - scout/retailbot.yaml
  - scout/vibe-testbot.yaml
  - shared/context-manager.yaml
```

### CES Campaign Platform  
```yaml
# ces-platform/.pulserrc  
agents:
  - ces/cesai.yaml
  - ces/creative-analyzer.yaml
  - shared/sync-agent.yaml
```

## 📁 Agent Directory Structure

```bash
agents/
├── ces/
│   ├── cesai.yaml              # Campaign analysis AI
│   ├── creative-analyzer.yaml  # Visual content AI
│   └── performance-predictor.yaml
├── scout/
│   ├── learnbot.yaml          # Tutorial & onboarding
│   ├── retailbot.yaml         # FMCG analytics specialist
│   ├── vibe-testbot.yaml      # AI code QA
│   └── scout-ai-combo.yaml    # Unified configuration
└── shared/
    ├── context-manager.yaml   # Memory management
    ├── sync-agent.yaml       # Multi-platform sync
    └── qa-validator.yaml     # Quality assurance
```

## 🎯 Key Features

- **🔒 Boundary Control** - Each project locks to specific agent scope
- **🔄 Auto-Sync** - Pull latest configurations without conflicts  
- **🧠 Persistent Memory** - Cross-session context retention
- **⚡ Dynamic Loading** - Runtime agent initialization
- **🌐 Multi-Platform** - Works across Scout, CES, and custom projects
- **📊 Monitoring** - Built-in performance tracking and reporting

## 🛠️ CLI Commands

```bash
# Initialize agent runtime
pulser init --config ai-agency/.pulserrc

# Launch specific agent combo
pulser load scout/scout-ai-combo.yaml

# Sync with latest configurations
./scripts/sync_agents.sh

# Deploy agents to production
./scripts/deploy_agents.sh --env production
```

## 🔧 Development Workflow

1. **Agent Development** - Create/modify agents in appropriate directories
2. **Testing** - Use `scripts/test_agents.sh` for validation
3. **Deployment** - Push to main branch for distribution
4. **Sync** - Child projects pull latest via Git submodule

## 📋 Agent Manifest

The `agent_manifest.yaml` provides centralized registration of all available agents with metadata, capabilities, and compatibility information.

## 🚀 Quick Start

```bash
# Clone the canonical runtime
git clone git@github.com:jgtolentino/ai-agency.git

# Initialize agent environment  
cd ai-agency
./scripts/setup.sh

# Test agent configurations
./scripts/test_agents.sh

# Ready to integrate with projects!
```

## 📖 Documentation

- [Agent Configuration Guide](docs/AGENT_CONFIG.md)
- [Orchestration Patterns](docs/ORCHESTRATION.md)  
- [CLI Reference](docs/CLI_REFERENCE.md)
- [Integration Examples](docs/INTEGRATION.md)

## 🤝 Contributing

1. Fork this repository
2. Create agent/orchestration in appropriate directory
3. Test with `scripts/test_agents.sh`
4. Submit PR with clear description

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Powered by InsightPulseAI • Built for TBWA • Made with ❤️**