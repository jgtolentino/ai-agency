import React, { useState, useEffect } from 'react';
import { fetchLearnBotTip } from '../utils/learnbot';
import { logMemory, getMemory } from '../utils/memory';

interface LearnBotTooltipProps {
  trigger: React.ReactNode;
  context: string;
  userAction?: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  context?: string;
}

export const LearnBotTooltip: React.FC<LearnBotTooltipProps> = ({
  trigger,
  context,
  userAction
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [tip, setTip] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [chatMode, setChatMode] = useState(false);

  // Load previous chat history from memory
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const memory = await getMemory('learnbot-chat', context);
        if (memory?.messages) {
          setChatMessages(memory.messages);
        }
      } catch (err) {
        console.warn('Failed to load chat history:', err);
      }
    };
    
    if (isOpen) {
      loadChatHistory();
    }
  }, [isOpen, context]);

  // Save chat to memory when messages change
  useEffect(() => {
    if (chatMessages.length > 0) {
      logMemory('learnbot-chat', {
        context,
        messages: chatMessages,
        lastUpdated: new Date().toISOString()
      });
    }
  }, [chatMessages, context]);

  const fetchTip = async () => {
    setLoading(true);
    setError('');
    
    try {
      const tipContent = await fetchLearnBotTip(context, userAction);
      setTip(tipContent);
    } catch (err) {
      setError('Failed to load tip. Please try again.');
      console.error('LearnBot tip error:', err);
    } finally {
      setLoading(false);
    }
  };

  const sendChatMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
      context
    };

    setChatMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      // Fetch contextual response from LearnBot RAG
      const response = await fetchLearnBotTip(context, inputValue);
      
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response,
        timestamp: new Date(),
        context
      };

      setChatMessages(prev => [...prev, botMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try asking again.',
        timestamp: new Date(),
        context
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  useEffect(() => {
    if (isOpen && !chatMode) {
      fetchTip();
    }
  }, [isOpen, context, userAction, chatMode]);

  return (
    <div className="relative inline-block">
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="cursor-pointer"
      >
        {trigger}
      </div>
      
      {isOpen && (
        <div className="absolute z-50 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4 mt-2 right-0">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">L</span>
              </div>
              <span className="font-medium text-gray-800">LearnBot</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setChatMode(!chatMode)}
                className={`px-2 py-1 text-xs rounded ${
                  chatMode 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                {chatMode ? 'Tip' : 'Chat'}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
          </div>

          {!chatMode ? (
            // Tip Mode
            <div className="space-y-3">
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  <span className="text-sm text-gray-600">Loading tip...</span>
                </div>
              ) : error ? (
                <div className="text-sm text-red-600">{error}</div>
              ) : tip ? (
                <div className="text-sm text-gray-700 leading-relaxed">
                  {tip}
                </div>
              ) : null}
              
              <div className="text-xs text-gray-500 border-t pt-2">
                💡 Context: {context}
              </div>
            </div>
          ) : (
            // Chat Mode
            <div className="space-y-3">
              <div className="h-40 overflow-y-auto space-y-2 border border-gray-100 rounded p-2">
                {chatMessages.length === 0 ? (
                  <div className="text-sm text-gray-500 text-center py-4">
                    Ask me anything about this feature!
                  </div>
                ) : (
                  chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`text-sm p-2 rounded ${
                        message.type === 'user'
                          ? 'bg-blue-100 text-blue-800 ml-4'
                          : 'bg-gray-100 text-gray-700 mr-4'
                      }`}
                    >
                      {message.content}
                    </div>
                  ))
                )}
                {loading && (
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <div className="animate-spin w-3 h-3 border border-blue-500 border-t-transparent rounded-full"></div>
                    <span>LearnBot is thinking...</span>
                  </div>
                )}
              </div>
              
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask LearnBot..."
                  className="flex-1 px-3 py-1 text-sm border border-gray-200 rounded focus:outline-none focus:border-blue-400"
                  disabled={loading}
                />
                <button
                  onClick={sendChatMessage}
                  disabled={loading || !inputValue.trim()}
                  className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};