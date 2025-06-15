#!/bin/bash
# AI Agency - Agent Sync Script
# Synchronizes latest agent configurations from canonical repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
CANONICAL_REPO="git@github.com:jgtolentino/ai-agency.git"
SYNC_BRANCH="main"
BACKUP_DIR=".agent_backups"

echo -e "${PURPLE}"
cat << "EOF"
    ╭─────────────────────────────────────╮
    │        AI AGENCY SYNC TOOL          │
    │     Canonical Agent Repository      │
    ╰─────────────────────────────────────╯
EOF
echo -e "${NC}"

# Function to log with timestamp
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[${timestamp}] ℹ️  ${message}${NC}"
            ;;
        "WARN")
            echo -e "${YELLOW}[${timestamp}] ⚠️  ${message}${NC}"
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] ❌ ${message}${NC}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[${timestamp}] ✅ ${message}${NC}"
            ;;
    esac
}

# Check if we're in ai-agency directory or submodule
check_location() {
    if [[ -f ".pulserrc" && -f "agent_manifest.yaml" ]]; then
        log "INFO" "Found ai-agency configuration"
        return 0
    elif [[ -d "ai-agency" ]]; then
        log "INFO" "Found ai-agency submodule, switching directory"
        cd ai-agency
        return 0
    else
        log "ERROR" "Not in ai-agency directory or submodule not found"
        log "INFO" "Please run from ai-agency root or parent directory with ai-agency submodule"
        exit 1
    fi
}

# Create backup of current agents
backup_current_agents() {
    if [[ -d "agents" ]]; then
        log "INFO" "Creating backup of current agents..."
        
        mkdir -p "$BACKUP_DIR"
        local backup_name="agents_backup_$(date +%Y%m%d_%H%M%S)"
        
        cp -r agents "$BACKUP_DIR/$backup_name"
        log "SUCCESS" "Backup created: $BACKUP_DIR/$backup_name"
    fi
}

# Sync with canonical repository
sync_with_canonical() {
    log "INFO" "Syncing with canonical agent repository..."
    
    # Check if git repo exists
    if [[ ! -d ".git" ]]; then
        log "ERROR" "Not a git repository. Please initialize or clone ai-agency first."
        exit 1
    fi
    
    # Fetch latest changes
    log "INFO" "Fetching latest changes from $SYNC_BRANCH..."
    git fetch origin $SYNC_BRANCH
    
    # Check for conflicts
    local conflicts=$(git diff HEAD origin/$SYNC_BRANCH --name-only)
    if [[ -n "$conflicts" ]]; then
        log "WARN" "Potential conflicts detected in:"
        echo "$conflicts"
        read -p "Continue with sync? [y/N]: " confirm
        if [[ $confirm != [yY] ]]; then
            log "INFO" "Sync cancelled by user"
            exit 0
        fi
    fi
    
    # Pull latest changes
    log "INFO" "Pulling latest agent configurations..."
    git pull origin $SYNC_BRANCH
    
    log "SUCCESS" "Sync completed successfully"
}

# Validate agent configurations
validate_agents() {
    log "INFO" "Validating agent configurations..."
    
    local validation_errors=0
    
    # Check manifest file
    if [[ ! -f "agent_manifest.yaml" ]]; then
        log "ERROR" "agent_manifest.yaml not found"
        ((validation_errors++))
    fi
    
    # Check pulser config
    if [[ ! -f ".pulserrc" ]]; then
        log "ERROR" ".pulserrc configuration not found"
        ((validation_errors++))
    fi
    
    # Check agent directories
    for dir in agents/scout agents/ces agents/shared; do
        if [[ ! -d "$dir" ]]; then
            log "ERROR" "Required directory not found: $dir"
            ((validation_errors++))
        fi
    done
    
    # Validate individual agent files
    find agents -name "*.yaml" -type f | while read -r agent_file; do
        if ! grep -q "agent_name:" "$agent_file"; then
            log "ERROR" "Invalid agent configuration: $agent_file"
            ((validation_errors++))
        fi
    done
    
    if [[ $validation_errors -eq 0 ]]; then
        log "SUCCESS" "All agent configurations are valid"
        return 0
    else
        log "ERROR" "$validation_errors validation errors found"
        return 1
    fi
}

# Update agent manifest
update_manifest() {
    log "INFO" "Updating agent manifest..."
    
    # Count agents
    local total_agents=$(find agents -name "*.yaml" -type f | wc -l)
    
    # Update manifest timestamp
    if [[ -f "agent_manifest.yaml" ]]; then
        local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        sed -i.bak "s/last_updated:.*/last_updated: \"$timestamp\"/" agent_manifest.yaml
        sed -i.bak "s/total_agents:.*/total_agents: $total_agents/" agent_manifest.yaml
        rm agent_manifest.yaml.bak
        
        log "SUCCESS" "Manifest updated: $total_agents agents registered"
    fi
}

# Display sync summary
show_summary() {
    log "INFO" "Sync Summary:"
    echo
    echo "📊 Agent Statistics:"
    
    if [[ -d "agents/scout" ]]; then
        local scout_count=$(find agents/scout -name "*.yaml" -type f | wc -l)
        echo "   Scout Agents: $scout_count"
    fi
    
    if [[ -d "agents/ces" ]]; then
        local ces_count=$(find agents/ces -name "*.yaml" -type f | wc -l)
        echo "   CES Agents: $ces_count"
    fi
    
    if [[ -d "agents/shared" ]]; then
        local shared_count=$(find agents/shared -name "*.yaml" -type f | wc -l)
        echo "   Shared Agents: $shared_count"
    fi
    
    echo
    echo "🔧 Available CLI Commands:"
    echo "   pulser load scout/scout-ai-combo.yaml"
    echo "   pulser load ces/cesai.yaml"
    echo "   pulser load shared/context-manager.yaml"
    echo
    
    log "SUCCESS" "AI Agency sync completed successfully!"
    echo -e "${PURPLE}Ready to power your AI-driven platforms! 🚀${NC}"
}

# Main execution
main() {
    log "INFO" "Starting AI Agency agent sync..."
    
    check_location
    backup_current_agents
    sync_with_canonical
    validate_agents || exit 1
    update_manifest
    show_summary
}

# Run main function
main "$@"