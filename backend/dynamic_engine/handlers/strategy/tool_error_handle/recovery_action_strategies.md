# Recovery Action Strategies

## Overview

- Purpose: Define seven distinct recovery actions that can be automatically triggered based on error classification and context.
- Category: incident_response
- Severity: high
- Tags: recovery-actions, incident-response, automation, error-handling

## Context and Use-Cases

- Automated tool orchestration systems that need deterministic recovery paths for different failure modes.
- Incident response playbooks that require escalation and fallback decision trees.
- Self-healing infrastructure that attempts multiple remediation strategies before human intervention.

## Procedure / Knowledge detail

Seven distinct recovery strategies are defined:

1. **RETRY_WITH_BACKOFF** - Retry the operation with exponential backoff delays (suitable for transient failures like timeouts).
2. **RETRY_WITH_REDUCED_SCOPE** - Retry with narrower parameters or smaller target set (e.g., fewer ports, fewer directories).
3. **SWITCH_TO_ALTERNATIVE_TOOL** - Replace the failed tool with a pre-mapped alternative from the fallback chain.
4. **ADJUST_PARAMETERS** - Modify tool parameters (e.g., reduce timeout, increase verbosity, disable certain checks).
5. **ESCALATE_TO_HUMAN** - Route the error to human analysts with full context and recommendations.
6. **GRACEFUL_DEGRADATION** - Continue operation with partial results and fill gaps with basic checks.
7. **ABORT_OPERATION** - Terminate the operation and mark as failed (used for unrecoverable errors).

## Examples

- Action Selection:

  ```python
  action = RecoveryAction.RETRY_WITH_BACKOFF  # "retry_with_backoff"
  action = RecoveryAction.SWITCH_TO_ALTERNATIVE_TOOL  # "switch_to_alternative_tool"
  action = RecoveryAction.GRACEFUL_DEGRADATION  # "graceful_degradation"
  ```

- Recovery Decision Tree:

  ```text
  ErrorType.TIMEOUT -> RecoveryAction.RETRY_WITH_BACKOFF or RETRY_WITH_REDUCED_SCOPE
  ErrorType.RATE_LIMITED -> RecoveryAction.RETRY_WITH_BACKOFF (with longer delays)
  ErrorType.TOOL_NOT_FOUND -> RecoveryAction.SWITCH_TO_ALTERNATIVE_TOOL
  ErrorType.INVALID_PARAMETERS -> RecoveryAction.ADJUST_PARAMETERS
  ErrorType.RESOURCE_EXHAUSTED -> RecoveryAction.GRACEFUL_DEGRADATION or ABORT_OPERATION
  ErrorType.PERMISSION_DENIED -> RecoveryAction.ESCALATE_TO_HUMAN
  ```
