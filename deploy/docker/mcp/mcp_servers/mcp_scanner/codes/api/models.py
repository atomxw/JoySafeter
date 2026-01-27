"""
API 请求和响应模型。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

# 添加 codes 目录到路径，以便导入 scanner 模块
# Path(__file__) = codes/api/models.py
# parent.parent = codes
codes_dir = Path(__file__).parent.parent
if str(codes_dir) not in sys.path:
    sys.path.insert(0, str(codes_dir))

from scanner.data_types import ScanContext, SecurityFinding


@dataclass
class UploadResponse:
    """文件上传接口响应。"""

    task_id: str
    storage_path: str
    message: str = "文件上传成功"
    output: str | None = None  # 扫描结果输出（JSON格式或simple格式）


@dataclass
class GitScanRequest:
    """Git 扫描请求模型。"""

    url: str
    ref: str | None = None
    token: str | None = None


@dataclass
class GitScanResponse:
    """Git 扫描接口响应。"""

    task_id: str
    storage_path: str
    message: str = "Git 仓库克隆成功"
    report: dict[str, Any] | None = None  # 扫描报告结果（可选）


@dataclass
class ScanResponse:
    """扫描结果响应。"""

    task_id: str
    status: str
    message: str
    report: dict[str, Any] | None = None  # 扫描报告结果


@dataclass
class ResolveContextRequest:
    """解析上下文请求。"""

    path: str
    explicit_languages: list[str] | None = None
    auto_detect_languages: bool = True
    language_detection_limit: int = 5000
    scan_methods: dict[str, Any] | list[str] | None = None
    metadata: dict[str, str] | None = None
    extension_language_map: dict[str, list[str]] | None = None


@dataclass
class ResolveContextResponse:
    """解析上下文响应。"""

    context: dict[str, Any]  # 序列化后的 ScanContext


@dataclass
class ScanRequest:
    """Pipeline 扫描请求。"""

    context: dict[str, Any]  # 序列化后的 ScanContext


@dataclass
class PipelineScanResponse:
    """Pipeline 扫描响应。"""

    findings: list[dict[str, Any]]  # 序列化后的 SecurityFinding 列表


@dataclass
class DeduplicateRequest:
    """去重请求。"""

    findings: list[dict[str, Any]]  # 序列化后的 SecurityFinding 列表


@dataclass
class DeduplicateResponse:
    """去重响应。"""

    findings: list[dict[str, Any]]  # 去重后的 SecurityFinding 列表


def serialize_report(findings: list[SecurityFinding]) -> dict[str, Any]:
    """
    将 SecurityFinding 列表序列化为字典。

    Args:
        findings: 扫描结果列表

    Returns:
        序列化后的字典
    """
    return {
        "findings": [serialize_security_finding(finding) for finding in findings],
        "count": len(findings),
    }


def serialize_scan_context(context: ScanContext) -> dict[str, Any]:
    """
    将 ScanContext 对象序列化为字典。

    Args:
        context: ScanContext 对象

    Returns:
        序列化后的字典
    """
    return {
        "root_path": str(context.root_path),
        "languages": list(context.languages),
        "scan_methods": (
            list(context.scan_methods)
            if isinstance(context.scan_methods, (list, tuple))
            else dict(context.scan_methods) if context.scan_methods else None
        ),
        "metadata": dict(context.metadata),
        "output_path": str(context.output_path) if context.output_path else None,
    }


def deserialize_scan_context(data: dict[str, Any]) -> ScanContext:
    """
    从字典反序列化为 ScanContext 对象。

    Args:
        data: 包含 ScanContext 数据的字典

    Returns:
        ScanContext 对象
    """
    return ScanContext(
        root_path=Path(data["root_path"]),
        languages=tuple(data.get("languages", [])),
        scan_methods=data.get("scan_methods"),
        metadata=data.get("metadata", {}),
        output_path=Path(data["output_path"]) if data.get("output_path") else None,
    )


def serialize_security_finding(finding: SecurityFinding) -> dict[str, Any]:
    """
    将 SecurityFinding 对象序列化为字典。

    Args:
        finding: SecurityFinding 对象

    Returns:
        序列化后的字典
    """
    return asdict(finding)


def deserialize_security_finding(data: dict[str, Any]) -> SecurityFinding:
    """
    从字典反序列化为 SecurityFinding 对象。

    Args:
        data: 包含 SecurityFinding 数据的字典

    Returns:
        SecurityFinding 对象
    """
    return SecurityFinding(
        finding_id=data["finding_id"],
        source=data["source"],
        severity=data["severity"],
        confidence=data["confidence"],
        title=data["title"],
        description=data["description"],
        file_path=data["file_path"],
        start_line=data["start_line"],
        end_line=data["end_line"],
        remediation=data.get("remediation"),
        evidence=data["evidence"],
        tags=data["tags"],
        rule_id=data["rule_id"],
        metadata=data["metadata"],
    )


@dataclass
class PIScanRequest:
    """Prompt Injection 扫描请求。"""

    schema: str  # JSON Schema 字符串


@dataclass
class PIScanResponse:
    """Prompt Injection 扫描响应（文本格式）。"""

    result: str  # 格式化的检测结果字符串


@dataclass
class PIScanJsonResponse:
    """Prompt Injection 扫描响应（JSON 格式）。"""

    error: str | None  # 错误信息（如果有）
    results: list[dict[str, Any]]  # 检测结果列表
    summary: dict[str, int]  # 统计信息：total, safe, unsafe, error
    message: str | None = None  # 提示信息（如果有）

