"""
核心领域模型定义。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

@dataclass(slots=True)
class ScanContext:
    """扫描上下文，包括原始输入与环境元数据。"""

    root_path: Path
    languages: Sequence[str]
    scan_methods: Mapping[str, object] | Sequence[str] | None = None
    metadata: MutableMapping[str, str] = field(default_factory=dict)
    output_path: Path | None = None


@dataclass(slots=True)
class SecurityFinding:
    """安全告警结构。"""
    finding_id: str
    source: str
    severity: str
    confidence: float
    title: str
    description: str
    file_path: str
    start_line: int
    end_line: int
    remediation: str | None
    evidence: dict
    tags: list[str]
    rule_id: str
    metadata: dict


@dataclass(slots=True)
class FileReviewPromptItem:
    """文件审阅提示词配置。"""
    name: str
    user_prompt: str


@dataclass(slots=True)
class _ReviewJob:
    """内部使用的审阅任务。"""
    job_id: str
    prompts: dict
    absolute_path: str
    output: str


@dataclass(slots=True)
class ScanStrategyConfig:
    """扫描策略配置"""
    enable_pm: bool = True
    enable_llm: bool = True
    enable_deep_scan: bool = False
    pm_timeout: int | None = None
    llm_max_workers: int | None = None


@dataclass(slots=True)
class DeduplicationStrategyConfig:
    """去重策略配置"""
    fields: Sequence[str] | None = field(
        default_factory=lambda: ["file_path", "start_line", "end_line"]
    )  # 用于去重的字段列表，如果为 None 或空列表则跳过去重


@dataclass(slots=True)
class OutputStrategyConfig:
    """输出策略配置"""
    formats: list[str] = field(default_factory=lambda: ["simple"])  # ["simple", "json", "markdown"]
    output_dir: Path | None = None


@dataclass(slots=True)
class FilterStrategyConfig:
    """过滤策略配置"""
    min_severity: str | None = None  # "low", "medium", "high", "critical"
    min_confidence: float | None = None  # 0.0 - 1.0
    require_valid_lines: bool = True  # 是否要求有效的行号
    use_hard_exclusions: bool = True  # 是否使用硬规则排除
    custom_rules: dict[str, Any] = field(default_factory=dict)
