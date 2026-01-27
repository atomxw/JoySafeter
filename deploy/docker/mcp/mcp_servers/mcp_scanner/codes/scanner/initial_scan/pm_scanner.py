"""
Encapsulates pattern matching scan workflow.
"""

from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import logging
import subprocess
from collections.abc import Mapping, Sequence
from typing import cast

from scanner.data_types import ScanContext, SecurityFinding


logger = logging.getLogger(__name__)

RawPayload = dict[str, object]
RawSemgrepResult = Mapping[str, object]

DEFAULT_RULE_DIR = Path(__file__).parent.parent.parent / "configs" / "initial_scan" / "rules"
DEFAULT_OUTPUT_FILENAME = "pm_scanner.json"
DEFAULT_CONFIDENCE = 0.5
DEFAULT_SEVERITY = "INFO"

class LocalPMScanner:
    """Executes scans sequentially using local pattern matching tools (e.g., semgrep)."""

    def __init__(
        self,
        rule_paths: Sequence[Path] | None = None,
        extra_args: Sequence[str] | None = None,
    ) -> None:
        self._rule_paths: tuple[Path, ...] = (
            tuple(rule_paths) if rule_paths else (DEFAULT_RULE_DIR,)
        )
        self._extra_args: tuple[str, ...] = tuple(extra_args) if extra_args else ()

    def scan(self, context: ScanContext) -> list[SecurityFinding]:
        workdir = self._resolve_workdir(context)
        if not workdir.exists():
            raise FileNotFoundError(f"Scan root directory does not exist: {workdir}")
        output_file = self._resolve_output_file(context)
        command = self._build_command(context, output_file)

        logger.debug("Running pattern matching scan: cwd=%s command=%s", workdir, command)
        completed = subprocess.run(
            command,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            check=False,
        )

        self._log_stderr(completed.stderr)
        self._validate_returncode(completed)

        payload = self._load_payload(output_file, completed.stdout)
        return self._extract_findings(payload)

    def _build_command(self, context: ScanContext, output_file: Path | None) -> list[str]:
        command: list[str] = [
            "semgrep",
            "scan",
            "--json",
            "--no-error",
            "--no-git-ignore",
        ]  # todo: add metrics=off
        command.extend(self._extra_args)
        command.extend(self._build_rule_args())

        if output_file is not None:
            command.extend(("--json-output", str(output_file)))

        command.extend(self._resolve_targets(context))
        return command

    def _build_rule_args(self) -> list[str]:
        args: list[str] = []
        for rule_path in self._rule_paths:
            args.extend(("--config", str(rule_path)))
        return args

    def _resolve_workdir(self, context: ScanContext) -> Path:
        return context.root_path

    def _resolve_output_file(self, context: ScanContext) -> Path | None:
        output_dir = context.output_path
        if output_dir is None:
            return None
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / DEFAULT_OUTPUT_FILENAME

    def _resolve_targets(self, context: ScanContext) -> list[str]:
        if context.root_path.exists():
            return ["."]
        return [str(context.root_path)]

    def _log_stderr(self, stderr: str) -> None:
        stderr = stderr.strip()
        if stderr:
            logger.warning("Pattern matching scan (stderr): %s", stderr)

    def _validate_returncode(self, completed: subprocess.CompletedProcess[str]) -> None:
        if completed.returncode not in (0,):
            raise Exception(
                f"Pattern matching scan execution failed, exit code {completed.returncode}: "
                f"{completed.stderr or completed.stdout}"
            )

    def _load_payload(self, output_file: Path | None, stdout: str) -> RawPayload:
        if output_file is not None:
            return self._load_payload_from_file(output_file)
        return self._parse_payload(stdout)

    def _load_payload_from_file(self, output_file: Path) -> RawPayload:
        if not output_file.exists():
            logger.debug("Pattern matching scan did not generate output file: %s", output_file)
            return {}

        try:
            with output_file.open("r", encoding="utf-8") as fp:
                payload = json.load(fp)
        except json.JSONDecodeError as exc:
            raise Exception(f"Unable to parse pattern matching scan output file {output_file} as JSON") from exc
        except OSError as exc:
            raise Exception(f"Unable to read pattern matching scan output file {output_file}") from exc

        return cast(RawPayload, payload)

    def _parse_payload(self, raw_output: str) -> RawPayload:
        raw_output = (raw_output or "").strip()
        if not raw_output:
            return {}
        try:
            return cast(RawPayload, json.loads(raw_output))
        except json.JSONDecodeError as exc:
            raise Exception("Unable to parse semgrep stdout as JSON") from exc

    def _extract_findings(self, payload: RawPayload) -> list[SecurityFinding]:
        errors = self._as_sequence(payload.get("errors"))

        if errors:
            logger.warning("Pattern matching scan returned %d errors: %s", len(errors), errors)

        results = self._as_sequence(payload.get("results"))

        findings: list[SecurityFinding] = []
        for raw in results:
            if not isinstance(raw, Mapping):
                logger.debug("Ignoring non-dict scan result: %s", raw)
                continue
            finding = self._build_finding(raw)
            if finding is not None:
                findings.append(finding)
        return findings

    def _build_finding(self, result: RawSemgrepResult) -> SecurityFinding | None:
        check_id = result.get("check_id")
        if not isinstance(check_id, str):
            logger.debug("Ignoring pattern matching scan result missing check_id: %s", result)
            return None

        path_value = result.get("path")
        file_path = Path(path_value) if isinstance(path_value, str) else Path(".")

        start = result.get("start") or {}
        end = result.get("end") or {}

        start_line = start.get("line") if isinstance(start, Mapping) else None
        end_line = end.get("line") if isinstance(end, Mapping) else None

        extra = result.get("extra") if isinstance(result.get("extra"), Mapping) else {}
        if not isinstance(extra, Mapping):
            extra = {}

        message = extra.get("message")
        severity_str = extra.get("severity")
        severity = self._normalize_severity(severity_str)

        fingerprint = extra.get("fingerprint")
        finding_id = (
            fingerprint
            if isinstance(fingerprint, str)
            else f"{check_id}:{file_path}:{start_line}:{end_line}"
        )

        metadata = extra.get("metadata") if isinstance(extra.get("metadata"), Mapping) else None

        confidence_value = extra.get("confidence")
        confidence = self._normalize_confidence(confidence_value)

        remediation = extra.get("fix") if isinstance(extra.get("fix"), str) else None
        description = self._build_description(extra, metadata, message)

        evidence = self._build_evidence(extra)
        tags = self._build_tags(metadata)

        return SecurityFinding(
            finding_id=finding_id,
            source="semgrep",
            severity=severity,
            confidence=confidence,
            title=message if isinstance(message, str) and message else check_id,
            description=description,
            file_path=str(file_path),
            start_line=start_line if isinstance(start_line, int) else 0,
            end_line=end_line if isinstance(end_line, int) else 0,
            remediation=remediation,
            evidence=evidence if isinstance(evidence, dict) else {},
            tags=list(tags),
            rule_id=check_id,
            metadata=metadata if isinstance(metadata, dict) else {},
        )


    @staticmethod
    def _as_sequence(value: object) -> Sequence[object]:
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return value
        return ()

    @staticmethod
    def _build_description(
        extra: Mapping[str, object], metadata: Mapping[str, object] | None, message: object
    ) -> str:
        parts: list[str] = []
        if isinstance(message, str) and message:
            parts.append(message)

        if metadata:
            summary = metadata.get("description")
            if isinstance(summary, str) and summary:
                parts.append(summary)
            references = metadata.get("references")
            if isinstance(references, Sequence) and not isinstance(references, (str, bytes)):
                links = [ref for ref in references if isinstance(ref, str)]
                if links:
                    parts.append("References: " + ", ".join(links))

        lines = extra.get("lines")
        if isinstance(lines, str) and lines:
            parts.append("Code snippet:\n" + lines)

        return "\n\n".join(parts) if parts else str(message) if message is not None else ""

    @staticmethod
    def _build_evidence(extra: Mapping[str, object]) -> Mapping[str, object] | None:
        evidence: dict[str, object] = {}
        metavars = extra.get("metavars")
        if isinstance(metavars, Mapping) and metavars:
            evidence["metavars"] = metavars
        lines = extra.get("lines")
        if isinstance(lines, str) and lines:
            evidence["snippet"] = lines
        if not evidence:
            return None
        return evidence

    @staticmethod
    def _build_tags(metadata: Mapping[str, object] | None) -> Sequence[str]:
        if not metadata:
            return ()

        tags: list[str] = []
        for key, value in metadata.items():
            if isinstance(value, str):
                tags.append(value)
            elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                tags.extend(str(item) for item in value if isinstance(item, str))
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_tags: list[str] = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        return tuple(unique_tags)

    @staticmethod
    def _normalize_severity(value: object) -> str:
        if isinstance(value, str):
            normalized = value.strip().upper()
            if normalized in {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}:
                return normalized
        return DEFAULT_SEVERITY

    @staticmethod
    def _normalize_confidence(value: object) -> float:
        if isinstance(value, (int, float)):
            return LocalPMScanner._clamp_confidence(float(value))
        if isinstance(value, str):
            normalized = value.strip().lower()
            try:
                return LocalPMScanner._clamp_confidence(float(normalized))
            except ValueError:
                mapping = {
                    "critical": 0.95,
                    "high": 0.8,
                    "medium": 0.5,
                    "low": 0.2,
                }
                if normalized in mapping:
                    return mapping[normalized]
        return DEFAULT_CONFIDENCE

    @staticmethod
    def _clamp_confidence(value: float) -> float:
        return max(0.0, min(1.0, value))

if __name__ == "__main__":
    scanner = LocalPMScanner()
    root_path = Path(
        "/Users/lijinqi13/Code/agent-safety/evals/ghsa/repos/create-mcp-server-stdio-GHSA-3ch2-jxxc-v4xf.json-32e03b8"
    ).resolve()
    output_dir = root_path / ".pm_scanner"

    context = ScanContext(
        root_path=root_path,
        languages=("python",),
        output_path=output_dir,
    )

    secfindings = list(scanner.scan(context))

    if not secfindings:
        print("✅ No alerts found.")

    print(f"Found {len(secfindings)} alerts:")
    for secfinding in secfindings:
        print("-" * 60)
        print(f"Rule: {secfinding.rule_id}")
        print(f"File: {secfinding.file_path}")
        print(f"Location: {secfinding.start_line}-{secfinding.end_line}")
        print(f"Severity: {secfinding.severity}")
        print(f"Confidence: {secfinding.confidence:.2f}")
        print(f"Title: {secfinding.title}")
        if secfinding.description:
            print()
            print(secfinding.description)