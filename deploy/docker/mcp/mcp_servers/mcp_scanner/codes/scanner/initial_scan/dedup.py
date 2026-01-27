"""
SecurityFinding deduplication functionality.
"""

from __future__ import annotations
import sys
from typing import Callable, Iterable
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from scanner.data_types import SecurityFinding


def deduplicate_findings(
    findings: Iterable[SecurityFinding],
    key_func: Callable[[SecurityFinding], tuple] | None = None,
) -> list[SecurityFinding]:
    """
    Deduplicate SecurityFinding list.

    Args:
        findings: Iterable of SecurityFinding objects
        key_func: Optional deduplication key function. If None, uses default strategy:
                  (file_path, start_line, end_line)

    Returns:
        Deduplicated SecurityFinding list, keeping first occurrence

    Examples:
        >>> findings = [
        ...     SecurityFinding(..., file_path="a.py", start_line=10, end_line=12, rule_id="rule1"),
        ...     SecurityFinding(..., file_path="a.py", start_line=10, end_line=12, rule_id="rule2"),
        ... ]
        >>> deduplicated = deduplicate_findings(findings)
        >>> len(deduplicated)
        1
    """
    if key_func is None:
        # Default deduplication strategy: based on file path and line number range
        def default_key(finding: SecurityFinding) -> tuple:
            return (
                finding.file_path,
                finding.start_line,
                finding.end_line,
            )
        key_func = default_key

    seen = set()
    result = []

    for finding in findings:
        key = key_func(finding)
        if key not in seen:
            seen.add(key)
            result.append(finding)

    return result


def deduplicate_by_fields(
    findings: Iterable[SecurityFinding],
    *fields: str,
) -> list[SecurityFinding]:
    """
    Deduplicate based on specified fields.

    Args:
        findings: Iterable of SecurityFinding objects
        *fields: Field names for deduplication, can pass one or more field names.
                 Supported fields include: source, confidence, start_line, end_line,
                 file_path, title, rule_id, severity, finding_id, etc.

    Returns:
        Deduplicated SecurityFinding list

    Examples:
        >>> # Deduplicate by source
        >>> deduplicated = deduplicate_by_fields(findings, "source")
        >>>
        >>> # Deduplicate by confidence, start_line, end_line
        >>> deduplicated = deduplicate_by_fields(findings, "confidence", "start_line", "end_line")
        >>>
        >>> # Deduplicate by single field
        >>> deduplicated = deduplicate_by_fields(findings, "rule_id")
    """
    if not fields:
        raise ValueError("At least one field must be specified for deduplication")

    # Validate field names
    valid_fields = {
        "finding_id", "source", "severity", "confidence", "title",
        "description", "file_path", "start_line", "end_line",
        "remediation", "rule_id"
    }
    invalid_fields = set(fields) - valid_fields
    if invalid_fields:
        raise ValueError(f"Invalid field names: {invalid_fields}")

    def fields_key(finding: SecurityFinding) -> tuple:
        """Dynamically build deduplication key based on specified fields"""
        return tuple(getattr(finding, field) for field in fields)

    return deduplicate_findings(findings, key_func=fields_key)


if __name__ == "__main__":
    # Create example SecurityFinding objects
    findings = [
        SecurityFinding(
            finding_id="1",
            source="semgrep",
            severity="high",
            confidence=0.9,
            title="SQL Injection Vulnerability",
            description="Potential SQL injection risk detected",
            file_path="/path/to/file1.py",
            start_line=10,
            end_line=12,
            remediation="Use parameterized queries",
            evidence={"code": "query = f'SELECT * FROM users WHERE id = {user_id}'"},
            tags=["sql-injection", "security"],
            rule_id="rule-001",
            metadata={"tool": "semgrep"},
        ),
        SecurityFinding(
            finding_id="2",
            source="llm",
            severity="high",
            confidence=0.85,
            title="SQL Injection Vulnerability",
            description="Potential SQL injection risk detected",
            file_path="/path/to/file1.py",
            start_line=10,
            end_line=12,  # Same location, different rule_id
            remediation="Use parameterized queries",
            evidence={"code": "query = f'SELECT * FROM users WHERE id = {user_id}'"},
            tags=["sql-injection"],
            rule_id="rule-002",  # Different rule_id
            metadata={"tool": "llm"},
        ),
        SecurityFinding(
            finding_id="3",
            source="semgrep",
            severity="medium",
            confidence=0.7,
            title="Hardcoded Password",
            description="Hardcoded password detected",
            file_path="/path/to/file2.py",
            start_line=25,
            end_line=25,
            remediation="Use environment variables or key management service",
            evidence={"code": "password = '123456'"},
            tags=["hardcoded-secret"],
            rule_id="rule-003",
            metadata={},
        ),
        SecurityFinding(
            finding_id="4",
            source="semgrep",
            severity="medium",
            confidence=0.7,
            title="Hardcoded Password",
            description="Hardcoded password detected",
            file_path="/path/to/file2.py",
            start_line=25,
            end_line=25,  # Same location, should be deduplicated
            remediation="Use environment variables or key management service",
            evidence={"code": "password = '123456'"},
            tags=["hardcoded-secret"],
            rule_id="rule-003",
            metadata={},
        ),
    ]

    print("=" * 60)
    print("Original findings count:", len(findings))
    print("=" * 60)
    for i, finding in enumerate(findings, 1):
        print(f"\n{i}. {finding.title}")
        print(f"   File: {finding.file_path}:{finding.start_line}-{finding.end_line}")
        print(f"   Rule ID: {finding.rule_id}")
        print(f"   Source: {finding.source}")

    # Use default deduplication strategy (based on location)
    deduplicated = deduplicate_findings(findings)
    print("\n" + "=" * 60)
    print("Deduplicated findings count (default strategy, based on location):", len(deduplicated))
    print("=" * 60)
    for i, finding in enumerate(deduplicated, 1):
        print(f"\n{i}. {finding.title}")
        print(f"   File: {finding.file_path}:{finding.start_line}-{finding.end_line}")
        print(f"   Rule ID: {finding.rule_id}")
        print(f"   Source: {finding.source}")

    # Use dynamic field deduplication: deduplicate by source
    deduplicated_by_source = deduplicate_by_fields(findings, "source")
    print("\n" + "=" * 60)
    print("Deduplicated findings count (by source):", len(deduplicated_by_source))
    print("=" * 60)
    for i, finding in enumerate(deduplicated_by_source, 1):
        print(f"\n{i}. {finding.title}")
        print(f"   File: {finding.file_path}:{finding.start_line}-{finding.end_line}")
        print(f"   Rule ID: {finding.rule_id}")
        print(f"   Source: {finding.source}")

    # Use dynamic field deduplication: deduplicate by confidence, start_line, end_line
    deduplicated_by_fields = deduplicate_by_fields(findings, "confidence", "start_line", "end_line")
    print("\n" + "=" * 60)
    print("Deduplicated findings count (by confidence, start_line, end_line):", len(deduplicated_by_fields))
    print("=" * 60)
    for i, finding in enumerate(deduplicated_by_fields, 1):
        print(f"\n{i}. {finding.title}")
        print(f"   File: {finding.file_path}:{finding.start_line}-{finding.end_line}")
        print(f"   Rule ID: {finding.rule_id}")
        print(f"   Source: {finding.source}")
        print(f"   Confidence: {finding.confidence}")
