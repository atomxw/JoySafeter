"""
SecurityFinding filtering and validation module.

This module provides functions for filtering and validating SecurityFinding objects,
can be reused by llm_scanner and pm_scanner.

Supports:
- Basic filtering: severity, confidence, line number validation
- Hard rule filtering: pattern-based common false positive exclusion
"""

from __future__ import annotations
import sys
from pathlib import Path
import re
import time
import logging
from dataclasses import dataclass, field
from typing import Iterable, Optional, Dict, Any, List, Pattern, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from scanner.data_types import SecurityFinding, FilterStrategyConfig

logger = logging.getLogger(__name__)

# Severity level mapping (module-level constant to avoid repeated creation)
SEVERITY_LEVELS: dict[str, int] = {"low": 1, "medium": 2, "high": 3, "critical": 4}
VALID_SEVERITIES: set[str] = {"low", "medium", "high", "critical", "info"}

def filter_findings(
    findings: Iterable[SecurityFinding],
    *,
    min_severity: str | None = None,
    min_confidence: float | None = None,
    require_valid_lines: bool = True,
) -> list[SecurityFinding]:
    """
    Filter SecurityFinding list.

    Args:
        findings: Iterable of SecurityFinding objects
        min_severity: Minimum severity level ("low", "medium", "high", "critical"),
                      only keep findings greater than or equal to this level
        min_confidence: Minimum confidence (0.0-1.0), only keep findings greater than or equal to this confidence
        require_valid_lines: Whether start_line and end_line must be valid (> 0)

    Returns:
        Filtered SecurityFinding list
    """
    # Precompute minimum severity level (if specified)
    min_level = None
    if min_severity is not None:
        min_level = SEVERITY_LEVELS.get(min_severity.lower(), 0)
    
    filtered: list[SecurityFinding] = []
    
    for finding in findings:
        # Validate severity
        if min_level is not None:
            finding_level = SEVERITY_LEVELS.get(finding.severity.lower(), 0)
            if finding_level < min_level:
                continue
        
        # Validate confidence
        if min_confidence is not None:
            if finding.confidence < min_confidence:
                continue
        
        # Validate line numbers
        if require_valid_lines:
            if finding.start_line is None or finding.start_line <= 0:
                continue
            if finding.end_line is None or finding.end_line <= 0:
                continue
            if finding.end_line < finding.start_line:
                continue
        
        filtered.append(finding)
    
    return filtered


def validate_finding(finding: SecurityFinding) -> bool:
    """
    Validate if a single SecurityFinding object is valid.

    Args:
        finding: SecurityFinding object to validate

    Returns:
        Returns True if finding is valid, otherwise False
    """
    # Check required fields
    if not finding.finding_id:
        return False
    if not finding.source:
        return False
    if not finding.severity:
        return False
    if not finding.title:
        return False
    if not finding.file_path:
        return False
    
    # Check if severity value is valid
    if finding.severity.lower() not in VALID_SEVERITIES:
        return False
    
    # Check confidence range
    if not (0.0 <= finding.confidence <= 1.0):
        return False
    
    # Check line number validity
    if finding.start_line is not None and finding.start_line <= 0:
        return False
    if finding.end_line is not None and finding.end_line <= 0:
        return False
    if (finding.start_line is not None and 
        finding.end_line is not None and 
        finding.end_line < finding.start_line):
        return False
    
    return True


def filter_invalid_findings(
    findings: Iterable[SecurityFinding],
    use_hard_exclusions: bool = True,
) -> list[SecurityFinding]:
    """
    Filter out invalid SecurityFinding objects.

    This function will:
    1. Validate basic validity of finding (required fields, severity, confidence, line numbers, etc.)
    2. If enabled, apply hard rules to exclude common false positives (based on HardExclusionRules)

    Args:
        findings: Iterable of SecurityFinding objects
        use_hard_exclusions: Whether to apply hard rule exclusions (default True)

    Returns:
        List containing only valid findings not excluded by hard rules
    """
    filtered: list[SecurityFinding] = []
    
    for finding in findings:
        # Step 1: Basic validation
        if not validate_finding(finding):
            continue
        
        # Step 2: Hard rule exclusion (if enabled)
        if use_hard_exclusions:
            exclusion_reason = HardExclusionRules.get_exclusion_reason(finding)
            if exclusion_reason:
                logger.debug(f"Hard rule excluded finding {finding.finding_id}: {exclusion_reason}")
                continue
        
        filtered.append(finding)
    
    return filtered


