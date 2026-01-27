/**
 * Common type definitions for Open Pentest Frontend
 * @module types
 */

/**
 * Represents the severity level of a security finding
 */
export enum SeverityLevel {
    CRITICAL = 'critical',
    HIGH = 'high',
    MEDIUM = 'medium',
    LOW = 'low',
    INFO = 'info',
}

/**
 * Represents the status of a security scan or task
 */
export enum TaskStatus {
    PENDING = 'pending',
    RUNNING = 'running',
    COMPLETED = 'completed',
    FAILED = 'failed',
    CANCELLED = 'cancelled',
}

/**
 * Represents the type of security target
 */
export enum TargetType {
    WEB_APPLICATION = 'web_application',
    NETWORK_HOST = 'network_host',
    API_ENDPOINT = 'api_endpoint',
    CLOUD_SERVICE = 'cloud_service',
    BINARY_FILE = 'binary_file',
}

/**
 * API response wrapper for consistent error handling
 */
export interface ApiResponse<T = unknown> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
    timestamp: string;
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
}

/**
 * Paginated API response
 */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
    meta: PaginationMeta;
}

/**
 * Represents a security finding or vulnerability
 */
export interface SecurityFinding {
    id: string;
    title: string;
    description: string;
    severity: SeverityLevel;
    targetType: TargetType;
    targetUrl?: string;
    discoveredAt: string;
    remediationSteps?: string[];
    references?: string[];
    tags: string[];
}

/**
 * Represents a security scan task
 */
export interface SecurityTask {
    id: string;
    name: string;
    description: string;
    targetType: TargetType;
    targetUrl: string;
    status: TaskStatus;
    progress: number;
    createdAt: string;
    startedAt?: string;
    completedAt?: string;
    findings: SecurityFinding[];
    errorMessage?: string;
}

/**
 * User authentication context
 */
export interface AuthContext {
    isAuthenticated: boolean;
    user?: {
        id: string;
        email: string;
        name: string;
        role: 'admin' | 'user' | 'viewer';
    };
    token?: string;
}

/**
 * Application configuration
 */
export interface AppConfig {
    apiBaseUrl: string;
    apiTimeout: number;
    environment: 'development' | 'staging' | 'production';
    version: string;
}

/**
 * Generic error response
 */
export interface ErrorResponse {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    timestamp: string;
}

// Re-export chat, session, and tool types
export * from './chat';
export * from './session';
export * from './tool';

// Explicitly export execution types to avoid conflicts
export type {
  ExecutionStatus,
  Task,
  Agent,
  ExecutionTree,
  TimelineAgent,
  ExecutionTimeline,
  AgentFilter,
  VisualizationView,
  ExportFormat,
  LevelStatistics,
} from './execution';

// Export ToolInvocation from execution as AgentToolInvocation to avoid conflict with tool.ts
export type { ToolInvocation as AgentToolInvocation } from './execution';

// Export validation rules and type guards
export { VALIDATION_RULES, isAgent, isToolInvocation, isExecutionTree } from './execution';
