# Parameter Auto-Adjustment

## Overview

- Purpose: Automatically adjust tool parameters based on error types and system resources
- Category: incident_response
- Severity: high
- Tags: parameter-optimization, auto-adjustment, incident-response

## Context and Use-Cases

- Handling timeout errors by reducing concurrency
- Managing rate limiting with delays
- Preventing resource exhaustion
- Adaptive tool tuning based on error patterns

## Procedure / Knowledge detail

### Tool-Specific Parameter Adjustments

#### Nmap Parameter Adjustments

**For TIMEOUT errors:**
```
timing: -T2 (reduced from -T4)
reduce_ports: true
```

**For RATE_LIMITED errors:**
```
timing: -T1 (slowest)
delay: 1000ms
```

**For RESOURCE_EXHAUSTED errors:**
```
max_parallelism: 10
```

#### Gobuster Parameter Adjustments

**For TIMEOUT errors:**
```
threads: 10 (reduced)
timeout: 30s
```

**For RATE_LIMITED errors:**
```
threads: 5
delay: 1s
```

**For RESOURCE_EXHAUSTED errors:**
```
threads: 5
```

#### Nuclei Parameter Adjustments

**For TIMEOUT errors:**
```
concurrency: 10
timeout: 30
```

**For RATE_LIMITED errors:**
```
rate-limit: 10
concurrency: 5
```

**For RESOURCE_EXHAUSTED errors:**
```
concurrency: 5
```

#### Feroxbuster Parameter Adjustments

**For TIMEOUT errors:**
```
threads: 10
timeout: 30
```

**For RATE_LIMITED errors:**
```
threads: 5
rate-limit: 10
```

**For RESOURCE_EXHAUSTED errors:**
```
threads: 5
```

#### FFuf Parameter Adjustments

**For TIMEOUT errors:**
```
threads: 10
timeout: 30
```

**For RATE_LIMITED errors:**
```
threads: 5
rate: 10
```

**For RESOURCE_EXHAUSTED errors:**
```
threads: 5
```

### Generic Parameter Adjustments

When tool-specific adjustments are not available:

**For TIMEOUT errors:**
```
timeout: 60
threads: 5
```

**For RATE_LIMITED errors:**
```
delay: 2s
threads: 3
```

**For RESOURCE_EXHAUSTED errors:**
```
threads: 3
memory_limit: 1G
```

### Adjustment Algorithm

1. **Look up tool-specific adjustments** for the error type
2. **If found**, use tool-specific parameters
3. **If not found**, use generic adjustments based on error type
4. **Merge adjustments** with original parameters
5. **Return adjusted parameters**

## Examples

### Auto-Adjustment Example

```python
from error_handler_error_handler import IntelligentErrorHandler, ErrorType

handler = IntelligentErrorHandler()

# Original parameters
original_params = {
    "ports": "1-65535",
    "timing": "-T4",
    "threads": "50"
}

# Auto-adjust for timeout error
adjusted_params = handler.auto_adjust_parameters(
    tool="nmap",
    error_type=ErrorType.TIMEOUT,
    original_params=original_params
)

# Result: {
#   "ports": "1-65535",
#   "timing": "-T2",
#   "threads": "50",
#   "reduce_ports": True
# }
```

### Gobuster Rate Limiting Adjustment

```python
original_params = {
    "wordlist": "/usr/share/wordlists/dirb/common.txt",
    "threads": "50",
    "timeout": "10s"
}

adjusted_params = handler.auto_adjust_parameters(
    tool="gobuster",
    error_type=ErrorType.RATE_LIMITED,
    original_params=original_params
)

# Result: {
#   "wordlist": "/usr/share/wordlists/dirb/common.txt",
#   "threads": "5",
#   "timeout": "10s",
#   "delay": "1s"
# }
```

### Nuclei Resource Exhaustion Adjustment

```python
original_params = {
    "templates": "/path/to/templates",
    "concurrency": "50"
}

adjusted_params = handler.auto_adjust_parameters(
    tool="nuclei",
    error_type=ErrorType.RESOURCE_EXHAUSTED,
    original_params=original_params
)

# Result: {
#   "templates": "/path/to/templates",
#   "concurrency": "5"
# }
```

## Parameter Tuning Strategies

### Concurrency Reduction

- Start with high concurrency (50+)
- On timeout: reduce to 10-20
- On rate limit: reduce to 5-10
- On resource exhaustion: reduce to 3-5

### Timeout Adjustment

- Default: 10-30 seconds
- On timeout: increase to 60+ seconds
- On rate limit: keep default or increase slightly

### Timing/Delay Adjustment

- Default: no delay or minimal (100ms)
- On rate limit: add 1-2 second delays
- On resource exhaustion: add 500ms-1s delays

## Related Knowledge Items

- **error_classification_patterns** - Error type detection
- **timeout_error_recovery** - Timeout handling
- **system_resource_monitoring** - Resource tracking