def apply_filter_strategy(
    findings: Iterable[SecurityFinding],
    config: FilterStrategyConfig,
) -> list[SecurityFinding]:
    """
    Apply filtering strategy according to FilterStrategyConfig.
    
    This function unifies filtering logic, applying filters in the following order:
    1. Basic filtering (severity, confidence, line number validation)
    2. Hard rule exclusion (if enabled)
    
    Args:
        findings: Iterable of SecurityFinding objects
        config: Filtering strategy configuration
        
    Returns:
        Filtered SecurityFinding list
    """
    # First apply basic filtering (severity, confidence, line numbers)
    filtered = filter_findings(
        findings,
        min_severity=config.min_severity,
        min_confidence=config.min_confidence,
        require_valid_lines=config.require_valid_lines,
    )
    
    # Then apply hard rule exclusion (if enabled)
    if config.use_hard_exclusions:
        filtered = filter_invalid_findings(
            filtered,
            use_hard_exclusions=True,
        )
    
    return filtered


def finding_to_dict(finding: SecurityFinding) -> Dict[str, Any]:
    """
    Convert SecurityFinding object to dictionary format.

    Args:
        finding: SecurityFinding object

    Returns:
        Finding in dictionary format, field names compatible with ref_findings_filter
    """
    return {
        "finding_id": finding.finding_id,
        "source": finding.source,
        "severity": finding.severity,
        "confidence": finding.confidence,
        "title": finding.title,
        "description": finding.description,
        "file": finding.file_path,  # ref_findings_filter uses 'file' field
        "file_path": finding.file_path,
        "start_line": finding.start_line,
        "end_line": finding.end_line,
        "remediation": finding.remediation,
        "evidence": finding.evidence,
        "tags": finding.tags,
        "rule_id": finding.rule_id,
        "metadata": finding.metadata,
    }


@dataclass
class FilterStats:
    """Statistics for filtering process."""
    total_findings: int = 0
    hard_excluded: int = 0
    # claude_excluded: int = 0
    kept_findings: int = 0
    exclusion_breakdown: Dict[str, int] = field(default_factory=dict)
    confidence_scores: List[float] = field(default_factory=list)
    runtime_seconds: float = 0.0


