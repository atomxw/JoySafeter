# Tool Failure Recovery System

## Overview

- Purpose: Analyze tool failures and provide intelligent recovery strategies with alternative tool suggestions
- Category: incident_response
- Severity: high
- Tags: failure-recovery, tool-alternatives, error-analysis, fallback, resilience

## Context and Use-Cases

- Automatically detect failure types from error output and exit codes
- Suggest recovery strategies tailored to specific failure types
- Recommend alternative tools when primary tool fails
- Enable resilient security testing workflows

## Failure Type Detection

### Failure Patterns

The system identifies failures through pattern matching:

- **Timeout**: "timeout", "timed out", "connection timeout"
- **Permission Denied**: "permission denied", "access denied", "forbidden"
- **Not Found**: "not found", "command not found", "no such file"
- **Network Error**: "network unreachable", "connection refused", "host unreachable"
- **Rate Limited**: "rate limit", "too many requests", "throttled"
- **Authentication Required**: "authentication required", "unauthorized", "login required"

### Exit Code Analysis

- Exit code 1: Generic error (+0.1 confidence)
- Exit code 124: Timeout (+0.5 confidence, sets failure_type to "timeout")
- Exit code 126: Permission denied (+0.5 confidence, sets failure_type to "permission_denied")

## Tool Alternatives Mapping

The system provides fallback tools for common security tools:

- **nmap**: rustscan, masscan, zmap
- **gobuster**: dirsearch, feroxbuster, dirb
- **sqlmap**: sqlninja, bbqsql, jsql-injection
- **nuclei**: nikto, w3af, skipfish
- **hydra**: medusa, ncrack, patator
- **hashcat**: john, ophcrack, rainbowcrack
- **amass**: subfinder, sublist3r, assetfinder
- **ffuf**: wfuzz, gobuster, dirb

## Recovery Strategies

### Timeout Failures

Recovery actions:
- Increase timeout values
- Reduce thread count
- Use alternative faster tool
- Split target into smaller chunks

Parameter adjustments:
- Double timeout values
- Reduce threads by 50%

### Permission Denied Failures

Recovery actions:
- Run with elevated privileges
- Check file permissions
- Use alternative tool with different approach

### Rate Limited Failures

Recovery actions:
- Implement delays between requests
- Reduce thread count
- Use stealth timing profile
- Rotate IP addresses if possible

Parameter adjustments:
- Apply stealth timing profile (delay: 2.0s, threads: 5, timeout: 30s)

### Network Error Failures

Recovery actions:
- Check network connectivity
- Try alternative network routes
- Use proxy or VPN
- Verify target is accessible

## Examples

### Failure Analysis Output

```python
{
    "failure_type": "timeout",
    "confidence": 0.8,
    "recovery_strategies": [
        "Increase timeout values",
        "Reduce thread count",
        "Use alternative faster tool",
        "Split target into smaller chunks"
    ],
    "alternative_tools": ["rustscan", "masscan", "zmap"]
}
```

### Recovery Plan Output

```python
{
    "original_tool": "nmap",
    "failure_analysis": {
        "failure_type": "timeout",
        "confidence": 0.8,
        "recovery_strategies": [...],
        "alternative_tools": ["rustscan", "masscan", "zmap"]
    },
    "recovery_actions": [
        "Increased timeout and reduced threads"
    ],
    "alternative_tools": ["rustscan", "masscan", "zmap"],
    "adjusted_parameters": {
        "timeout": 20,
        "threads": 10
    }
}
```

## Related Items

- rate_limit_detection_system
- parameter_optimization_advanced
- technology_detection_system
