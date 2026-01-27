"""
扫描任务编排器。
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging         
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence, cast
from concurrent.futures import ThreadPoolExecutor

from scanner.initial_scan import (  # noqa: E402
    LocalPMScanner,
    OpenAILLMScanner,
)
from scanner.data_types import (  # noqa: E402
    ScanContext,
    SecurityFinding,
    ScanStrategyConfig,
    DeduplicationStrategyConfig,
    OutputStrategyConfig,
    FilterStrategyConfig,
)
from scanner import resolve_scan_context  # noqa: E402
from scanner.output_resolver import (  # noqa: E402
    simple_output,
)
from scanner.initial_scan.dedup import (  # noqa: E402
    deduplicate_by_fields,
)
from scanner.initial_scan.finding_filter import (  # noqa: E402
    apply_filter_strategy,
)


logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """流水线配置。"""
    jobs: int = 8
    
    # 策略配置：直接使用配置对象，默认值提供常用配置
    scan_strategy: ScanStrategyConfig = field(
        default_factory=lambda: ScanStrategyConfig(enable_pm=True, enable_llm=True)
    )
    dedup_strategy: DeduplicationStrategyConfig = field(
        default_factory=lambda: DeduplicationStrategyConfig(fields=["file_path", "start_line", "end_line"])
    )
    output_strategy: OutputStrategyConfig = field(
        default_factory=lambda: OutputStrategyConfig(formats=["simple"])
    )
    filter_strategy: FilterStrategyConfig = field(
        default_factory=lambda: FilterStrategyConfig(min_severity="medium", min_confidence=0.85, require_valid_lines=True, use_hard_exclusions=True)
    )


class DefaultOrchestrator:
    """参考实现骨架。"""

    def __init__(
        self,
        *,
        resolver,
        pm_scanner: LocalPMScanner,
        llm_scanner: OpenAILLMScanner,
        # cpg_backend: CPGBackend,
        # agent_orchestrator: AgentOrchestrator,
        config: PipelineConfig,
    ) -> None:
        self._resolver = resolver
        self._pm_scanner = pm_scanner
        self._llm_scanner = llm_scanner
        # self._cpg_backend = cpg_backend
        # self._agent_orchestrator = agent_orchestrator
        self._config = config

    def run(self, target: str) -> list[SecurityFinding]:
        """执行端到端扫描。"""
        context = self._resolver(target)
        findings = list(self._initial_screening(context))
        findings = self._apply_deduplication(findings)
        
        if self._config.filter_strategy is not None:
            findings = apply_filter_strategy(findings, self._config.filter_strategy)
        
        if self._config.scan_strategy.enable_deep_scan:
            deep_findings = list(self._deep_screening(context, findings))
            findings.extend(deep_findings)
        
        return findings

    # 以下辅助方法定义主要扩展点
    def _initial_screening(self, context: ScanContext) -> Iterable[SecurityFinding]:
        """执行初筛，根据配置决定执行哪些扫描。"""
        findings: list[SecurityFinding] = []
        scan_config = self._config.scan_strategy
        
        # 根据策略配置决定执行哪些扫描
        futures = []
        with ThreadPoolExecutor(max_workers=self._config.jobs) as executor:
            if scan_config.enable_pm:
                pm_future = executor.submit(self._pm_scanner.scan, context)
                futures.append(("pm", pm_future))
            
            if scan_config.enable_llm:
                llm_future = executor.submit(self._llm_scanner.scan, context)
                futures.append(("llm", llm_future))
            
            # 等待所有任务完成
            for name, future in futures:
                try:
                    result = future.result()
                    findings.extend(result)
                except Exception as e:
                    logger.warning(f"{name} 扫描失败: {e}", exc_info=True)
            
        return cast(Iterable[SecurityFinding], findings)
    
    def _apply_deduplication(
        self, findings: list[SecurityFinding]
    ) -> list[SecurityFinding]:
        """根据去重策略配置应用去重。"""
        dedup_config = self._config.dedup_strategy
        
        # 如果字段列表为空或 None，跳过去重
        if not dedup_config.fields:
            return findings
        
        # 直接使用字段列表进行去重
        return deduplicate_by_fields(findings, *dedup_config.fields)
    
    def _deep_screening(
        self,
        context: ScanContext,
        initial_findings: Sequence[SecurityFinding],
    ) -> Iterable[SecurityFinding]:
        raise NotImplementedError

    def _build_report(
        self,
        context: ScanContext,
        findings: Sequence[SecurityFinding],
    ) -> tuple[ScanContext, list[SecurityFinding]]:
        raise NotImplementedError

if __name__ == "__main__":
    # 注意：CPGBackend、AgentOrchestrator 是 Protocol，不能直接实例化
    # 这里仅作为示例，实际使用时需要提供具体实现
    orchestrator = DefaultOrchestrator(
        resolver=resolve_scan_context,
        pm_scanner=LocalPMScanner(),
        llm_scanner=OpenAILLMScanner(prompt_path="", model_name=""),  # 空字符串会使用默认值
        config=PipelineConfig(),
    )
    findings = orchestrator.run("/Users/lijinqi13/Code/agent-safety/evals/ghsa/repos/create-mcp-server-stdio-GHSA-3ch2-jxxc-v4xf.json-32e03b8")
    print(f"Findings: {len(findings)} items")
    simple_output(findings)
    #json_output(findings)