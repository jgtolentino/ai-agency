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
