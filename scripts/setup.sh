#!/bin/bash
# AI Agency - Setup Script
# Initializes canonical agent runtime environment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}"
cat << "EOF"
    ╭─────────────────────────────────────╮
    │       AI AGENCY SETUP WIZARD       │
    │    Canonical Agent Runtime Init    │
    ╰─────────────────────────────────────╯
EOF
echo -e "${NC}"

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

# Check prerequisites
log "Checking prerequisites..."

# Node.js check
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Git check
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠️  Git not found. Please install Git first.${NC}"
    exit 1
fi

log "✅ Prerequisites satisfied"

# Initialize git repository if needed
if [[ ! -d ".git" ]]; then
    log "Initializing git repository..."
    git init
    git add .
    git commit -m "🎯 Initial commit - AI Agency canonical runtime"
fi

# Create necessary directories
log "Creating directory structure..."
mkdir -p {prompts,orchestration,cli,docs,.agent_backups}

# Set up CLI commands
log "Setting up CLI commands..."
cat > cli/pulser_commands.sh << 'EOF'
#!/bin/bash
# Pulser CLI Commands for AI Agency

# Load agent configuration
pulser_load() {
    local agent_config="$1"
    if [[ -f "agents/$agent_config" ]]; then
        echo "Loading agent: $agent_config"
        # Add actual loading logic here
    else
        echo "Agent configuration not found: $agent_config"
        return 1
    fi
}

# List available agents
pulser_list() {
    echo "Available agents:"
    find agents -name "*.yaml" -type f | sed 's|^agents/||'
}

# Agent status check
pulser_status() {
    echo "Agent runtime status:"
    echo "- Memory file: $(test -f .pulser_memory.json && echo "✅" || echo "❌")"
    echo "- Config file: $(test -f .pulserrc && echo "✅" || echo "❌")"
    echo "- Agents: $(find agents -name "*.yaml" | wc -l) configured"
}

# Export functions
alias pulser-load='pulser_load'
alias pulser-list='pulser_list' 
alias pulser-status='pulser_status'
EOF

chmod +x cli/pulser_commands.sh

# Create basic prompts
log "Setting up base prompts..."
cat > prompts/system_base.txt << 'EOF'
You are an AI assistant integrated into the TBWA AI Agency platform. You help users with:

1. Dashboard navigation and tutorials
2. Data analysis and insights
3. Code quality and testing
4. Campaign analysis and optimization

Always maintain a helpful, professional tone and provide actionable insights.
EOF

# Create orchestration example
log "Setting up orchestration examples..."
cat > orchestration/basic_workflow.yaml << 'EOF'
workflow_name: Basic Multi-Agent Workflow
version: 1.0
description: Example orchestration workflow

agents:
  - name: context-manager
    role: coordinator
    priority: 1
  
  - name: primary-agent
    role: executor
    priority: 2
    depends_on: [context-manager]

execution:
  type: sequential
  timeout: 300s
  
steps:
  - initialize_context
  - execute_primary_task
  - save_results
  - cleanup
EOF

# Create documentation
log "Creating documentation..."
cat > docs/QUICK_START.md << 'EOF'
# AI Agency Quick Start

## Setup
```bash
./scripts/setup.sh
```

## Usage
```bash
# List available agents
find agents -name "*.yaml"

# Load agent configuration
source cli/pulser_commands.sh
pulser-load scout/learnbot.yaml

# Check status
pulser-status
```

## Directory Structure
- `agents/` - Agent configurations
- `prompts/` - System prompts
- `orchestration/` - Multi-agent workflows
- `cli/` - Command line utilities
- `scripts/` - Setup and deployment tools
EOF

# Set up environment
log "Configuring environment..."
echo "export AI_AGENCY_ROOT=\"$(pwd)\"" > .env
echo "export PULSER_CONFIG=\"$(pwd)/.pulserrc\"" >> .env

# Final validation
log "Validating setup..."
if [[ -f ".pulserrc" && -f "agent_manifest.yaml" && -d "agents" ]]; then
    log "✅ AI Agency setup completed successfully!"
    echo
    echo -e "${BLUE}📚 Next steps:${NC}"
    echo "1. Source the environment: source .env"
    echo "2. Load CLI commands: source cli/pulser_commands.sh"
    echo "3. Check agent status: pulser-status"
    echo "4. Sync with remote: ./scripts/sync_agents.sh"
    echo
    echo -e "${PURPLE}🚀 Ready to power your AI-driven platforms!${NC}"
else
    echo -e "${YELLOW}⚠️  Setup completed with warnings. Please check configuration files.${NC}"
fi