// AI Agency Memory Management with Supabase Integration
// Provides persistent memory for all AI agents with encryption and chat logging

import { createClient, SupabaseClient } from '@supabase/supabase-js';

// Memory configuration
interface MemoryConfig {
  supabaseUrl?: string;
  supabaseKey?: string;
  encryptionEnabled: boolean;
  memoryRetention: number; // days
  maxMemorySize: number; // MB
  enableChatLogging: boolean;
}

// Memory entry structure
interface MemoryEntry {
  id: string;
  key: string;
  data: any;
  agent_id?: string;
  session_id?: string;
  timestamp: string;
  expires_at?: string;
  encrypted: boolean;
  size_bytes: number;
  metadata?: Record<string, any>;
}

// Chat message structure for logging
interface ChatMessage {
  id: string;
  session_id: string;
  agent_name: string;
  message_type: 'user' | 'agent' | 'system';
  content: string;
  context?: string;
  timestamp: string;
  user_id?: string;
  platform?: string;
}

// Chat session structure
interface ChatSession {
  id: string;
  agent_name: string;
  user_id?: string;
  platform?: string;
  started_at: string;
  ended_at?: string;
  message_count: number;
  context?: Record<string, any>;
}

class MemoryManager {
  private supabase: SupabaseClient | null = null;
  private config: MemoryConfig;
  private localMemory: Map<string, any> = new Map();
  private encryptionKey: string = '';

  constructor(config: Partial<MemoryConfig> = {}) {
    this.config = {
      encryptionEnabled: true,
      memoryRetention: 30,
      maxMemorySize: 100,
      enableChatLogging: true,
      ...config
    };

    this.initializeSupabase();
    this.initializeEncryption();
  }

  // Initialize Supabase connection
  private initializeSupabase() {
    try {
      const supabaseUrl = this.config.supabaseUrl || process.env.NEXT_PUBLIC_SUPABASE_URL;
      const supabaseKey = this.config.supabaseKey || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

      if (supabaseUrl && supabaseKey) {
        this.supabase = createClient(supabaseUrl, supabaseKey);
        console.log('✅ Supabase memory backend connected');
      } else {
        console.warn('⚠️ Supabase credentials not found, using local memory only');
      }
    } catch (error) {
      console.error('❌ Failed to initialize Supabase:', error);
    }
  }

  // Initialize encryption
  private initializeEncryption() {
    if (this.config.encryptionEnabled) {
      // In production, use a proper key derivation function
      this.encryptionKey = process.env.MEMORY_ENCRYPTION_KEY || 'ai-agency-default-key-2024';
    }
  }

  // Simple encryption (use proper crypto in production)
  private encrypt(data: string): string {
    if (!this.config.encryptionEnabled) return data;
    
    // Simple XOR encryption for demo - use AES in production
    let encrypted = '';
    for (let i = 0; i < data.length; i++) {
      encrypted += String.fromCharCode(
        data.charCodeAt(i) ^ this.encryptionKey.charCodeAt(i % this.encryptionKey.length)
      );
    }
    return btoa(encrypted);
  }

  // Simple decryption
  private decrypt(encryptedData: string): string {
    if (!this.config.encryptionEnabled) return encryptedData;
    
    try {
      const data = atob(encryptedData);
      let decrypted = '';
      for (let i = 0; i < data.length; i++) {
        decrypted += String.fromCharCode(
          data.charCodeAt(i) ^ this.encryptionKey.charCodeAt(i % this.encryptionKey.length)
        );
      }
      return decrypted;
    } catch (error) {
      console.error('Decryption failed:', error);
      return encryptedData;
    }
  }

  // Store memory entry
  async store(key: string, data: any, options: {
    agentId?: string;
    sessionId?: string;
    ttl?: number; // seconds
    metadata?: Record<string, any>;
  } = {}): Promise<void> {
    const serializedData = JSON.stringify(data);
    const encryptedData = this.encrypt(serializedData);
    const sizeBytes = new Blob([serializedData]).size;

    const entry: MemoryEntry = {
      id: `${key}-${Date.now()}`,
      key,
      data: encryptedData,
      agent_id: options.agentId,
      session_id: options.sessionId,
      timestamp: new Date().toISOString(),
      expires_at: options.ttl ? new Date(Date.now() + options.ttl * 1000).toISOString() : undefined,
      encrypted: this.config.encryptionEnabled,
      size_bytes: sizeBytes,
      metadata: options.metadata
    };

    // Store locally
    this.localMemory.set(key, data);

    // Store in Supabase if available
    if (this.supabase) {
      try {
        const { error } = await this.supabase
          .from('ai_memory')
          .upsert(entry, { onConflict: 'key' });

        if (error) {
          console.error('Failed to store memory in Supabase:', error);
        }
      } catch (error) {
        console.error('Supabase storage error:', error);
      }
    }
  }

