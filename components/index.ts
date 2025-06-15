// Retail Intelligence Dashboard - Component Exports
// Client-safe components for external deployment

// AI Assistant Components
export { LearnBotTooltip as LearningAssistant } from './LearnBotTooltip';
export { InsightCard as ValidatedInsightCard } from './InsightCard';

// Type Exports for Client Use
export type {
  InsightData,
  InsightValidation
} from '../utils/retailbot';

export type {
  ChatMessage,
  ChatSession,
  MemoryConfig
} from '../utils/memory';

// Client-safe utility exports
export { 
  fetchLearnBotTip as fetchAssistanceTip,
  hasLearnBotTips as hasAssistanceTips,
  getLearnBotSuggestions as getAssistanceSuggestions
} from '../utils/learnbot';

export {
  validateInsight as validateDataInsight,
  getInsightRecommendations,
  isValidationAvailable
} from '../utils/retailbot';

export {
  logMemory as logData,
  getMemory as getData,
  logChatMessage as logInteraction,
  startChatSession as startSession,
  endChatSession as endSession,
  getChatHistory as getInteractionHistory
} from '../utils/memory';

export { ClientSanitizer } from '../utils/client-sanitizer';

// Client configuration
export const CLIENT_CONFIG = {
  version: '1.0.0',
  name: 'Retail Intelligence Dashboard',
  description: 'AI-powered retail analytics platform',
  
  features: {
    aiAssistance: true,
    dataValidation: true,
    qualityAssurance: true,
    secureStorage: true,
    exportCapabilities: true,
    realTimeAnalytics: true
  },
  
  components: {
    learningAssistant: 'AI-powered learning and guidance',
    insightValidation: 'Automated data quality checks',
    interactiveCharts: 'Dynamic visualization components',
    exportTools: 'Data export and reporting'
  }
} as const;