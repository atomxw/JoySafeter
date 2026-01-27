"""
CPG 构建与管理。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from ..data_types import ScanContext


@dataclass(slots=True)
class CPGSnapshot:
    """封装 CPG 元数据与文件引用。"""

    backend: str
    version: str
    graph_path: Path
    metadata_path: Path | None = None


class CPGBackend(Protocol):
    """CPG 构建器接口。"""

    name: str

    def generate(self, context: ScanContext, targets: Sequence[Path]) -> CPGSnapshot:
        """生成/刷新指定文件的 CPG。"""

    def warmup(self) -> None:
        """初始化底层引擎。"""