  // Retrieve memory entry
  async retrieve(key: string): Promise<any | null> {
    // Check local memory first
    if (this.localMemory.has(key)) {
      return this.localMemory.get(key);
    }

    // Check Supabase if available
    if (this.supabase) {
      try {
        const { data, error } = await this.supabase
          .from('ai_memory')
          .select('*')
          .eq('key', key)
          .order('timestamp', { ascending: false })
          .limit(1)
          .single();

        if (error || !data) {
          return null;
        }

        // Check expiration
        if (data.expires_at && new Date(data.expires_at) < new Date()) {
          await this.delete(key);
          return null;
        }

        // Decrypt and parse data
        const decryptedData = this.decrypt(data.data);
        const parsedData = JSON.parse(decryptedData);

        // Cache locally
        this.localMemory.set(key, parsedData);

        return parsedData;
      } catch (error) {
        console.error('Failed to retrieve memory from Supabase:', error);
      }
    }

    return null;
  }

  // Delete memory entry
  async delete(key: string): Promise<void> {
    // Remove from local memory
    this.localMemory.delete(key);

    // Remove from Supabase if available
    if (this.supabase) {
      try {
        await this.supabase
          .from('ai_memory')
          .delete()
          .eq('key', key);
      } catch (error) {
        console.error('Failed to delete memory from Supabase:', error);
      }
    }
  }

  // Log chat message
  async logChatMessage(
    agentName: string,
    messageType: 'user' | 'agent' | 'system',
    content: string,
    options: {
      sessionId?: string;
      userId?: string;
      platform?: string;
      context?: string;
    } = {}
  ): Promise<string> {
    if (!this.config.enableChatLogging) {
      return '';
    }

    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const message: ChatMessage = {
      id: messageId,
      session_id: options.sessionId || 'default',
      agent_name: agentName,
      message_type: messageType,
      content,
      context: options.context,
      timestamp: new Date().toISOString(),
      user_id: options.userId,
      platform: options.platform || 'ai-agency'
    };

    // Store in Supabase if available
    if (this.supabase) {
      try {
        const { error } = await this.supabase
          .from('chat_messages')
          .insert(message);

        if (error) {
          console.error('Failed to log chat message:', error);
        }
      } catch (error) {
        console.error('Chat logging error:', error);
      }
    }

    // Also store in memory for quick access
    await this.store(`chat-${messageId}`, message, {
      agentId: agentName,
      sessionId: options.sessionId,
      ttl: 86400 // 24 hours
    });

    return messageId;
  }

  // Start chat session
  async startChatSession(
    agentName: string,
    options: {
      userId?: string;
      platform?: string;
      context?: Record<string, any>;
    } = {}
  ): Promise<string> {
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const session: ChatSession = {
      id: sessionId,
      agent_name: agentName,
      user_id: options.userId,
      platform: options.platform || 'ai-agency',
      started_at: new Date().toISOString(),
      message_count: 0,
      context: options.context
    };

    // Store session in Supabase if available
    if (this.supabase) {
      try {
        const { error } = await this.supabase
          .from('chat_sessions')
          .insert(session);

        if (error) {
          console.error('Failed to create chat session:', error);
        }
      } catch (error) {
        console.error('Session creation error:', error);
      }
    }

    // Store in memory
    await this.store(`session-${sessionId}`, session, {
      agentId: agentName,
      sessionId,
      ttl: 86400 * 7 // 7 days
    });

    return sessionId;
  }

  // End chat session
  async endChatSession(sessionId: string): Promise<void> {
    const session = await this.retrieve(`session-${sessionId}`);
    if (!session) return;

    session.ended_at = new Date().toISOString();

    // Get message count
    if (this.supabase) {
      try {
        const { count } = await this.supabase
          .from('chat_messages')
          .select('*', { count: 'exact', head: true })
          .eq('session_id', sessionId);

        session.message_count = count || 0;

        // Update session in Supabase
        await this.supabase
          .from('chat_sessions')
          .update(session)
          .eq('id', sessionId);
      } catch (error) {
        console.error('Session end error:', error);
      }
    }

    // Update in memory
    await this.store(`session-${sessionId}`, session, {
      sessionId,
      ttl: 86400 * 30 // 30 days for completed sessions
    });
  }

