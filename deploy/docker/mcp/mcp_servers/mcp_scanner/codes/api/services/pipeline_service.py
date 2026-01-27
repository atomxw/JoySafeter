"""
Pipeline 步骤服务模块。

提供独立的 pipeline 步骤服务，每个步骤都可以单独调用。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 添加 codes 目录到路径，以便导入 scanner 和 pipeline 模块
# Path(__file__) = codes/api/services/pipeline_service.py
# parent.parent.parent = codes
codes_dir = Path(__file__).parent.parent.parent
if str(codes_dir) not in sys.path:
    sys.path.insert(0, str(codes_dir))

import asyncio
from typing import Any

from scanner.initial_scan import LocalPMScanner, OpenAILLMScanner
from scanner.initial_scan.dedup import deduplicate_by_fields
from scanner import resolve_scan_context
from scanner.data_types import ScanContext, SecurityFinding


class PipelineService:
    """Pipeline 步骤服务，封装各个步骤的业务逻辑。"""

    def __init__(self) -> None:
        """初始化服务，创建扫描器实例。"""
        self._pm_scanner = LocalPMScanner()
        self._llm_scanner = OpenAILLMScanner(prompt_path="", model_name="")

    async def resolve_context(
        self,
        path: str,
        *,
        explicit_languages: list[str] | None = None,
        auto_detect_languages: bool = True,
        language_detection_limit: int = 5000,
        scan_methods: dict[str, Any] | list[str] | None = None,
        metadata: dict[str, str] | None = None,
        extension_language_map: dict[str, list[str]] | None = None,
    ) -> ScanContext:
        """
        解析目标路径，生成 ScanContext。

        Args:
            path: 目标路径（字符串）
            explicit_languages: 显式指定的语言列表
            auto_detect_languages: 是否自动检测语言
            language_detection_limit: 语言检测的最大文件数
            scan_methods: 扫描方法配置
            metadata: 用户元数据
            extension_language_map: 扩展名到语言的映射

        Returns:
            ScanContext 对象
        """
        # 在异步上下文中执行同步的解析操作
        loop = asyncio.get_event_loop()
        
        # 使用 functools.partial 来传递关键字参数
        from functools import partial
        resolve_func = partial(
            resolve_scan_context,
            path,
            explicit_languages=explicit_languages,
            auto_detect_languages=auto_detect_languages,
            language_detection_limit=language_detection_limit,
            scan_methods=scan_methods,
            metadata=metadata,
            extension_language_map=extension_language_map,
        )
        context = await loop.run_in_executor(None, resolve_func)
        return context

    async def pm_scan(self, context: ScanContext) -> list[SecurityFinding]:
        """
        执行 PM Scanner 扫描。

        Args:
            context: 扫描上下文

        Returns:
            SecurityFinding 列表
        """
        # 在异步上下文中执行同步的扫描操作
        loop = asyncio.get_event_loop()
        findings_iter = await loop.run_in_executor(None, self._pm_scanner.scan, context)
        # 将 Iterable 转换为 list
        return list(findings_iter)

    async def llm_scan(self, context: ScanContext) -> list[SecurityFinding]:
        """
        执行 LLM Scanner 扫描。

        Args:
            context: 扫描上下文

        Returns:
            SecurityFinding 列表
        """
        # 在异步上下文中执行同步的扫描操作
        loop = asyncio.get_event_loop()
        findings_iter = await loop.run_in_executor(None, self._llm_scanner.scan, context)
        # 将 Iterable 转换为 list
        return list(findings_iter)

    async def deduplicate(
        self, findings: list[SecurityFinding]
    ) -> list[SecurityFinding]:
        """
        对发现结果进行去重。

        Args:
            findings: SecurityFinding 列表

        Returns:
            去重后的 SecurityFinding 列表
        """
        # 在异步上下文中执行同步的去重操作
        loop = asyncio.get_event_loop()
        deduplicated = await loop.run_in_executor(
            None, deduplicate_by_fields, findings, "file_path", "start_line", "end_line"
        )
        return deduplicated


# 创建默认的服务实例
_default_pipeline_service = PipelineService()


async def resolve_context(path: str, **kwargs: Any) -> ScanContext:
    """解析目标路径（便捷函数）。"""
    return await _default_pipeline_service.resolve_context(path, **kwargs)


async def pm_scan(context: ScanContext) -> list[SecurityFinding]:
    """执行 PM Scanner 扫描（便捷函数）。"""
    return await _default_pipeline_service.pm_scan(context)


async def llm_scan(context: ScanContext) -> list[SecurityFinding]:
    """执行 LLM Scanner 扫描（便捷函数）。"""
    return await _default_pipeline_service.llm_scan(context)


async def deduplicate_findings(
    findings: list[SecurityFinding],
) -> list[SecurityFinding]:
    """对发现结果进行去重（便捷函数）。"""
    return await _default_pipeline_service.deduplicate(findings)

