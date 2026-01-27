# Rate Limit Detection System

## Overview

- Purpose: Detect rate limiting from HTTP responses and automatically adjust tool timing parameters
- Category: tooling
- Severity: high
- Tags: rate-limiting, timing-adjustment, detection, evasion, throttling, http-429

## Context and Use-Cases

- Automatically detect when targets implement rate limiting
- Recommend appropriate timing profiles based on detection confidence
- Adjust tool parameters (threads, delays, timeouts) to avoid detection
- Support four timing profiles for different scenarios

## Detection Indicators

### Rate Limit Detection Patterns

The system detects rate limiting through multiple indicators:

- HTTP 429 (Too Many Requests) status code
- Response text patterns: "rate limit", "too many requests", "throttle", "slow down", "retry after", "quota exceeded", "api limit", "request limit"
- HTTP headers: X-RateLimit-*, Retry-After, X-Rate-Limit-*

### Confidence Scoring

- HTTP 429 status: +0.8 confidence
- Text pattern match: +0.2 confidence per match
- Rate limit header: +0.3 confidence per header

Maximum confidence: 1.0

## Timing Profiles

### Aggressive Profile
```
delay: 0.1 seconds
threads: 50
timeout: 5 seconds
```
Use when no rate limiting detected (confidence < 0.2)

### Normal Profile
```
delay: 0.5 seconds
threads: 20
timeout: 10 seconds
```
Use when minimal rate limiting detected (confidence 0.2-0.5)

### Conservative Profile
```
delay: 1.0 seconds
threads: 10
timeout: 15 seconds
```
Use when moderate rate limiting detected (confidence 0.5-0.8)

### Stealth Profile
```
delay: 2.0 seconds
threads: 5
timeout: 30 seconds
```
Use when strong rate limiting detected (confidence >= 0.8)

## Parameter Adjustment Process

1. **Detect rate limiting** from response status, text, and headers
2. **Calculate confidence score** based on indicators found
3. **Recommend timing profile** based on confidence threshold
4. **Adjust parameters**:
   - Update threads, delay, timeout values
   - Modify additional_args for tool-specific timing flags
   - Remove conflicting timing arguments before adding new ones

## Examples

### Detection Output
```python
{
    "detected": True,
    "confidence": 0.9,
    "indicators": [
        "HTTP 429 status",
        "Text: 'rate limit'",
        "Header: X-RateLimit-Remaining"
    ],
    "recommended_profile": "stealth"
}
```

### Parameter Adjustment Example

Original parameters:
```python
{
    "threads": 50,
    "delay": 0.1,
    "timeout": 5,
    "additional_args": "-t 50"
}
```

After stealth profile adjustment:
```python
{
    "threads": 5,
    "delay": 2.0,
    "timeout": 30,
    "additional_args": "-t 5 --delay 2.0"
}
```

## Related Items

- technology_detection_system
- parameter_optimization_advanced
- tool_failure_recovery_system
