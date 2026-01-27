"""
Agent 协同细筛逻辑。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence

from ..data_types import SecurityFinding
from .cpg_builder import CPGSnapshot


@dataclass(slots=True)
class AgentTask:
    """Agent 任务描述。"""

    kind: str
    seed_findings: Sequence[SecurityFinding]
    snapshot: CPGSnapshot


@dataclass(slots=True)
class AgentFinding(SecurityFinding):
    """细筛阶段的高置信发现。"""

    validated: bool = False
    reviewers: Sequence[str] = ()


class AgentOrchestrator(Protocol):
    """负责将初筛结果与 CPG 结合，生成 Agent 工作流程。"""

    def run(self, tasks: Sequence[AgentTask]) -> Iterable[AgentFinding]:
        """执行 Agent 工作流。"""

    def register_agent(self, name: str, *, capabilities: Sequence[str]) -> None:
        """动态注册 Agent，实现扩展。"""

