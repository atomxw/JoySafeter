/**
 * Chat-related TypeScript type definitions
 * Defines interfaces for messages, chat state, and streaming responses
 */

import type { ToolInvocation } from './tool';

/**
 * Represents a single message in a conversation
 */
export interface Message {
  /** Unique message identifier */
  id: string;
  /** Session ID this message belongs to */
  sessionId: string;
  /** Task ID associated with this user input (for user messages only) */
  taskId?: string;
  /** Message role: 'user', 'assistant', or 'system' */
  role: 'user' | 'assistant' | 'system';
  /** Message content text */
  content: string;
  /** Timestamp when message was created */
  timestamp: number;
  /** Tool invocations associated with this message */
  toolInvocations?: ToolInvocation[];
  /** Whether message is still streaming */
  isStreaming?: boolean;
  /** Error message if message failed to send */
  error?: string;
}

/**
 * Chat state managed by Zustand store
 */
export interface ChatState {
  /** Current session ID */
  currentSessionId: string | null;
  /** Messages in current session */
  messages: Message[];
  /** Whether currently loading/streaming */
  isLoading: boolean;
  /** Current error message if any */
  error: string | null;
  /** Whether input is disabled (during streaming) */
  isInputDisabled: boolean;
}

/**
 * Chat store actions
 */
export interface ChatActions {
  /** Add a new message to the chat */
  addMessage: (message: Message) => void;
  /** Update an existing message */
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  /** Remove a message from the chat */
  removeMessage: (messageId: string) => void;
  /** Clear all messages in current session */
  clearMessages: () => void;
  /** Set loading state */
  setLoading: (isLoading: boolean) => void;
  /** Set error message */
  setError: (error: string | null) => void;
  /** Set input disabled state */
  setInputDisabled: (disabled: boolean) => void;
  /** Set current session ID */
  setCurrentSessionId: (sessionId: string | null) => void;
  /** Reset chat state */
  reset: () => void;
}

/**
 * Complete chat store type
 */
export type ChatStore = ChatState & ChatActions;
