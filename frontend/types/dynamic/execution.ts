/**
 * Core types for agent execution visualization system
 * Defines data structures for agents, tool invocations, and execution trees
 */

/**
 * Status of an agent or tool execution
 */
export type ExecutionStatus = 'running' | 'completed' | 'failed' | 'pending';

/**
 * Represents a user session containing multiple tasks
 */
export interface Session {
  /** Unique identifier for this session */
  id: string;

  /** Session title (usually derived from the first task) */
  title: string;

  /** Unix timestamp when session was created */
  created_at: number;

  /** List of tasks in this session */
  tasks: Task[];
}

/**
 * Represents a task from chat conversation
 * Tasks are the primary dimension for visualization
 */
export interface Task {
  /** Unique identifier for this task */
  id: string;

  /** Associated session ID */
  session_id?: string;

  /** Task title/name */
  title: string;

  /** Task description */
  description: string;

  /** Status of the task */
  status: ExecutionStatus;

  /** Unix timestamp when task started */
  start_time: number;

  /** Unix timestamp when task ended */
  end_time: number;

  /** Duration in milliseconds */
  duration_ms: number;

  /** Associated execution tree for this task */
  execution_id: string;

  /** Root agent executing this task */
  root_agent_id: string;

  /** Number of sub-agents spawned */
  agent_count: number;

  /** Number of tools used */
  tool_count: number;

  /** Success rate percentage */
  success_rate: number;

  /** Error message if failed */
  error_message?: string;

  /** Result summary from task execution */
  result_summary?: string;

  /** Parent task ID for subtasks (null for root tasks) */
  parent_id?: string | null;
}

/**
 * Represents a single tool invocation by an agent
 */
export interface ToolInvocation {
  /** Unique identifier for this tool invocation */
  id: string;

  /** Name of the tool (e.g., 'nmap_scan', 'decision_engine') */
  tool_name: string;

  /** Description of what the tool does */
  tool_description: string;

  /** Input parameters passed to the tool (JSON object) */
  parameters: Record<string, any>;

  /** Output/result from the tool execution (JSON object) */
  result: Record<string, any>;

  /** Current status of the tool execution */
  status: ExecutionStatus;

  /** Unix timestamp in milliseconds when tool started */
  start_time: number;

  /** Unix timestamp in milliseconds when tool ended */
  end_time: number;

  /** Computed duration in milliseconds (end_time - start_time) */
  duration_ms: number;

  /** Error message if tool failed (optional) */
  error_message?: string;

  /** Whether this tool is an agent_tool that spawns child agents */
  is_agent_tool?: boolean;

  /** ID of the child agent spawned by this agent_tool (if is_agent_tool is true) */
  child_agent_id?: string;

  /** Task ID that this tool belongs to (for debugging) */
  task_id?: string;

  /** Dynamically loaded subtasks for this agent_tool (only populated when expanded) */
  loaded_subtasks?: Agent[];
}

/**
 * Represents a single agent execution
 * Can have sub-agents (recursive structure)
 */
export interface Agent {
  /** Unique identifier for this agent */
  id: string;

  /** Agent name (max 200 characters) */
  name: string;

  /** Task description (max 1000 characters) */
  task_description: string;

  /** Current status of the agent */
  status: ExecutionStatus;

  /** Nesting level in the agent tree (0-3, where 0 is root) */
  level: number;

  /** Unix timestamp in milliseconds when agent started */
  start_time: number;

  /** Unix timestamp in milliseconds when agent ended */
  end_time: number;

  /** Computed duration in milliseconds (end_time - start_time) */
  duration_ms: number;

  /** ID of parent agent (if this is a sub-agent) */
  parent_agent_id?: string;

  /** Array of tools called by this agent */
  tool_invocations: ToolInvocation[];

  /** Array of sub-agents spawned by this agent */
  sub_agents: Agent[];

  /** Array of child agents spawned by agent_tool (for multi-level hierarchy) */
  child_agents?: Agent[];

  /** Context information for the agent (can be a string or structured object) */
  context?: string | {
    current_target?: string;
    objective?: string;
    constraints?: string[];
  };

  /** List of available tools for this agent */
  available_tools?: string[];

  /** Final output from the agent */
  output?: Record<string, any>;

  /** Error message if agent failed (optional) */
  error_message?: string;

  /** Success rate as percentage (0-100) */
  success_rate?: number;

  /** Associated task ID for this agent (if agent corresponds to a task) */
  task_id?: string;

  /** Whether this agent has subtasks that can be loaded */
  has_subtasks?: boolean;