class HardExclusionRules:
    """Hard rules for excluding common false positives."""
    
    # Precompiled regex patterns for better performance
    _DOS_PATTERNS: List[Pattern] = [
        re.compile(r'\b(denial of service|dos attack|resource exhaustion)\b', re.IGNORECASE),
        re.compile(r'\b(exhaust|overwhelm|overload).*?(resource|memory|cpu)\b', re.IGNORECASE),
        re.compile(r'\b(infinite|unbounded).*?(loop|recursion)\b', re.IGNORECASE),
    ]
    
    _RATE_LIMITING_PATTERNS: List[Pattern] = [
        re.compile(r'\b(missing|lack of|no)\s+rate\s+limit', re.IGNORECASE),
        re.compile(r'\brate\s+limiting\s+(missing|required|not implemented)', re.IGNORECASE),
        re.compile(r'\b(implement|add)\s+rate\s+limit', re.IGNORECASE),
        re.compile(r'\bunlimited\s+(requests|calls|api)', re.IGNORECASE),
    ]
    
    _RESOURCE_PATTERNS: List[Pattern] = [
        re.compile(r'\b(resource|memory|file)\s+leak\s+potential', re.IGNORECASE),
        re.compile(r'\bunclosed\s+(resource|file|connection)', re.IGNORECASE),
        re.compile(r'\b(close|cleanup|release)\s+(resource|file|connection)', re.IGNORECASE),
        re.compile(r'\bpotential\s+memory\s+leak', re.IGNORECASE),
        re.compile(r'\b(database|thread|socket|connection)\s+leak', re.IGNORECASE),
    ]
    
    _OPEN_REDIRECT_PATTERNS: List[Pattern] = [
        re.compile(r'\b(open redirect|unvalidated redirect)\b', re.IGNORECASE),
        re.compile(r'\b(redirect.(attack|exploit|vulnerability))\b', re.IGNORECASE),
        re.compile(r'\b(malicious.redirect)\b', re.IGNORECASE),
    ]
    
    _MEMORY_SAFETY_PATTERNS: List[Pattern] = [
        re.compile(r'\b(buffer overflow|stack overflow|heap overflow)\b', re.IGNORECASE),
        re.compile(r'\b(oob)\s+(read|write|access)\b', re.IGNORECASE),
        re.compile(r'\b(out.?of.?bounds?)\b', re.IGNORECASE),
        re.compile(r'\b(memory safety|memory corruption)\b', re.IGNORECASE),
        re.compile(r'\b(use.?after.?free|double.?free|null.?pointer.?dereference)\b', re.IGNORECASE),
        re.compile(r'\b(segmentation fault|segfault|memory violation)\b', re.IGNORECASE),
        re.compile(r'\b(bounds check|boundary check|array bounds)\b', re.IGNORECASE),
        re.compile(r'\b(integer overflow|integer underflow|integer conversion)\b', re.IGNORECASE),
        re.compile(r'\barbitrary.?(memory read|pointer dereference|memory address|memory pointer)\b', re.IGNORECASE),
    ]

    _REGEX_INJECTION: List[Pattern] = [
        re.compile(r'\b(regex|regular expression)\s+injection\b', re.IGNORECASE),
        re.compile(r'\b(regex|regular expression)\s+denial of service\b', re.IGNORECASE),
        re.compile(r'\b(regex|regular expression)\s+flooding\b', re.IGNORECASE),
    ]
    
    _SSRF_PATTERNS: List[Pattern] = [
        re.compile(r'\b(ssrf|server\s+.?side\s+.?request\s+.?forgery)\b', re.IGNORECASE),
    ]
    
    @classmethod
    def get_exclusion_reason(cls, finding: SecurityFinding) -> Optional[str]:
        """Check if finding should be excluded based on hard rules.
        
        Args:
            finding: SecurityFinding object to check
            
        Returns:
            Returns exclusion reason if should be excluded, otherwise None
        """
        # Check if in Markdown file
        file_path = finding.file_path or ''
        if file_path.lower().endswith('.md'):
            return "Finding in Markdown documentation file"
        
        description = finding.description or ''
        title = finding.title or ''
        
        combined_text = f"{title} {description}".lower()
        
        # Check DOS patterns
        for pattern in cls._DOS_PATTERNS:
            if pattern.search(combined_text):
                return "Generic DOS/resource exhaustion finding (low signal)"
        
        # Check rate limiting patterns
        for pattern in cls._RATE_LIMITING_PATTERNS:
            if pattern.search(combined_text):
                return "Generic rate limiting recommendation"
        
        # Check resource patterns - always exclude
        for pattern in cls._RESOURCE_PATTERNS:
            if pattern.search(combined_text):
                return "Resource management finding (not a security vulnerability)"
        
        # Check open redirect patterns
        for pattern in cls._OPEN_REDIRECT_PATTERNS:
            if pattern.search(combined_text):
                return "Open redirect vulnerability (not high impact)"
        
        # Check regex injection patterns
        for pattern in cls._REGEX_INJECTION:
            if pattern.search(combined_text):
                return "Regex injection finding (not applicable)"
        
        # Check memory safety patterns - exclude if not in C/C++ files
        c_cpp_extensions = {'.c', '.cc', '.cpp', '.h', '.hpp'}
        file_ext = ''
        if '.' in file_path:
            file_ext = f".{file_path.lower().split('.')[-1]}"
        
        # If file doesn't have C/C++ extension (including no extension), exclude memory safety findings
        if file_ext not in c_cpp_extensions:
            for pattern in cls._MEMORY_SAFETY_PATTERNS:
                if pattern.search(combined_text):
                    return "Memory safety finding in non-C/C++ code (not applicable)"
        
        # Check SSRF patterns - only exclude in HTML files
        html_extensions = {'.html', '.htm'}
        
        # If file has HTML extension, exclude SSRF findings
        if file_ext in html_extensions:
            for pattern in cls._SSRF_PATTERNS:
                if pattern.search(combined_text):
                    return "SSRF finding in HTML file (not applicable to client-side code)"
        
        return None


