/**
 * Tool invocation-related TypeScript type definitions
 * Defines interfaces for tool calls, execution, and results
 */

/**
 * Represents a tool that can be invoked by the AI
 */
export interface Tool {
  /** Unique tool identifier */
  id: string;
  /** Tool name */
  name: string;
  /** Tool description */
  description: string;
  /** Tool category */
  category: string;
  /** Input schema for tool parameters */
  inputSchema?: Record<string, unknown>;
  /** Whether tool is available */
  isAvailable: boolean;
}

/**
 * Represents a tool invocation (call) made by the AI
 */
export interface ToolInvocation {
  /** Unique invocation identifier */
  id: string;
  /** Tool ID being invoked */
  toolId: string;
  /** Tool name */
  toolName: string;
  /** Tool description */
  description?: string;
  /** Parameters passed to the tool */
  parameters: Record<string, unknown>;
  /** Execution status */
  status: 'pending' | 'executing' | 'completed' | 'failed';
  /** Tool execution result */
  result?: unknown;
  /** Time taken to execute (in milliseconds) */
  executionTime?: number;
  /** Error message if execution failed */
  error?: string;
  /** Timestamp when invocation started */
  startedAt: number;
  /** Timestamp when invocation completed */
  completedAt?: number;
}

/**
 * Represents a streaming event from the server
 */
export interface StreamingEvent {
  /** Event type */
  type: StreamingEventType;
  /** Event data */
  data: unknown;
  /** Timestamp when event was received */
  timestamp: number;
  /** Optional message ID for tracking */
  messageId?: string;
}

/**
 * Types of streaming events
 */
export type StreamingEventType =
  | 'thinking'          // AI is thinking
  | 'tool_call'         // Tool is being called
  | 'tool_executing'    // Tool is executing
  | 'tool_result'       // Tool result received
  | 'intermediate'      // Intermediate result (tool start/end)
  | 'message_chunk'     // Message chunk received
  | 'message_complete'  // Message complete
  | 'task_created'      // Task created with task_id
  | 'error'             // Error occurred
  | 'complete';         // Stream complete

/**
 * Tool invocation request
 */
export interface ToolInvocationRequest {
  /** Tool name */
  toolName: string;
  /** Tool parameters */
  parameters: Record<string, unknown>;
  /** Optional timeout in milliseconds */
  timeout?: number;
}

/**
 * Tool invocation response
 */
export interface ToolInvocationResponse {
  /** Invocation ID */
  id: string;
  /** Tool name */
  toolName: string;
  /** Execution status */
  status: 'success' | 'failed' | 'timeout';
  /** Tool result */
  result?: unknown;
  /** Error message if failed */
  error?: string;
  /** Execution time in milliseconds */
  executionTime: number;
}

/**
 * Tool execution chain - multiple tools called sequentially
 */
export interface ToolExecutionChain {
  /** Chain ID */
  id: string;
  /** List of tool invocations in order */
  invocations: ToolInvocation[];
  /** Overall chain status */
  status: 'pending' | 'executing' | 'completed' | 'failed';
  /** Chain error message if failed */
  error?: string;
  /** Total execution time */
  totalExecutionTime: number;
}

/**
 * Tool metadata for display
 */
export interface ToolMetadata {
  /** Tool name */
  name: string;
  /** Tool description */
  description: string;
  /** Tool category */
  category: string;
  /** Tool icon/emoji */
  icon?: string;
  /** Tool color for UI */
  color?: string;
}

/**
 * Tool result display format
 */
export interface ToolResultDisplay {
  /** Result format: 'text', 'json', 'table', 'code', 'html' */
  format: 'text' | 'json' | 'table' | 'code' | 'html';
  /** Formatted result content */
  content: string;
  /** Raw result data */
  rawData?: unknown;
  /** Whether result is collapsible */
  isCollapsible?: boolean;
}
