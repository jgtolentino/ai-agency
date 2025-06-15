// LearnBot RAG System - Fetch contextual tips and responses
import { logMemory } from './memory';

interface RAGDocument {
  id: string;
  content: string;
  metadata: {
    category: string;
    tags: string[];
    relevance_score?: number;
  };
}

interface LearnBotResponse {
  tip: string;
  sources: string[];
  confidence: number;
}

// Simulated knowledge base - in production, this would connect to a vector database
const KNOWLEDGE_BASE: RAGDocument[] = [
  {
    id: 'dashboard-overview-1',
    content: 'The Scout Analytics Dashboard provides real-time insights into retail performance across multiple metrics. Use the filter controls at the top to narrow down data by region, time period, or brand category.',
    metadata: {
      category: 'dashboard',
      tags: ['overview', 'filters', 'navigation']
    }
  },
  {
    id: 'brand-performance-1',
    content: 'Brand Performance metrics show market share, growth trends, and competitive positioning. Click on any brand tile to drill down into detailed analytics including customer sentiment and purchase patterns.',
    metadata: {
      category: 'analytics',
      tags: ['brands', 'metrics', 'drill-down']
    }
  },
  {
    id: 'consumer-insights-1',
    content: 'Consumer Insights leverage AI-powered sentiment analysis and behavioral patterns. The demographic breakdowns help identify target segments and optimize marketing strategies.',
    metadata: {
      category: 'insights',
      tags: ['consumers', 'ai', 'demographics']
    }
  },
  {
    id: 'export-data-1',
    content: 'Export functionality supports multiple formats: CSV for raw data analysis, PDF for presentations, and API endpoints for automated integrations. Use the export button in the top-right corner of any widget.',
    metadata: {
      category: 'features',
      tags: ['export', 'csv', 'pdf', 'api']
    }
  },
  {
    id: 'realtime-updates-1',
    content: 'Dashboard data refreshes automatically every 5 minutes. For immediate updates, click the refresh icon. Real-time alerts will notify you of significant changes in performance metrics.',
    metadata: {
      category: 'features',
      tags: ['realtime', 'refresh', 'alerts']
    }
  },
  {
    id: 'troubleshooting-1',
    content: 'If you encounter loading issues: 1) Check your internet connection, 2) Clear browser cache, 3) Refresh the page, 4) Contact support if problems persist. Most issues resolve with a simple page refresh.',
    metadata: {
      category: 'troubleshooting',
      tags: ['loading', 'cache', 'support']
    }
  },
  {
    id: 'keyboard-shortcuts-1',
    content: 'Keyboard shortcuts: Ctrl+F for search, Ctrl+E for export, Ctrl+R for refresh, Tab to navigate between widgets, Enter to drill down into selected items.',
    metadata: {
      category: 'productivity',
      tags: ['shortcuts', 'navigation', 'efficiency']
    }
  },
  {
    id: 'data-accuracy-1',
    content: 'Data accuracy is maintained through automated validation pipelines. All metrics are cross-referenced with multiple sources and flagged for inconsistencies. Confidence scores are displayed for predictive analytics.',
    metadata: {
      category: 'quality',
      tags: ['accuracy', 'validation', 'confidence']
    }
  }
];

// Simple text similarity scoring (in production, use vector embeddings)
function calculateRelevance(query: string, document: RAGDocument): number {
  const queryLower = query.toLowerCase();
  const contentLower = document.content.toLowerCase();
  const tagMatches = document.metadata.tags.filter(tag => 
    queryLower.includes(tag) || tag.includes(queryLower)
  ).length;
  
  const contentMatches = queryLower.split(' ').filter(word => 
    word.length > 2 && contentLower.includes(word)
  ).length;
  
  return (tagMatches * 3 + contentMatches) / (queryLower.split(' ').length + 1);
}

// Retrieve relevant documents based on context and query
function retrieveRelevantDocuments(context: string, query?: string, topK: number = 3): RAGDocument[] {
  const searchQuery = query || context;
  
  return KNOWLEDGE_BASE
    .map(doc => ({
      ...doc,
      metadata: {
        ...doc.metadata,
        relevance_score: calculateRelevance(searchQuery, doc)
      }
    }))
    .filter(doc => doc.metadata.relevance_score! > 0)
    .sort((a, b) => b.metadata.relevance_score! - a.metadata.relevance_score!)
    .slice(0, topK);
}

