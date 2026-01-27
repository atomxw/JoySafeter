# Timeout Error Recovery

## Overview

- Purpose: Implement exponential backoff and scope reduction strategies for timeout errors
- Category: incident_response
- Severity: high
- Tags: timeout, recovery, backoff, exponential-backoff

## Context and Use-Cases

- Handling timeouts in network scanning tools (nmap, masscan)
- Recovering from slow target responses
- Preventing cascading failures in tool chains
- Automatic retry with adaptive parameters

## Procedure / Knowledge detail

### Recovery Strategies for Timeout Errors

The system implements three primary recovery strategies:

#### Strategy 1: Retry with Exponential Backoff

```
Action: RETRY_WITH_BACKOFF
Initial Delay: 5 seconds
Max Delay: 60 seconds
Backoff Multiplier: 2.0
Max Attempts: 3
Success Probability: 0.7
Estimated Time: 30 seconds
```

**Algorithm:**
1. Wait for initial_delay seconds
2. Retry operation
3. If timeout occurs again, multiply delay by backoff_multiplier
4. Repeat until max_delay or max_attempts reached

**Example timing sequence:**
- Attempt 1: Wait 5s → Timeout
- Attempt 2: Wait 10s → Timeout
- Attempt 3: Wait 20s → Success (or final timeout)

#### Strategy 2: Retry with Reduced Scope

```
Action: RETRY_WITH_REDUCED_SCOPE
Parameters:
  - reduce_threads: true
  - reduce_timeout: true
Max Attempts: 2
Success Probability: 0.8
Estimated Time: 45 seconds
```

**Scope reduction techniques:**
- Reduce thread count (e.g., 50 → 10)
- Increase individual operation timeout
- Reduce port range for scanning
- Limit concurrent connections

#### Strategy 3: Switch to Alternative Tool

```
Action: SWITCH_TO_ALTERNATIVE_TOOL
Parameters:
  - prefer_faster_tools: true
Max Attempts: 1
Success Probability: 0.6
Estimated Time: 60 seconds
```

**Tool alternatives for timeout scenarios:**
- nmap → rustscan (faster scanning)
- gobuster → feroxbuster (concurrent requests)
- nuclei → jaeles (parallel execution)

### Implementation Details

**Backoff calculation:**
```python
delay = min(initial_delay * (backoff_multiplier ** (attempt - 1)), max_delay)
```

**Success probability adjustment:**
```python
adjusted_probability = success_probability * (0.9 ** (attempt_count - 1))
```

## Examples

### Timeout Recovery Example

```python
from error_handler_error_handler import IntelligentErrorHandler, ErrorType, ErrorContext
from datetime import datetime

handler = IntelligentErrorHandler()

# Simulate timeout error
error_context = ErrorContext(
    tool_name="nmap",
    target="192.168.1.1",
    parameters={"ports": "1-65535", "threads": "50"},
    error_type=ErrorType.TIMEOUT,
    error_message="Connection timeout after 30 seconds",
    attempt_count=1,
    timestamp=datetime.now(),
    stack_trace="...",
    system_resources=handler._get_system_resources()
)

# Get recovery strategy
strategies = handler.recovery_strategies[ErrorType.TIMEOUT]
best_strategy = handler._select_best_strategy(strategies, error_context)

# Apply strategy
if best_strategy.action.value == "retry_with_backoff":
    initial_delay = best_strategy.parameters["initial_delay"]
    max_delay = best_strategy.parameters["max_delay"]
    print(f"Retrying with backoff: {initial_delay}s initial, {max_delay}s max")

elif best_strategy.action.value == "retry_with_reduced_scope":
    print("Retrying with reduced scope (fewer threads, longer timeout)")

elif best_strategy.action.value == "switch_to_alternative_tool":
    alt_tool = handler.get_alternative_tool("nmap", {})
    print(f"Switching to alternative tool: {alt_tool}")
```

### Parameter Adjustment for Timeout

```python
# Auto-adjust nmap parameters for timeout
adjusted_params = handler.auto_adjust_parameters(
    tool="nmap",
    error_type=ErrorType.TIMEOUT,
    original_params={"ports": "1-65535", "timing": "-T4"}
)

# Result: {"ports": "1-65535", "timing": "-T2", "reduce_ports": True}
```

## Related Knowledge Items

- **error_classification_patterns** - Error type detection
- **parameter_auto_adjustment** - Parameter optimization
- **tool_alternatives_fallback** - Alternative tool selection
