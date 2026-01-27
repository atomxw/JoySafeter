"""
LLM-based source file review.
"""
from __future__ import annotations

import json
import logging
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openai import OpenAI
from yaml import load
from yaml.loader import SafeLoader

from scanner.data_types import ScanContext, SecurityFinding, _ReviewJob
from scanner.initial_scan.finding_filter import filter_invalid_findings

logger = logging.getLogger(__name__)


class OpenAILLMScanner:
    """LLM scanner based on OpenAI API."""

    def __init__(
        self,
        prompt_path: str = "",
        model_name: str = "",
        max_workers: int = 4,
    ) -> None:
        """
        Initialize LLM scanner.

        Args:
            prompt_path: Prompt file path, if empty then use default path
            model_name: Model name, if empty then use default value from config file
            max_workers: Maximum concurrent worker threads, if 0 then use default value from config file
        """
        # Load config file
        config_path = Path(__file__).parent.parent.parent / "configs" / "default.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = load(f, Loader=SafeLoader)
        
        # Set prompt path
        if prompt_path:
            self.prompt_path = Path(prompt_path)
        else:
            self.prompt_path = Path(__file__).parent.parent.parent / "configs" / "initial_scan" / "prompts"
        
        # Set concurrency
        if max_workers > 0:
            self.max_workers = max_workers
        else:
            self.max_workers = self._config.get("llm", {}).get("max_workers", 4)
        
        # Initialize OpenAI client
        llm_config = self._config.get("llm", {})
        self.model = OpenAI(
            api_key=llm_config.get("api_key", ""),
            base_url=llm_config.get("base_url", "")
        )
        
        # Set model name
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = llm_config.get("model_name", "")
        
    def call_model(self, user_prompt: str,temperature: float = 0.7) -> str:
        """
        Call LLM model.

        Args:
            user_prompt: User prompt
            temperature: Temperature
        Returns:
            Content returned by LLM, returns empty string if empty
        """
        try:
            response = self.model.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=temperature,
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            logger.error(f"Failed to call LLM model: {e}")
            return ""
    def _review_method_analysis(self, job: _ReviewJob,read_content: str) -> tuple[str,list[dict[str,str]]]:
        """
        Execute a single review task (runs in thread).
        Contains two stages: initial analysis and clarification verification.
        """

        # Stage 1: Initial security analysis
        analysis_prompt = job.prompts.get('security_review', '')
        if not analysis_prompt:
            logger.warning("Missing security_review prompt")
            return "",[]
        
        context1 = analysis_prompt.replace("{{code}}", read_content)
        output1 = self.call_model(context1)
        messages = [
            {"role": "user", "content": context1},
            {"role": "assistant", "content": output1},
        ]
        if not output1:
            logger.warning(f"Stage 1 analysis returned no result: {job.absolute_path}")
            return "",[]
        
        # Stage 2: Clarification verification
        clarify_prompt = job.prompts.get('clarify_security_review', '')
        if not clarify_prompt:
            logger.warning("Missing clarify_security_review prompt, returning stage 1 analysis result")
            return output1, messages
        
        # Replace placeholders: code and first analysis result
        context2 = clarify_prompt.replace("{{code}}", read_content)
        context2 = context2.replace("{{analysis}}", output1)
        
        output2 = self.call_model(context2)
        if not output2:
            logger.warning(f"Clarification stage returned no result: {job.absolute_path}, returning stage 1 analysis result")
            return output1, messages
        
        # Add clarification stage conversation to messages list
        messages.append({"role": "user", "content": context2})
        messages.append({"role": "assistant", "content": output2})
        
        return output2, messages
    def _review_method_two_stage(self, job: _ReviewJob,read_content: str) -> tuple[str,list[dict[str,str]]]:
        """
        Execute a single review task (runs in thread).
        """

        analysis_prompt = job.prompts.get('analysis', '')
        if not analysis_prompt:
            logger.warning("Missing analysis prompt")
            return "",[]
        
        context1 = analysis_prompt.replace("{{code}}", read_content)
        output1 = self.call_model(context1)
        messages = [
            {"role": "user", "content": context1},
            {"role": "assistant", "content": output1},
        ]
        if not output1:
            logger.warning(f"Stage 1 analysis returned no result: {job.absolute_path}")
            return "",[]
        para_output_prompt = job.prompts.get('para_output', '')
        if not para_output_prompt:
            logger.warning("Missing para_output prompt")
            return "",[]
        context2 = para_output_prompt.replace("{{context}}", output1)
        output = self.call_model(context2)
        messages.append({"role": "user", "content": context2})
        messages.append({"role": "assistant", "content": output})
        return output,messages
    def _review_method_self_consistent(self, job: _ReviewJob,read_content: str) -> tuple[str,list[dict[str,str]]]:
        """
        Execute a single review task (runs in thread).
        """

        analysis_prompt = job.prompts.get('security_review_cn', '')
        if not analysis_prompt:
            logger.warning("Missing security_review_cn prompt")
            return "",[]
        
        context1 = analysis_prompt.replace("{{code}}", read_content)
        output1 = self.call_model(context1,temperature=1)
        messages = [
            {"role": "user", "content": context1},
            {"role": "assistant", "content": output1},
        ]
        if not output1:
            logger.warning(f"self_consistent1 analysis returned no result: {job.absolute_path}")
            return "",[]
        
        output2 = self.call_model(context1,temperature=1)
        messages = [
            {"role": "user", "content": context1},
            {"role": "assistant", "content": output2},
        ]
        if not output2:
            logger.warning(f"self_consistent2 analysis returned no result: {job.absolute_path}")
            return "",[]
                
        output3 = self.call_model(context1,temperature=1)
        if not output3:
            logger.warning(f"self_consistent3 analysis returned no result: {job.absolute_path}")
            return "",[]
        
        # Use majority logic: select the output that appears most frequently
        outputs = [output1, output2, output3]
        counter = Counter(outputs)
        # Get the most common output, if multiple exist return the first one
        output = counter.most_common(1)[0][0]
        
        # Build messages, including the finally selected output
        messages = [
            {"role": "user", "content": context1},
            {"role": "assistant", "content": output},
        ]
        
        return output, messages
        
    def _execute_review_job(self, job: _ReviewJob) -> list[SecurityFinding]:  # pragma: no cover
        """
        Execute a single review task (runs in thread).

        Args:
            job: Review task object

        Returns:
            List of SecurityFinding objects, returns empty list if no vulnerabilities found or parsing failed
        """
        try:
            # Read file content
            file_path = Path(job.absolute_path)
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return []
            
            read_content = file_path.read_text(encoding="utf-8")
            
            output,messages = self._review_method_two_stage(job, read_content)
            # Parse JSON output
            try:
                # Remove possible code block markers
                cleaned_output = output.replace("```json", "").replace("```", "").strip()
                
                # Try to parse JSON
                parsed_output = json.loads(cleaned_output)
                
                # If null is returned, no vulnerabilities found
                if parsed_output is None:
                    return []
                
                findings: list[SecurityFinding] = []
                
                # Handle list case
                if isinstance(parsed_output, list):
                    for idx, item in enumerate(parsed_output):
                        if not isinstance(item, dict) or 'severity' not in item:
                            logger.debug(f"List item {idx} missing required fields: {file_path}")
                            continue
                        
                        # Build SecurityFinding object
                        start_line = item.get("start_line")
                        end_line = item.get("end_line")
                        
                        # Ensure line numbers are integers, use 0 if None
                        start_line = int(start_line) if start_line is not None else 0
                        end_line = int(end_line) if end_line is not None else 0
                        
                        # Generate unique finding_id for each finding
                        finding_id = f"{job.job_id}_{idx}" if len(parsed_output) > 1 else job.job_id
                        
                        findings.append(SecurityFinding(
                            finding_id=finding_id,
                            source="llm",
                            severity=item.get("severity", "medium"),
                            confidence=item.get("confidence", 1.0),
                            title=item.get("category", "Unnamed alert"),
                            description=item.get("description", ""),
                            file_path=job.absolute_path,
                            start_line=start_line,
                            end_line=end_line,
                            remediation=item.get("remediation"),
                            evidence=item.get("exploit_scenario", {}),
                            tags=item.get("tags", []),
                            rule_id=finding_id,
                            metadata={"messages": messages},
                        ))
                
                # Handle single object case
                elif isinstance(parsed_output, dict):
                    if 'severity' not in parsed_output:
                        logger.debug(f"Output missing required fields: {file_path}")
                        return []
                    
                    # Build SecurityFinding object
                    start_line = parsed_output.get("start_line")
                    end_line = parsed_output.get("end_line")
                    
                    # Ensure line numbers are integers, use 0 if None
                    start_line = int(start_line) if start_line is not None else 0
                    end_line = int(end_line) if end_line is not None else 0
                    
                    findings.append(SecurityFinding(
                        finding_id=job.job_id,
                        source="llm",
                        severity=parsed_output.get("severity", "medium"),
                        confidence=parsed_output.get("confidence", 1.0),
                        title=parsed_output.get("category", "Unnamed alert"),
                        description=parsed_output.get("description", ""),
                        file_path=job.absolute_path,
                        start_line=start_line,
                        end_line=end_line,
                        remediation=parsed_output.get("remediation"),
                        evidence=parsed_output.get("exploit_scenario", {}),
                        tags=parsed_output.get("tags", []),
                        rule_id=job.job_id,
                        metadata={"messages": messages},
                    ))
                else:
                    logger.debug(f"Output format incorrect, expected dict or list, got {type(parsed_output)}: {file_path}")
                    return []
                
                return findings
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed {file_path}: {e}\nOutput content: {output[:200]}")
                return []
                
        except Exception as e:
            logger.error(f"Review task execution failed {job.absolute_path}: {e}", exc_info=True)
            return []

    def _get_prompt_items(self) -> dict[str, str]:
        """
        Get prompt items.

        Returns:
            Prompt dictionary, keys are prompt names, values are prompt contents
        """
        prompt_items = {}
        
        if not self.prompt_path.exists():
            logger.error(f"Prompt path does not exist: {self.prompt_path}")
            return prompt_items
        
        try:
            for file in self.prompt_path.iterdir():
                if file.is_file() and file.suffix == ".md":
                    file_name = file.stem
                    prompt_items[file_name] = file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read prompt file: {e}")
        
        return prompt_items

    def scan(self, context: ScanContext) -> Iterable[SecurityFinding]:
        """
        Generate potential risks for scan context.

        Read file list to scan from process_file in ScanContext.metadata.

        Args:
            context: Scan context

        Returns:
            Iterable of SecurityFinding objects
        """
        # Get file list from metadata
        process_files = context.metadata.get("process_file")
        if not process_files:
            logger.warning("process_file not found in metadata, returning empty result")
            return []
        
        # Determine root path (for resolving relative paths)
        root_path = context.root_path.resolve()
        output_path = context.output_path.resolve() if context.output_path else root_path
        
        # Get prompts
        prompt_items = self._get_prompt_items()
        if not prompt_items:
            logger.error("No prompts loaded, returning empty result")
            return []
        
        # Build task list
        jobs: list[_ReviewJob] = []
        for file_rel_path in process_files:
            # Try to resolve file from output_path (processed files)
            file_path = output_path / file_rel_path
            
            # If not in output_path, try to resolve from root_path
            if not file_path.exists():
                file_path = root_path / file_rel_path
            
            # If still doesn't exist, skip
            if not file_path.exists():
                logger.warning(f"File does not exist, skipping: {file_rel_path}")
                continue
            
            # Create task
            job = _ReviewJob(
                job_id=str(uuid.uuid4()),
                prompts=prompt_items,
                absolute_path=str(file_path.resolve()),
                output="",
            )
            jobs.append(job)
        
        if not jobs:
            logger.info("No files to scan")
            return []
        
        logger.info(f"Starting scan of {len(jobs)} files")
        
        # Execute scan tasks in parallel
        secfindings: list[SecurityFinding] = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self._execute_review_job, job)
                for job in jobs
            ]

            for future in futures:
                try:
                    results = future.result()
                    if results:
                        secfindings.extend(results)
                except Exception as e:
                    logger.error(f"Scan task execution failed: {e}", exc_info=True)
        
        # Filter invalid findings
        valid_findings = filter_invalid_findings(secfindings)
        
        logger.info(f"Scan completed, found {len(valid_findings)} valid vulnerabilities (total {len(secfindings)})")
        
        # Save results to file
        try:
            output_file = output_path / "llm_scan.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"secfindings": [asdict(finding) for finding in valid_findings]},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            logger.warning(f"Failed to save scan results: {e}")
        
        return valid_findings

    def warmup(self) -> None:
        """Optional: Preload prompts, trigger model health check."""
        pass

if __name__ == "__main__":
    from scanner.input_resolver import resolve_scan_context
    scanner = OpenAILLMScanner()
    context = resolve_scan_context(
        "/Users/lijinqi13/Code/agent-safety/evals/ghsa/repos/evernote-mcp-server-GHSA-h2v8-4c3f-vqgv.json-39ca9f6"#"
    )
    secfindings = scanner.scan(context)
    # after-effects-mcp-main
    import scanner.output_resolver as output_resolver
    output_resolver.simple_output(secfindings)
