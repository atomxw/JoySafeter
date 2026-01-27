"""
EverWhistler-MCPScan 核心包。

暴露关键数据结构与工厂方法，供 CLI 与上层服务调用。
"""

from .input_resolver import resolve_scan_context
from .data_types import ScanContext, SecurityFinding

__all__ = [
    "ScanContext",
    "SecurityFinding",
    "resolve_scan_context",
]