class FindingsFilter:
    """Main filtering class for security findings."""
    
    def __init__(self, 
                 use_hard_exclusions: bool = True,
                 ):
        """Initialize findings filter.
        
        Args:
            use_hard_exclusions: Whether to apply hard rule exclusions
        """
        self.use_hard_exclusions = use_hard_exclusions
    def filter_findings(self, 
                       findings: List[SecurityFinding],
                       ) -> Tuple[bool, Dict[str, Any], FilterStats]:
        """Filter security findings to remove false positives.
        
        Args:
            findings: SecurityFinding list from scan
            
        Returns:
            (success, filtered_results, stats) tuple
        """
        start_time = time.time()
        
        if not findings:
            stats = FilterStats(total_findings=0, runtime_seconds=0.0)
            return True, {
                "filtered_findings": [],
                "excluded_findings": [],
                "analysis_summary": {
                    "total_findings": 0,
                    "kept_findings": 0,
                    "excluded_findings": 0,
                    "exclusion_breakdown": {}
                }
            }, stats
        
        logger.info(f"Filtering {len(findings)} security findings")
        
        # Initialize statistics
        stats = FilterStats(total_findings=len(findings))
        
        # Step 1: Apply hard rule exclusions
        findings_after_hard: List[Tuple[int, SecurityFinding]] = []
        excluded_hard: List[Dict[str, Any]] = []
        
        if self.use_hard_exclusions:
            for i, finding in enumerate(findings):
                exclusion_reason = HardExclusionRules.get_exclusion_reason(finding)
                if exclusion_reason:
                    excluded_hard.append({
                        "finding": finding_to_dict(finding),
                        "index": i,
                        "exclusion_reason": exclusion_reason,
                        "filter_stage": "hard_rules"
                    })
                    stats.hard_excluded += 1
                    
                    # Track exclusion breakdown
                    key = exclusion_reason.split('(')[0].strip()
                    stats.exclusion_breakdown[key] = stats.exclusion_breakdown.get(key, 0) + 1
                else:
                    findings_after_hard.append((i, finding))
            
            logger.info(f"Hard rules excluded {stats.hard_excluded} findings")
        else:
            findings_after_hard = [(i, f) for i, f in enumerate(findings)]
        
        findings_after_claude: List[SecurityFinding] = []
        excluded_claude: List[Dict[str, Any]] = []
        for orig_idx, finding in findings_after_hard:
            finding.metadata = finding.metadata.copy() if finding.metadata else {}
            finding.metadata['_filter_metadata'] = {
                'confidence_score': 10.0,  # Default high confidence
                'justification': 'Claude filtering disabled',
            }
            findings_after_claude.append(finding)
            stats.kept_findings += 1
        
        # Merge all excluded findings
        all_excluded = excluded_hard + excluded_claude
        
        # Calculate final statistics
        stats.runtime_seconds = time.time() - start_time
        
        # Build filtering results
        filtered_results = {
            "filtered_findings": [finding_to_dict(f) for f in findings_after_claude],
            "excluded_findings": all_excluded,
            "analysis_summary": {
                "total_findings": stats.total_findings,
                "kept_findings": stats.kept_findings,
                "excluded_findings": len(all_excluded),
                "hard_excluded": stats.hard_excluded,
                # "claude_excluded": stats.claude_excluded,
                "exclusion_breakdown": stats.exclusion_breakdown,
                "average_confidence": sum(stats.confidence_scores) / len(stats.confidence_scores) if stats.confidence_scores else None,
                "runtime_seconds": stats.runtime_seconds
            }
        }
        
        logger.info(f"Filtering completed: {stats.kept_findings}/{stats.total_findings} findings kept "
                    f"({stats.runtime_seconds:.1f}s)")
        
        return True, filtered_results, stats