// Generate contextual response using retrieved documents
function generateResponse(context: string, query: string | undefined, documents: RAGDocument[]): LearnBotResponse {
  if (documents.length === 0) {
    return {
      tip: "I don't have specific information about that topic yet. Try exploring the dashboard features or ask about analytics, insights, or data export.",
      sources: [],
      confidence: 0.1
    };
  }

  // Combine information from relevant documents
  const combinedContent = documents.map(doc => doc.content).join(' ');
  const sources = documents.map(doc => doc.metadata.category);
  const avgConfidence = documents.reduce((sum, doc) => sum + (doc.metadata.relevance_score || 0), 0) / documents.length;

  // Create contextual tip based on the query type
  let tip = '';
  
  if (query?.toLowerCase().includes('how')) {
    tip = `Here's how to work with this feature: ${documents[0].content}`;
  } else if (query?.toLowerCase().includes('what')) {
    tip = `${documents[0].content} ${documents.length > 1 ? `Also, ${documents[1].content}` : ''}`;
  } else if (query?.toLowerCase().includes('error') || query?.toLowerCase().includes('problem')) {
    const troubleshootingDoc = documents.find(doc => doc.metadata.category === 'troubleshooting');
    tip = troubleshootingDoc?.content || documents[0].content;
  } else {
    // Default context-based response
    tip = documents[0].content;
    if (documents.length > 1 && avgConfidence > 0.5) {
      tip += ` Additional tip: ${documents[1].content}`;
    }
  }

  return {
    tip,
    sources,
    confidence: Math.min(avgConfidence, 1.0)
  };
}

// Main function to fetch LearnBot tips
export async function fetchLearnBotTip(context: string, userAction?: string): Promise<string> {
  try {
    // Log the interaction for analytics
    await logMemory('learnbot-interactions', {
      context,
      userAction,
      timestamp: new Date().toISOString()
    });

    // Retrieve relevant documents
    const relevantDocs = retrieveRelevantDocuments(context, userAction);
    
    // Generate response
    const response = generateResponse(context, userAction, relevantDocs);
    
    // Log the response for improvement tracking
    await logMemory('learnbot-responses', {
      context,
      userAction,
      response: response.tip,
      confidence: response.confidence,
      sources: response.sources,
      timestamp: new Date().toISOString()
    });

    return response.tip;
    
  } catch (error) {
    console.error('LearnBot RAG error:', error);
    
    // Fallback responses based on context
    const fallbackTips: Record<string, string> = {
      'dashboard': 'Use the navigation menu to explore different sections of the dashboard. Hover over charts for detailed information.',
      'analytics': 'Click on metrics to drill down into detailed views. Use filters to narrow down your analysis scope.',
      'export': 'Look for the download or export button in the top-right corner of widgets to save data.',
      'insights': 'Consumer insights are updated daily. Check the timestamp to see when data was last refreshed.',
      'default': 'Explore the dashboard features by clicking on different sections. Each widget provides interactive insights.'
    };

    return fallbackTips[context] || fallbackTips.default;
  }
}

// Get LearnBot suggestions for a specific UI element
export async function getLearnBotSuggestions(elementType: string, elementId: string): Promise<string[]> {
  const suggestions: Record<string, string[]> = {
    'button': [
      'Click this button to perform the action',
      'Right-click for additional options',
      'Use keyboard shortcuts for faster access'
    ],
    'chart': [
      'Hover over data points for detailed values',
      'Click and drag to zoom into specific time periods',
      'Double-click to reset zoom level'
    ],
    'filter': [
      'Use multiple filters to narrow down results',
      'Clear filters using the reset button',
      'Save filter combinations for future use'
    ],
    'widget': [
      'Drag widgets to rearrange dashboard layout',
      'Click the gear icon to configure widget settings',
      'Use the expand button for full-screen view'
    ]
  };

  return suggestions[elementType] || ['Interact with this element to explore its features'];
}

// Check if LearnBot has tips for a specific context
export function hasLearnBotTips(context: string): boolean {
  return KNOWLEDGE_BASE.some(doc => 
    doc.metadata.category === context || 
    doc.metadata.tags.some(tag => context.toLowerCase().includes(tag))
  );
}