  /** Loaded subtasks (lazy loaded when agent_tool is clicked) */
  loaded_subtasks?: Agent[];

  /** Task metadata (includes tools list and other task-level information) */
  metadata?: Record<string, any>;
}

/**
 * Root container for a complete execution
 * Contains the root agent and overall statistics
 */
export interface ExecutionTree {
  /** Unique identifier for this execution */
  id: string;

  /** The root agent of this execution */
  root_agent: Agent;

  /** Total execution time in milliseconds */
  total_duration_ms: number;

  /** Total number of agents spawned */
  total_agents_count: number;

  /** Total number of tools called */
  total_tools_count: number;

  /** Overall success rate as percentage (0-100) */
  success_rate: number;

  /** Unix timestamp in milliseconds when execution started */
  execution_start_time: number;

  /** Unix timestamp in milliseconds when execution ended */
  execution_end_time: number;

  /** Unix timestamp in milliseconds when this execution was created */
  created_at: number;

  /** Maximum nesting depth in the execution tree (highest level number) */
  max_depth?: number;

  /** Result summary from task execution */
  result_summary?: string;
}

/**
 * Represents an agent positioned on a timeline
 * Used for timeline view rendering
 */
export interface TimelineAgent {
  /** The agent data */
  agent: Agent;

  /** Row number for concurrent agent grouping */
  row: number;

  /** Offset in milliseconds from timeline start */
  offset_ms: number;

  /** Width in milliseconds (duration of execution) */
  width_ms: number;
}

/**
 * Derived timeline view showing agents sorted by time
 */
export interface ExecutionTimeline {
  /** Agents positioned on timeline */
  agents: TimelineAgent[];

  /** Earliest start time in milliseconds */
  min_time: number;

  /** Latest end time in milliseconds */
  max_time: number;

  /** Total timeline duration in milliseconds */
  total_duration_ms: number;
}

/**
 * Statistics for a specific execution level
 */
export interface LevelStatistics {
  /** Level number (1, 2, 3, ...) */
  level: number;

  /** Number of agents at this level */
  agent_count: number;

  /** Number of tools invoked at this level */
  tool_count: number;

  /** Average duration in milliseconds for agents at this level */
  avg_duration_ms: number;

  /** Success rate as percentage (0-100) for this level */
  success_rate: number;

  /** Total duration in milliseconds for all agents at this level */
  total_duration_ms: number;
}

/**
 * Filter criteria for agent visualization
 */
export interface AgentFilter {
  /** Filter by agent status */
  status?: ExecutionStatus[];

  /** Search query for agent name or task description */
  searchQuery?: string;

  /** Minimum duration in milliseconds */
  minDuration?: number;

  /** Maximum duration in milliseconds */
  maxDuration?: number;
}

/**
 * Visualization state
 */
export type VisualizationView = 'tree' | 'timeline';

/**
 * Export format options
 */
export type ExportFormat = 'json' | 'markdown' | 'pdf';

/**
 * Validation rules for entities
 */
export const VALIDATION_RULES = {
  /** Maximum agent nesting level */
  MAX_AGENT_LEVEL: 3,

  /** Maximum concurrent agents per parent */
  MAX_CONCURRENT_AGENTS: 10,

  /** Maximum tool data size in bytes */
  MAX_TOOL_DATA_SIZE: 10 * 1024, // 10KB

  /** Maximum agent name length */
  MAX_AGENT_NAME_LENGTH: 200,

  /** Maximum task description length */
  MAX_TASK_DESCRIPTION_LENGTH: 1000,
} as const;

/**
 * Type guards for runtime validation
 */
export const isAgent = (obj: any): obj is Agent => {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.task_description === 'string' &&
    ['running', 'completed', 'failed', 'pending'].includes(obj.status) &&
    typeof obj.level === 'number' &&
    Array.isArray(obj.tool_invocations) &&
    Array.isArray(obj.sub_agents)
  );
};

export const isToolInvocation = (obj: any): obj is ToolInvocation => {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.tool_name === 'string' &&
    typeof obj.tool_description === 'string' &&
    typeof obj.parameters === 'object' &&
    typeof obj.result === 'object' &&
    ['running', 'completed', 'failed'].includes(obj.status)
  );
};

export const isExecutionTree = (obj: any): obj is ExecutionTree => {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    isAgent(obj.root_agent) &&
    typeof obj.total_duration_ms === 'number' &&
    typeof obj.total_agents_count === 'number' &&
    typeof obj.total_tools_count === 'number' &&
    typeof obj.success_rate === 'number'
  );
};
