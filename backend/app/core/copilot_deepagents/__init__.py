"""
DeepAgents Copilot - 用 DeepAgents 模式生成任意类型的 Agent 工作流图。

架构：
- Manager Agent：编排子代理 + 调用 create_node/connect_nodes
- SubAgents：requirements-analyst, workflow-architect, validator

特点：
- 子代理协作：分析→设计→验证→生成
- 产物落盘：analysis.json, blueprint.json, validation.json
- 标准输出：GraphAction（与现有 Copilot 完全兼容）

使用方式：
    from app.core.copilot_deepagents import stream_deepagents_actions
    
    async for event in stream_deepagents_actions(
        prompt="创建一个 APK 安全分析团队",
        graph_context={"nodes": [], "edges": []},
        graph_id="my_graph",
    ):
        print(event)
"""

from .schemas import (
    RequirementSpec,
    WorkflowBlueprint,
    ValidationReport,
    BlueprintNode,
    BlueprintEdge,
    NodeConfig,
    NodePosition,
)
from .artifacts import ArtifactStore, new_run_store
from .subagents import (
    SUBAGENT_REQUIREMENTS_ANALYST,
    SUBAGENT_WORKFLOW_ARCHITECT,
    SUBAGENT_VALIDATOR,
    ALL_SUBAGENTS,
    ANALYSIS_FILE,
    BLUEPRINT_FILE,
    VALIDATION_FILE,
)
from .manager import (
    create_copilot_manager,
    run_copilot_manager,
    stream_copilot_manager,
    DEEPAGENTS_AVAILABLE,
)
from .streaming import stream_deepagents_actions

__all__ = [
    # Schemas
    "RequirementSpec",
    "WorkflowBlueprint",
    "ValidationReport",
    "BlueprintNode",
    "BlueprintEdge",
    "NodeConfig",
    "NodePosition",
    # Artifacts
    "ArtifactStore",
    "new_run_store",
    # SubAgent Constants
    "SUBAGENT_REQUIREMENTS_ANALYST",
    "SUBAGENT_WORKFLOW_ARCHITECT",
    "SUBAGENT_VALIDATOR",
    "ALL_SUBAGENTS",
    "ANALYSIS_FILE",
    "BLUEPRINT_FILE",
    "VALIDATION_FILE",
    # Manager
    "create_copilot_manager",
    "run_copilot_manager",
    "stream_copilot_manager",
    "DEEPAGENTS_AVAILABLE",
    # Streaming (main entry point)
    "stream_deepagents_actions",
]