if __name__ == "__main__":
    """
    Script-style manual testing for finding_filter module
    
    Run with:
        python codes/scanner/initial_scan/finding_filter.py
    """
    
    print("=" * 60)
    print("Starting finding_filter module test")
    print("=" * 60)
    
    # Create test SecurityFinding objects
    def create_test_finding(
        finding_id="test-001",
        source="test_scanner",
        severity="high",
        confidence=0.8,
        title="Test Finding",
        description="This is a test finding",
        file_path="test.py",
        start_line=10,
        end_line=15,
        remediation="Fix this issue",
        evidence={},
        tags=[],
        rule_id="test-rule-001",
        metadata={}
    ):
        return SecurityFinding(
            finding_id=finding_id,
            source=source,
            severity=severity,
            confidence=confidence,
            title=title,
            description=description,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            remediation=remediation,
            evidence=evidence,
            tags=tags,
            rule_id=rule_id,
            metadata=metadata
        )
    
    # Test 1: filter_findings - Basic filtering
    print("\n[Test 1] filter_findings - Basic filtering functionality")
    print("-" * 60)
    
    test_findings = [
        create_test_finding("f1", severity="low", confidence=0.5, start_line=1, end_line=5),
        create_test_finding("f2", severity="medium", confidence=0.7, start_line=10, end_line=15),
        create_test_finding("f3", severity="high", confidence=0.9, start_line=20, end_line=25),
        create_test_finding("f4", severity="critical", confidence=0.95, start_line=30, end_line=35),
        create_test_finding("f5", severity="medium", confidence=0.3, start_line=40, end_line=45),  # Low confidence
        create_test_finding("f6", severity="high", confidence=0.8, start_line=0, end_line=5),  # Invalid line numbers
    ]
    
    # Test minimum severity filtering
    filtered_by_severity = filter_findings(test_findings, min_severity="high")
    print(f"✓ Minimum severity filtering (min_severity='high'): {len(filtered_by_severity)}/{len(test_findings)} findings kept")
    assert len(filtered_by_severity) == 2, f"Expected 2, got {len(filtered_by_severity)}"
    
    # Test minimum confidence filtering
    filtered_by_confidence = filter_findings(test_findings, min_confidence=0.7)
    print(f"✓ Minimum confidence filtering (min_confidence=0.7): {len(filtered_by_confidence)}/{len(test_findings)} findings kept")
    assert len(filtered_by_confidence) == 3, f"Expected 3, got {len(filtered_by_confidence)}"
    
    # Test line number validation
    filtered_by_lines = filter_findings(test_findings, require_valid_lines=True)
    print(f"✓ Line number validation filtering (require_valid_lines=True): {len(filtered_by_lines)}/{len(test_findings)} findings kept")
    assert len(filtered_by_lines) == 5, f"Expected 5, got {len(filtered_by_lines)}"
    
    # Test combined filtering
    filtered_combined = filter_findings(
        test_findings,
        min_severity="medium",
        min_confidence=0.7,
        require_valid_lines=True
    )
    print(f"✓ Combined filtering: {len(filtered_combined)}/{len(test_findings)} findings kept")
    assert len(filtered_combined) == 3, f"Expected 3, got {len(filtered_combined)}"
    
    # Test 2: validate_finding - Validate single finding
    print("\n[Test 2] validate_finding - Validate single finding")
    print("-" * 60)
    
    valid_finding = create_test_finding()
    invalid_findings = [
        create_test_finding(finding_id=""),  # Missing finding_id
        create_test_finding(source=""),  # Missing source
        create_test_finding(severity="invalid"),  # Invalid severity
        create_test_finding(confidence=1.5),  # Confidence out of range
        create_test_finding(start_line=-1),  # Invalid line number
        create_test_finding(start_line=10, end_line=5),  # end_line < start_line
    ]
    
    assert validate_finding(valid_finding), "Valid finding should pass validation"
    print("✓ Valid finding passed validation")
    
    for i, invalid in enumerate(invalid_findings, 1):
        result = validate_finding(invalid)
        assert not result, f"Invalid finding #{i} should be rejected"
        print(f"✓ Invalid finding #{i} correctly rejected")
    
    # Test 3: HardExclusionRules - Hard rule exclusion
    print("\n[Test 3] HardExclusionRules - Hard rule exclusion")
    print("-" * 60)
    
    exclusion_test_cases = [
        ("Markdown file", create_test_finding(file_path="README.md"), "Markdown documentation file"),
        ("DOS pattern", create_test_finding(description="This code has a denial of service vulnerability"), "Generic DOS"),
        ("Rate limiting", create_test_finding(title="Missing rate limiting"), "rate limiting"),
        ("Resource leak", create_test_finding(description="Potential memory leak in this code"), "Resource management"),
        ("Open redirect", create_test_finding(title="Open redirect vulnerability found"), "Open redirect"),
        ("Regex injection", create_test_finding(description="Regex injection vulnerability"), "Regex injection"),
        ("Memory safety (Python)", create_test_finding(file_path="test.py", description="Buffer overflow detected"), "Memory safety"),
        ("Memory safety (C++)", create_test_finding(file_path="test.cpp", description="Buffer overflow detected"), None),  # C++ files should not be excluded
        ("SSRF (HTML)", create_test_finding(file_path="index.html", description="SSRF vulnerability"), "SSRF finding in HTML"),
        ("SSRF (Python)", create_test_finding(file_path="test.py", description="SSRF vulnerability"), None),  # Python files should not be excluded
    ]
    
    for case_name, finding, expected_keyword in exclusion_test_cases:
        reason = HardExclusionRules.get_exclusion_reason(finding)
        if expected_keyword:
            assert reason is not None, f"{case_name}: Should be excluded"
            assert expected_keyword.lower() in reason.lower(), f"{case_name}: Exclusion reason should contain '{expected_keyword}'"
            print(f"✓ {case_name}: Excluded - {reason}")
        else:
            assert reason is None, f"{case_name}: Should not be excluded, but got reason: {reason}"
            print(f"✓ {case_name}: Not excluded (as expected)")
    
    # Test 4: filter_invalid_findings
    print("\n[Test 4] filter_invalid_findings - Filter invalid findings")
    print("-" * 60)
    
    mixed_findings = [
        create_test_finding("v1"),  # Valid
        create_test_finding("v2"),  # Valid
        create_test_finding(finding_id=""),  # Invalid (missing finding_id)
        create_test_finding("e1", description="denial of service attack"),  # Should be excluded by hard rules
        create_test_finding("v3"),  # Valid
    ]
    
    filtered_invalid = filter_invalid_findings(mixed_findings, use_hard_exclusions=True)
    print(f"✓ Filter invalid findings: {len(filtered_invalid)}/{len(mixed_findings)} findings kept")
    assert len(filtered_invalid) == 3, f"Expected 3, got {len(filtered_invalid)}"
    assert all(f.finding_id in ["v1", "v2", "v3"] for f in filtered_invalid), "Kept findings should be valid"
    
    # Test 5: apply_filter_strategy
    print("\n[Test 5] apply_filter_strategy - Apply filtering strategy")
    print("-" * 60)
    
    from scanner.data_types import FilterStrategyConfig
    
    strategy_config = FilterStrategyConfig(
        min_severity="medium",
        min_confidence=0.6,
        require_valid_lines=True,
        use_hard_exclusions=True
    )
    
    strategy_findings = [
        create_test_finding("s1", severity="low", confidence=0.5),  # Severity too low
        create_test_finding("s2", severity="medium", confidence=0.7),  # Pass
        create_test_finding("s3", severity="high", confidence=0.4),  # Confidence too low
        create_test_finding("s4", severity="high", confidence=0.8, description="denial of service"),  # Excluded by hard rules
        create_test_finding("s5", severity="critical", confidence=0.9),  # Pass
    ]
    
    strategy_filtered = apply_filter_strategy(strategy_findings, strategy_config)
    print(f"✓ Apply filtering strategy: {len(strategy_filtered)}/{len(strategy_findings)} findings kept")
    assert len(strategy_filtered) == 2, f"Expected 2, got {len(strategy_filtered)}"
    assert all(f.finding_id in ["s2", "s5"] for f in strategy_filtered), "Kept findings should be s2 and s5"
    
    # Test 6: FindingsFilter - Main filtering class
    print("\n[Test 6] FindingsFilter - Main filtering class")
    print("-" * 60)
    
    filter_instance = FindingsFilter(use_hard_exclusions=True)
    
    filter_test_findings = [
        create_test_finding("ff1", severity="high", confidence=0.8),
        create_test_finding("ff2", severity="medium", confidence=0.7, description="resource leak potential"),
        create_test_finding("ff3", severity="critical", confidence=0.9),
        create_test_finding("ff4", file_path="docs.md", severity="high", confidence=0.8),  # Markdown file
    ]
    
    success, results, stats = filter_instance.filter_findings(filter_test_findings)
    
    assert success, "Filtering should succeed"
    assert len(results["filtered_findings"]) == 2, f"Expected 2 kept, got {len(results['filtered_findings'])}"
    assert len(results["excluded_findings"]) == 2, f"Expected 2 excluded, got {len(results['excluded_findings'])}"
    assert stats.total_findings == 4, f"Total findings should be 4, got {stats.total_findings}"
    assert stats.kept_findings == 2, f"Kept findings should be 2, got {stats.kept_findings}"
    assert stats.hard_excluded == 2, f"Hard rule exclusions should be 2, got {stats.hard_excluded}"
    
    print(f"✓ Filtering succeeded: {stats.kept_findings}/{stats.total_findings} findings kept")
    print(f"✓ Hard rule exclusions: {stats.hard_excluded}")
    print(f"✓ Runtime: {stats.runtime_seconds:.3f} seconds")
    print(f"✓ Exclusion breakdown: {stats.exclusion_breakdown}")
    
    # Test 7: finding_to_dict - Conversion function
    print("\n[Test 7] finding_to_dict - Conversion function")
    print("-" * 60)
    
    test_finding = create_test_finding(
        finding_id="dict-test",
        file_path="test.py",
        start_line=42,
        end_line=50
    )
    
    finding_dict = finding_to_dict(test_finding)
    assert finding_dict["finding_id"] == "dict-test", "finding_id should be correctly converted"
    assert finding_dict["file"] == "test.py", "file field should exist"
    assert finding_dict["file_path"] == "test.py", "file_path field should exist"
    assert finding_dict["start_line"] == 42, "start_line should be correctly converted"
    print("✓ finding_to_dict correctly converts all fields")
    
    # Test 8: Edge cases
    print("\n[Test 8] Edge case testing")
    print("-" * 60)
    
    # Empty list
    empty_filtered = filter_findings([])
    assert len(empty_filtered) == 0, "Empty list should return empty list"
    print("✓ Empty list handled correctly")
    
    # Empty list filtering
    empty_success, empty_results, empty_stats = filter_instance.filter_findings([])
    assert empty_success, "Empty list filtering should succeed"
    assert len(empty_results["filtered_findings"]) == 0, "Empty list should return empty results"
    print("✓ Empty list filtering handled correctly")
    
    # All findings excluded
    all_excluded = [
        create_test_finding("ex1", file_path="README.md"),
        create_test_finding("ex2", description="denial of service"),
        create_test_finding("ex3", description="resource leak potential"),
    ]
    all_excluded_filtered = filter_invalid_findings(all_excluded, use_hard_exclusions=True)
    assert len(all_excluded_filtered) == 0, "Should return empty list after all findings excluded"
    print("✓ All findings excluded case handled correctly")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)

