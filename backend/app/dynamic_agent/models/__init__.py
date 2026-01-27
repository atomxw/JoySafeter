"""
Agent Models Package

Data models for CTF Agent Enhancement:
- ExecutionPlan: Progress tracking and visualization
- RetryStrategy: Intelligent retry mechanism
- ExtractedState: Structured state extraction from results
- HintTracker: Hint execution status tracking

Single Subagent Clean Architecture (006):
- SubagentSummary: Structured summary returned by subagents
- TodoItem, TodoPanel: Rich TODO panel for progress visualization
- TraceLogEntry, TraceLogger: JSONL debug logging

Intent-First Clean Context Architecture (007):
- SessionContext: Dynamic context for Intent Persistence
"""

from app.dynamic_agent.models.execution_plan import ExecutionPlan, PlanStep
from app.dynamic_agent.models.retry_strategy import (
    RetryStrategy, 
    RETRY_STRATEGIES, 
    classify_error,
    generate_adjustments,
    RetryAdjustment,
)
from app.dynamic_agent.models.extracted_state import ExtractedState, extract_key_state
from app.dynamic_agent.models.hint_tracker import HintTracker, HintExecutionState
from app.dynamic_agent.models.display_models import (
    ToolStatus,
    StepStatus,
    ToolCallDisplay,
    ThinkingDisplay,
    ExecutionStep,
    DisplayState,
)

# 006: Single Subagent Clean Architecture models
from app.dynamic_agent.models.subagent_summary import (
    SubagentSummary,
    create_summary_from_result,
    KEY_INFO_CATEGORIES,
)
from app.dynamic_agent.models.todo_panel import (
    TodoItem,
    TodoPanel,
    TodoStatus,
    STATUS_ICONS,
    STATUS_COLORS,
)
from app.dynamic_agent.models.trace_logger import (
    TraceLogEntry,
    TraceLogger,
    get_trace_logger,
    close_trace_logger,
)

# 007: Intent-First Clean Context Architecture models
from app.dynamic_agent.models.session_context import SessionContext

# 005: Whitebox Scan models
from app.dynamic_agent.models.scan import (
    ScanJobResponse,
    ScanJobStatus,
    ScanReport,
    Finding,
    ScanStatus,
    AgentVerificationStatus,
)

# Note: ExecutionPlan is already defined in execution_plan.py,
# display_models.py has a simplified version for display purposes only

__all__ = [
    # Execution Plan
    "ExecutionPlan",
    "PlanStep",
    # Retry Strategy
    "RetryStrategy",
    "RETRY_STRATEGIES",
    "classify_error",
    "generate_adjustments",
    "RetryAdjustment",
    # Extracted State
    "ExtractedState",
    "extract_key_state",
    # Hint Tracker
    "HintTracker",
    "HintExecutionState",
    # Display Models
    "ToolStatus",
    "StepStatus",
    "ToolCallDisplay",
    "ThinkingDisplay",
    "ExecutionStep",
    "DisplayState",
    # 006: Subagent Summary
    "SubagentSummary",
    "create_summary_from_result",
    "KEY_INFO_CATEGORIES",
    # 006: TODO Panel
    "TodoItem",
    "TodoPanel",
    "TodoStatus",
    "STATUS_ICONS",
    "STATUS_COLORS",
    # 006: Trace Logger
    "TraceLogEntry",
    "TraceLogger",
    "get_trace_logger",
    "close_trace_logger",
    # 007: Session Context
    "SessionContext",
    # 005: Whitebox Scan
    "ScanJobResponse",
    "ScanJobStatus",
    "ScanReport",
    "Finding",
    "ScanStatus",
    "AgentVerificationStatus",
]
