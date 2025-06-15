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
