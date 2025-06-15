# 🤖 AI Agency Canonical Runtime

[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green)]()
[![Version](https://img.shields.io/badge/Version-2.1.0-blue)]()
[![Agents](https://img.shields.io/badge/Agents-6%20Configured-orange)]()
[![AI Stack](https://img.shields.io/badge/AI%20Stack-Complete-purple)]()

## 🎯 **Complete AI Agent Orchestration System with Full Interaction Stack**

The **AI Agency Canonical Runtime** serves as the unified control center for all TBWA AI-powered platforms with **full AI interaction stack parity** — featuring LearnBot with RAG, RetailBot validation, Vibe TestBot QA, and Supabase memory logging. Better than Databricks One.

### 🚀 **Key Features**

- **🧠 Multi-Agent Orchestration** → 6 production-ready AI agents
- **💬 RAG-Powered LearnBot** → Interactive learning with contextual memory
- **✅ RetailBot Validation** → AI-powered insight card validation
- **🎯 Vibe TestBot QA** → Real-time development quality assurance
- **💾 Supabase Memory** → Persistent chat logging and encrypted storage
- **🔄 Git Submodule Pattern** → Canonical configuration management
- **⚡ CLI Automation** → Setup, sync, and deployment scripts
- **🔒 Enterprise Security** → Encryption, boundaries, access control

---

## 📁 **Repository Structure**

```bash
ai-agency-canonical/
├── agents/                    # 🤖 Agent Configurations
│   ├── scout/                # Scout Analytics Platform
│   │   ├── learnbot.yaml     # Tutorial & onboarding v2.1
│   │   ├── retailbot.yaml    # FMCG analytics v3.0
│   │   ├── vibe-testbot.yaml # AI code QA v1.2
│   │   └── scout-ai-combo.yaml # Unified orchestration
│   ├── ces/                  # CES Campaign Intelligence
│   │   └── cesai.yaml        # Campaign analysis specialist
│   ├── shared/               # Cross-platform utilities
│   │   └── context-manager.yaml # Memory management
│   └── VibeTestBot.ts        # 🎯 Dev runtime QA agent
├── components/               # ⚛️ React Components
│   ├── LearnBotTooltip.tsx   # 🧠 RAG-powered learning assistant
│   └── InsightCard.tsx       # ✅ RetailBot validation component
├── utils/                    # 🛠️ Core Utilities
│   ├── learnbot.ts          # 📚 RAG system implementation
│   ├── retailbot.ts         # 🔍 Insight validation engine
│   └── memory.ts            # 💾 Supabase memory management
├── config/                   # ⚙️ Configuration
│   └── dashboard.yaml       # 🎛️ Full AI interaction stack config
├── prompts/                  # 📝 System Prompts
├── orchestration/           # 🔄 Multi-agent Workflows
├── cli/                     # ⚡ Pulser CLI Utilities
├── scripts/                 # 🚀 Deployment Automation
│   ├── sync_agents.sh       # Sync with canonical repo
│   ├── deploy_agents.sh     # Production deployment
│   └── setup.sh             # Environment initialization
├── .pulserrc                # ⚙️ Runtime Configuration
├── .pulser_memory.json      # 🧠 Persistent Memory
├── agent_manifest.yaml     # 📋 Central Registry
├── package.json             # 📦 Dependencies
├── tsconfig.json            # 🔧 TypeScript config
└── README.md               # 📖 Documentation
```

---

## 🔧 **Quick Start**

### 1. **Initialize Environment**
```bash
git clone https://github.com/jgtolentino/ai-agency.git
cd ai-agency
npm install
./scripts/setup.sh
```

### 2. **Configure Supabase (Optional)**
```bash
# Set environment variables for persistent memory
export NEXT_PUBLIC_SUPABASE_URL="your_supabase_url"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your_supabase_key"
export MEMORY_ENCRYPTION_KEY="your_encryption_key"
```

### 3. **Load CLI Commands**
```bash
source cli/pulser_commands.sh
pulser_status  # Check agent availability
```

### 4. **Test AI Interaction Stack**
```bash
# Load Scout Analytics full combo with AI stack
pulser load scout/scout-ai-combo.yaml

# Test components
npm run dev  # Start development server
npm run build  # Build components
npm run typecheck  # Verify TypeScript
```

---

## 🤖 **AI Interaction Stack Components**

### **🧠 LearnBot with RAG**
```typescript
import { LearnBotTooltip } from './components/LearnBotTooltip';

<LearnBotTooltip 
  trigger={<button>Help</button>}
  context="dashboard-overview"
  userAction="viewing-metrics"
/>
```

**Features:**
- ✅ RAG-powered contextual tips
- ✅ Persistent chat memory with Supabase
- ✅ Real-time conversation mode
- ✅ Knowledge base integration
- ✅ Confidence scoring

### **✅ RetailBot Insight Validation**
```typescript
import { InsightCard } from './components/InsightCard';

<InsightCard
  title="Monthly Revenue"
  data={{ value: 125000, change: 12.5, unit: "$" }}
  type="metric"
  enableRetailBotValidation={true}
/>
```

**Features:**
- ✅ AI-powered data quality checks
- ✅ Business logic validation
- ✅ Confidence scoring
- ✅ Alternative view suggestions
- ✅ Real-time insight analysis

### **🎯 Vibe TestBot Development QA**
```typescript
import { createVibeTestBot } from './agents/VibeTestBot';

const vibeBot = createVibeTestBot({
  mode: 'vibe',
  enableRealTime: true,
  tikTokMode: true
});

await vibeBot.startSession('dev');
const issues = await vibeBot.analyzeCode(code, 'component.tsx');
```

**Features:**
- ✅ Real-time code analysis
- ✅ TikTok-style feedback
- ✅ Performance monitoring
- ✅ Fix suggestions
- ✅ Vibe scoring system

### **💾 Supabase Memory Integration**
```typescript
import { logChatMessage, getMemory } from './utils/memory';

// Log chat interactions
await logChatMessage('learnbot', 'user', 'How do I filter data?', {
  sessionId: 'session-123',
  context: 'dashboard-filters'
});

// Retrieve persistent memory
const memory = await getMemory('user-preferences');
```

**Features:**
- ✅ Encrypted memory storage
- ✅ Chat session logging
- ✅ Cross-agent memory sharing
- ✅ Automatic cleanup
- ✅ Performance analytics

---

## 🔗 **Integration Pattern**

### **Add to Existing Projects**

For any project (e.g., scout-mvp, ces-platform):

```bash
cd ~/your-project-root
git submodule add https://github.com/jgtolentino/ai-agency.git ai-agency
git submodule update --init --recursive
```

### **Configure AI Interaction Stack**

In your project's configuration:
```yaml
# .pulserrc
cwd_lock: ai-agency
agent_dir: ai-agency/agents
memory_file: ai-agency/.pulser_memory.json
platform: scout

# Enable AI interaction stack
features:
  learnbot_rag: true
  retailbot_validation: true
  vibe_testbot_qa: true
  chat_memory: true
```

### **Import Components**

```typescript
// Import AI components
import { LearnBotTooltip } from '../ai-agency/components/LearnBotTooltip';
import { InsightCard } from '../ai-agency/components/InsightCard';
import { createVibeTestBot } from '../ai-agency/agents/VibeTestBot';

// Import utilities
import { logMemory, getChatHistory } from '../ai-agency/utils/memory';
import { validateInsight } from '../ai-agency/utils/retailbot';
import { fetchLearnBotTip } from '../ai-agency/utils/learnbot';
```

---

## 🎛️ **Dashboard Configuration**

The complete AI interaction stack is configured via `config/dashboard.yaml`:

```yaml
dashboard_config:
  ai_assistant:
    enabled: true
    floating_panel: true
    agents:
      learnbot:
        rag_enabled: true
        chat_memory: true
      retailbot:
        validation_enabled: true
        auto_validate: true
      vibe_testbot:
        real_time_enabled: true
        tiktok_style: true

  memory:
    provider: "supabase"
    encryption_enabled: true
    chat_logging: true

  features:
    learnbot_rag: true
    retailbot_validation: true
    vibe_testbot_qa: true
    real_time_updates: true
```

---

## 🛠️ **Development Commands**

```bash
# Environment Management
npm install                     # Install dependencies
npm run setup                   # Initialize environment
npm run sync                    # Sync with latest configurations

# Development
npm run dev                     # Start development mode
npm run build                   # Build components
npm run typecheck               # TypeScript validation
npm run lint                    # Code quality check
npm run test                    # Run tests

# Agent Operations
pulser_status                   # Check agent status
pulser_list                     # List available agents
pulser load <agent_config>      # Load specific agent

# Deployment
npm run deploy                  # Deploy to production
./scripts/deploy_agents.sh --env production --agents scout/scout-ai-combo
```

---

## 📊 **AI Interaction Stack Features**

### ✅ **Complete Implementation**
- [x] **LearnBot RAG System** → Knowledge retrieval with contextual memory
- [x] **RetailBot Validation** → AI-powered insight card validation
- [x] **Vibe TestBot QA** → Real-time development quality assurance
- [x] **Supabase Memory** → Persistent chat logging and encryption
- [x] **React Components** → Ready-to-use UI components
- [x] **TypeScript Support** → Full type safety and intellisense
- [x] **Configuration Management** → YAML-based dashboard config
- [x] **Performance Monitoring** → Real-time metrics and analytics

### 🚀 **Better Than Databricks One**
- **Advanced RAG Integration** → Context-aware knowledge retrieval
- **Multi-Agent Orchestration** → Seamless agent coordination
- **Real-Time QA** → Live code analysis and feedback
- **Persistent Memory** → Cross-session context retention
- **TikTok-Style UX** → Engaging developer experience
- **Enterprise Security** → Encryption and access control
- **Git Submodule Pattern** → Scalable integration architecture

---

## 🔒 **Security & Performance**

### **Security Features**
- **Memory Encryption** → AES encryption for sensitive data
- **Access Control** → Role-based agent permissions
- **Data Privacy** → GDPR-compliant memory management
- **Rate Limiting** → API protection and abuse prevention
- **Session Management** → Secure chat session handling

### **Performance Optimizations**
- **Lazy Loading** → Components load on demand
- **Memory Cleanup** → Automatic memory management
- **Caching Strategy** → Intelligent response caching
- **Bundle Optimization** → Tree-shaking and code splitting
- **Real-Time Updates** → Efficient WebSocket connections

---

## 📚 **API Reference**

### **LearnBot RAG API**
```typescript
// Fetch contextual tips
const tip = await fetchLearnBotTip('dashboard-filters', 'how to filter data');

// Check knowledge availability
const hasTips = hasLearnBotTips('analytics');

// Get suggestions
const suggestions = await getLearnBotSuggestions('chart', 'revenue-chart');
```

### **RetailBot Validation API**
```typescript
// Validate insight data
const validation = await validateInsight(data, 'metric');

// Get recommendations
const recommendations = await getInsightRecommendations('trend');

// Check validation availability
const available = isValidationAvailable('forecast');
```

### **Vibe TestBot QA API**
```typescript
// Create QA bot
const vibeBot = createVibeTestBot({ mode: 'vibe' });

// Start session
const sessionId = await vibeBot.startSession('dev');

// Analyze code
const issues = await vibeBot.analyzeCode(code, 'component.tsx');

// Get session summary
const summary = await vibeBot.getSessionSummary();
```

### **Memory Management API**
```typescript
// Store/retrieve memory
await logMemory('user-state', { theme: 'dark' });
const state = await getMemory('user-state');

// Chat logging
const messageId = await logChatMessage('learnbot', 'user', 'Hello');
const history = await getChatHistory('session-123');

// Session management
const sessionId = await startChatSession('learnbot');
await endChatSession(sessionId);
```

---

## 🚀 **Deployment Workflow**

1. **Development** → Modify agents and components in ai-agency repo
2. **Testing** → Use `npm run test` and `./scripts/deploy_agents.sh --env dev --dry-run`
3. **Staging** → Deploy with `./scripts/deploy_agents.sh --env staging`
4. **Production** → Deploy with `./scripts/deploy_agents.sh --env production`
5. **Distribution** → Child projects sync via `./scripts/sync_agents.sh`

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-ai-feature`)
3. Implement your changes with proper TypeScript types
4. Add tests for new functionality
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing AI feature'`)
7. Push to the branch (`git push origin feature/amazing-ai-feature`)
8. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 **Ready for Production!**

**Repository Status:** ✅ Production Ready with Full AI Interaction Stack  
**AI Components:** 3 (LearnBot RAG + RetailBot Validation + Vibe TestBot QA)  
**Memory System:** Supabase-powered with encryption  
**Integration Pattern:** Git Submodule + React Components  
**Better Than:** Databricks One ✨

🚀 **The most advanced AI interaction stack for enterprise dashboards!**