  // Get chat history
  async getChatHistory(
    sessionId: string,
    limit: number = 50
  ): Promise<ChatMessage[]> {
    if (!this.supabase) {
      return [];
    }

    try {
      const { data, error } = await this.supabase
        .from('chat_messages')
        .select('*')
        .eq('session_id', sessionId)
        .order('timestamp', { ascending: true })
        .limit(limit);

      if (error) {
        console.error('Failed to get chat history:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Chat history error:', error);
      return [];
    }
  }

  // Clean up expired memories
  async cleanup(): Promise<void> {
    const cutoffDate = new Date(Date.now() - this.config.memoryRetention * 24 * 60 * 60 * 1000);

    if (this.supabase) {
      try {
        // Clean up expired memory entries
        await this.supabase
          .from('ai_memory')
          .delete()
          .lt('expires_at', new Date().toISOString());

        // Clean up old chat messages
        await this.supabase
          .from('chat_messages')
          .delete()
          .lt('timestamp', cutoffDate.toISOString());

        // Clean up old sessions
        await this.supabase
          .from('chat_sessions')
          .delete()
          .lt('started_at', cutoffDate.toISOString());

        console.log('✅ Memory cleanup completed');
      } catch (error) {
        console.error('Cleanup error:', error);
      }
    }

    // Clean up local memory
    this.localMemory.clear();
  }

  // Get memory statistics
  async getStats(): Promise<{
    totalEntries: number;
    totalSizeBytes: number;
    chatSessions: number;
    chatMessages: number;
  }> {
    const stats = {
      totalEntries: 0,
      totalSizeBytes: 0,
      chatSessions: 0,
      chatMessages: 0
    };

    if (this.supabase) {
      try {
        // Memory entries
        const { count: memoryCount } = await this.supabase
          .from('ai_memory')
          .select('*', { count: 'exact', head: true });

        const { data: memorySizes } = await this.supabase
          .from('ai_memory')
          .select('size_bytes');

        stats.totalEntries = memoryCount || 0;
        stats.totalSizeBytes = memorySizes?.reduce((sum, entry) => sum + (entry.size_bytes || 0), 0) || 0;

        // Chat sessions
        const { count: sessionCount } = await this.supabase
          .from('chat_sessions')
          .select('*', { count: 'exact', head: true });

        stats.chatSessions = sessionCount || 0;

        // Chat messages
        const { count: messageCount } = await this.supabase
          .from('chat_messages')
          .select('*', { count: 'exact', head: true });

        stats.chatMessages = messageCount || 0;
      } catch (error) {
        console.error('Stats error:', error);
      }
    }

    return stats;
  }
}

// Global memory manager instance
let memoryManager: MemoryManager | null = null;

// Initialize memory manager
export function initializeMemory(config: Partial<MemoryConfig> = {}): MemoryManager {
  if (!memoryManager) {
    memoryManager = new MemoryManager(config);
  }
  return memoryManager;
}

// Get memory manager instance
export function getMemoryManager(): MemoryManager {
  if (!memoryManager) {
    memoryManager = new MemoryManager();
  }
  return memoryManager;
}

// Convenience functions
export async function logMemory(key: string, data: any, options?: {
  agentId?: string;
  sessionId?: string;
  ttl?: number;
}): Promise<void> {
  const manager = getMemoryManager();
  await manager.store(key, data, options);
}

export async function getMemory(key: string): Promise<any | null> {
  const manager = getMemoryManager();
  return await manager.retrieve(key);
}

export async function deleteMemory(key: string): Promise<void> {
  const manager = getMemoryManager();
  await manager.delete(key);
}

export async function logChatMessage(
  agentName: string,
  messageType: 'user' | 'agent' | 'system',
  content: string,
  options?: {
    sessionId?: string;
    userId?: string;
    platform?: string;
    context?: string;
  }
): Promise<string> {
  const manager = getMemoryManager();
  return await manager.logChatMessage(agentName, messageType, content, options);
}

export async function startChatSession(
  agentName: string,
  options?: {
    userId?: string;
    platform?: string;
    context?: Record<string, any>;
  }
): Promise<string> {
  const manager = getMemoryManager();
  return await manager.startChatSession(agentName, options);
}

export async function endChatSession(sessionId: string): Promise<void> {
  const manager = getMemoryManager();
  await manager.endChatSession(sessionId);
}

export async function getChatHistory(sessionId: string, limit?: number): Promise<ChatMessage[]> {
  const manager = getMemoryManager();
  return await manager.getChatHistory(sessionId, limit);
}

// Export types and classes
export type { MemoryConfig, MemoryEntry, ChatMessage, ChatSession };
export { MemoryManager };