"""
扫描服务模块。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 添加 codes 目录到路径，以便导入 scanner 和 pipeline 模块
# Path(__file__) = codes/api/services/scan_service.py
# parent.parent = codes
codes_dir = Path(__file__).parent.parent.parent
if str(codes_dir) not in sys.path:
    sys.path.insert(0, str(codes_dir))

import asyncio

from scanner.initial_scan import LocalPMScanner, OpenAILLMScanner
from scanner import resolve_scan_context
from scanner.data_types import SecurityFinding
from pipeline import DefaultOrchestrator, PipelineConfig


class ScanService:
    """扫描服务，封装 orchestrator 初始化和执行逻辑。"""

    def __init__(self, jobs: int = 4) -> None:
        """
        初始化扫描服务。

        Args:
            jobs: 并行任务数，默认为 4
        """
        self._orchestrator = DefaultOrchestrator(
            resolver=resolve_scan_context,
            pm_scanner=LocalPMScanner(),
            llm_scanner=OpenAILLMScanner(prompt_path="", model_name=""),  # 空字符串会使用默认值
            config=PipelineConfig(jobs=jobs),
        )

    async def run_scan(self, storage_path: Path | str) -> list[SecurityFinding]:
        """
            执行扫描流程。

            Args:
                storage_path: 代码存储路径（Path 对象或字符串）

            Returns:
                扫描结果列表

            Raises:
                Exception: 扫描过程中发生的错误
        """
        # 将 Path 对象转换为字符串
        target_path = str(storage_path) if isinstance(storage_path, Path) else storage_path

        # 在异步上下文中执行同步的扫描操作
        # 使用 asyncio.to_thread 在线程池中执行，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        findings = await loop.run_in_executor(None, self._orchestrator.run, target_path)
        return findings


# 创建默认的扫描服务实例
_default_scan_service = ScanService()


async def run_scan(storage_path: Path | str) -> list[SecurityFinding]:
    """
    执行扫描流程（便捷函数）。

    Args:
        storage_path: 代码存储路径

    Returns:
        扫描结果列表
    """
    return await _default_scan_service.run_scan(storage_path)


