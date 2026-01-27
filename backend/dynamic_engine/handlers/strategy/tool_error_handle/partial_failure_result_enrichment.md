# Partial Failure Result Enrichment

## Overview

- Purpose: Preserve usable intelligence by augmenting partial scan data with fallback checks and manual guidance when graceful degradation triggers.
- Category: incident_response
- Severity: medium
- Tags: graceful-degradation, partial-results, incident-response, automation

## Context and Use-Cases

- Automated execution pipelines that still return data even when a subset of tools crashes or times out.
- Incident handlers who need traceability on what failed, which compensating checks ran, and what to verify manually next.
- Situations where degraded outputs should still include actionable remediation hints.

## Procedure / Knowledge detail

1. Copy the original partial results and append a `degradation_info` block containing:
   - operation: The type of operation that failed
   - failed_components: List of tools that failed
   - partial_success: Boolean indicating partial completion
   - fallback_applied: Boolean indicating fallback was used
   - timestamp: ISO8601 timestamp of when degradation occurred

2. Auto-fill missing fields per operation type:
   - For network_discovery: Call basic port check if "open_ports" is absent
   - For web_discovery: Call basic directory check if "directories" is missing
   - For vulnerability_scanning: Call basic security check if "vulnerabilities" is missing

3. Populate `manual_recommendations` based on the failed components to guide analysts toward manual verification steps.

## Examples

- Command:

  ```python
  enriched = degradation_manager.handle_partial_failure(
      operation="network_discovery",
      partial_results={"target": "scan.example.org"},
      failed_components=["nmap"]
  )
  ```

- Log Query/Rule:

  ```text
  "degradation_info" AND "partial_success": true AND "manual_recommendations"
  ```
