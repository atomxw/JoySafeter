from __future__ import annotations

import json
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, TextIO

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from scanner.data_types import SecurityFinding  # noqa: E402


def simple_output(
    findings: Iterable[SecurityFinding],
    output: TextIO | None = None,
) -> None:
    """
    美化输出 SecurityFinding 列表，按严重程度分组显示（总分总结构）。

    Args:
        findings: SecurityFinding 的可迭代对象
        output: 输出流，默认为 sys.stdout

    Output Format:
        - 总览部分：显示总数、按严重程度统计
        - 详细列表部分：按严重程度分组（high -> medium -> low），每组内按文件路径和行号排序
        - 总结部分：显示统计信息
    """
    if output is None:
        output = sys.stdout
    
    # 确保 output 不是 None（类型检查）
    assert output is not None

    findings_list = list(findings)
    total_count = len(findings_list)

    if total_count == 0:
        output.write("=" * 80 + "\n")
        output.write("未发现安全告警\n")
        output.write("=" * 80 + "\n")
        return

    # 按严重程度分组
    severity_groups: dict[str, list[SecurityFinding]] = defaultdict(list)
    severity_order = {"high": 0, "medium": 1, "low": 2}
    file_set = set()

    for finding in findings_list:
        severity = finding.severity.lower()
        severity_groups[severity].append(finding)
        file_set.add(finding.file_path)

    # 统计各严重程度数量
    severity_counts = {
        severity: len(findings)
        for severity, findings in severity_groups.items()
    }

    # ==================== 总览部分 ====================
    output.write("=" * 80 + "\n")
    output.write("安全扫描报告 - 总览\n")
    output.write("=" * 80 + "\n")
    output.write(f"\n总计发现 {total_count} 个安全告警\n\n")

    # 按优先级显示严重程度统计
    for severity in ["high", "medium", "low"]:
        count = severity_counts.get(severity, 0)
        if count > 0:
            output.write(f"  {severity.upper():6s}: {count:4d} 个\n")

    # 显示其他严重程度
    other_severities = {
        s: c for s, c in severity_counts.items()
        if s.lower() not in ["high", "medium", "low"]
    }
    if other_severities:
        for severity, count in sorted(other_severities.items()):
            output.write(f"  {severity.upper():6s}: {count:4d} 个\n")

    output.write(f"\n涉及文件数: {len(file_set)}\n")
    output.write("\n" + "=" * 80 + "\n\n")

    # ==================== 详细列表部分 ====================
    output.write("详细告警列表\n")
    output.write("=" * 80 + "\n\n")

    # 按严重程度优先级排序
    sorted_severities = sorted(
        severity_groups.keys(),
        key=lambda s: severity_order.get(s.lower(), 999)
    )

    for severity in sorted_severities:
        findings_in_severity = severity_groups[severity]
        # 按文件路径和行号排序
        findings_in_severity.sort(
            key=lambda f: (f.file_path, f.start_line, f.end_line)
        )

        output.write(f"\n{'=' * 80}\n")
        output.write(f"严重程度: {severity.upper()} ({len(findings_in_severity)} 个)\n")
        output.write("=" * 80 + "\n\n")

        for idx, finding in enumerate(findings_in_severity, 1):
            output.write(f"[{idx}] {finding.title}\n")
            output.write(f"     文件: {finding.file_path}:{finding.start_line}-{finding.end_line}\n")
            output.write(f"     严重程度: {finding.severity} | 置信度: {finding.confidence:.2f}\n")
            output.write(f"     规则ID: {finding.rule_id} | 来源: {finding.source}\n")

            if finding.description:
                output.write(f"     描述: {finding.description}\n")

            if finding.remediation:
                output.write(f"     修复建议: {finding.remediation}\n")

            if finding.tags:
                output.write(f"     标签: {', '.join(finding.tags)}\n")

            if finding.evidence:
                evidence_str = json.dumps(finding.evidence, ensure_ascii=False, indent=8)
                output.write(f"     证据:\n{evidence_str}\n")

            output.write("\n")

    # ==================== 总结部分 ====================
    output.write("\n" + "=" * 80 + "\n")
    output.write("统计总结\n")
    output.write("=" * 80 + "\n")
    output.write(f"\n总告警数: {total_count}\n")
    output.write(f"涉及文件数: {len(file_set)}\n")
    output.write("\n按严重程度分布:\n")
    for severity in ["high", "medium", "low"]:
        count = severity_counts.get(severity, 0)
        if count > 0:
            percentage = (count / total_count) * 100
            output.write(f"  {severity.upper():6s}: {count:4d} 个 ({percentage:5.1f}%)\n")

    if other_severities:
        for severity, count in sorted(other_severities.items()):
            percentage = (count / total_count) * 100
            output.write(f"  {severity.upper():6s}: {count:4d} 个 ({percentage:5.1f}%)\n")

    output.write("\n" + "=" * 80 + "\n")


def json_output(
    findings: Iterable[SecurityFinding],
    output_path: Path | str | TextIO | None = None,
) -> str | None:
    """
    将 SecurityFinding 列表序列化为 JSON 格式输出。

    Args:
        findings: SecurityFinding 的可迭代对象
        output_path: 输出路径（文件路径字符串或 Path 对象）或文件对象。
                     如果为 None，返回 JSON 字符串；如果为文件对象或路径，写入文件并返回 None

    Returns:
        如果 output_path 为 None，返回 JSON 字符串；否则返回 None（已写入文件）

    Examples:
        >>> findings = [SecurityFinding(...), ...]
        >>> json_str = json_output(findings)
        >>> json_output(findings, "output.json")
    """
    findings_list = list(findings)

    # 转换为字典列表
    findings_dict = [asdict(finding) for finding in findings_list]

    # 序列化为 JSON
    json_str = json.dumps(
        findings_dict,
        indent=2,
        ensure_ascii=False,
        sort_keys=False,
    )

    # 如果指定了输出路径，写入文件
    if output_path is not None:
        if isinstance(output_path, (str, Path)):
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_str)
        else:
            # 文件对象
            output_path.write(json_str)
        return None

    return json_str

