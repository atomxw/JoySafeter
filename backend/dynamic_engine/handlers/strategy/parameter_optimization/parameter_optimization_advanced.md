# Advanced Parameter Optimization

## Overview

- Purpose: Comprehensive parameter optimization system combining technology detection, resource monitoring, profile-based optimization, and failure recovery
- Category: tooling
- Severity: high
- Tags: parameter-optimization, advanced, intelligence, context-aware, tool-optimization, nmap, gobuster, sqlmap, nuclei

## Context and Use-Cases

- Optimize security tool parameters based on complete target context
- Combine multiple optimization strategies for maximum effectiveness
- Adapt parameters in real-time based on system resources and target responses
- Support multiple optimization profiles (stealth, normal, aggressive)
- Recover from tool failures with intelligent parameter adjustments

## Optimization Pipeline

The advanced optimization system follows a multi-stage pipeline:

1. **Get Base Parameters**: Retrieve tool-specific default parameters
2. **Detect Technologies**: Identify target technologies from headers, content, and ports
3. **Apply Technology Optimizations**: Customize parameters based on detected technologies
4. **Monitor System Resources**: Check current CPU, memory, disk, and network usage
5. **Optimize Based on Resources**: Adjust parameters if resources exceed thresholds
6. **Apply Profile Optimizations**: Apply stealth/normal/aggressive profile settings
7. **Add Metadata**: Include optimization metadata for tracking and debugging

## Optimization Profiles

### Stealth Profile

Used when WAF detected or stealth mode required:
- Minimal threads (5)
- Large delays (2.0s)
- Long timeouts (30s)
- Request randomization enabled

### Normal Profile

Default balanced approach:
- Moderate threads (20)
- Small delays (0.5s)
- Standard timeouts (10s)

### Aggressive Profile

Maximum performance when no restrictions detected:
- High threads (50)
- No delays (0s)
- Short timeouts (5s)

## Tool-Specific Base Parameters

### Nmap

```python
{
    "scan_type": "-sS",
    "ports": "1-1000",
    "timing": "-T4"
}
```

### Gobuster

```python
{
    "mode": "dir",
    "threads": 20,
    "wordlist": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
}
```

### SQLMap

```python
{
    "batch": True,
    "level": 1,
    "risk": 1
}
```

### Nuclei

```python
{
    "severity": "critical,high,medium",
    "threads": 25
}
```

## Optimization Metadata

Each optimization includes metadata for tracking:

```python
{
    "detected_technologies": {
        "web_servers": ["nginx"],
        "frameworks": ["express"],
        "cms": [],
        "databases": ["mysql"],
        "languages": ["nodejs"],
        "security": ["cloudflare"],
        "services": ["http", "https", "mysql"]
    },
    "resource_usage": {
        "cpu_percent": 45.2,
        "memory_percent": 62.1,
        "disk_percent": 55.0,
        "network_bytes_sent": 1000000,
        "network_bytes_recv": 2000000,
        "timestamp": 1704067200.0
    },
    "optimization_profile": "normal",
    "optimizations_applied": [
        "Applied technology-specific extensions for PHP",
        "Reduced threads due to high CPU usage"
    ],
    "timestamp": "2025-01-01T12:00:00Z"
}
```

## Failure Handling

When tool execution fails, the system:

1. **Analyzes failure**: Identify failure type from error output and exit code
2. **Calculates confidence**: Determine confidence in failure classification
3. **Suggests recovery**: Provide recovery strategies specific to failure type
4. **Adjusts parameters**: Modify parameters for retry attempt
5. **Suggests alternatives**: Recommend alternative tools if primary fails

## Examples

### Complete Optimization Flow

Input target: WordPress on Nginx with Cloudflare WAF

Step 1 - Base parameters for Gobuster:
```python
{
    "mode": "dir",
    "threads": 20,
    "wordlist": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
}
```

Step 2 - Detect technologies: nginx, WordPress, PHP, MySQL, Cloudflare

Step 3 - Apply technology optimizations:
```python
{
    "extensions": "php,html,txt,xml",
    "additional_paths": "/wp-content/,/wp-admin/,/wp-includes/",
    "threads": 20
}
```

Step 4 - Monitor resources: CPU 45%, Memory 62%, Disk 55%

Step 5 - No resource adjustments needed

Step 6 - Apply stealth profile (due to Cloudflare WAF):
```python
{
    "threads": 5,
    "delay": "2s",
    "timeout": "30s",
    "_stealth_mode": True
}
```

Final optimized parameters:
```python
{
    "mode": "dir",
    "wordlist": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "extensions": "php,html,txt,xml",
    "additional_paths": "/wp-content/,/wp-admin/,/wp-includes/",
    "threads": 5,
    "delay": "2s",
    "timeout": "30s",
    "_stealth_mode": True,
    "_optimization_metadata": {
        "detected_technologies": {...},
        "resource_usage": {...},
        "optimization_profile": "stealth",
        "optimizations_applied": [
            "Applied WordPress-specific extensions and paths",
            "Applied stealth profile due to Cloudflare WAF detection"
        ],
        "timestamp": "2025-01-01T12:00:00Z"
    }
}
```

## Related Items

- technology_detection_system
- rate_limit_detection_system
- tool_failure_recovery_system
- performance_monitoring_system
- technology_specific_optimizations
