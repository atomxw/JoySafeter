# Error Classification Patterns

## Overview
- Purpose: Classify errors into predefined types using pattern matching and exception type analysis
- Category: incident_response
- Severity: high
- Tags: error-handling, pattern-matching, classification, incident-response

## Context and Use-Cases
- Automated error diagnosis in security tool execution
- Intelligent recovery strategy selection
- Error history tracking and statistics
- Incident response automation

## Procedure / Knowledge detail

### Error Types (11 types)
The system classifies errors into the following types:

1. **TIMEOUT** - Connection or operation timeouts
2. **PERMISSION_DENIED** - Access control failures
3. **NETWORK_UNREACHABLE** - Network connectivity issues
4. **RATE_LIMITED** - API/service rate limiting
5. **TOOL_NOT_FOUND** - Missing executables or tools
6. **INVALID_PARAMETERS** - Bad command arguments
7. **RESOURCE_EXHAUSTED** - Memory, disk, or file descriptor limits
8. **AUTHENTICATION_FAILED** - Login or credential failures
9. **TARGET_UNREACHABLE** - Target host unavailable
10. **PARSING_ERROR** - Output format parsing failures
11. **UNKNOWN** - Unclassified errors

### Pattern Matching Rules

The classification uses regex patterns with case-insensitive matching:

**Timeout Patterns:**
```
timeout|timed out|connection timeout|read timeout
operation timed out|command timeout
```

**Permission Patterns:**
```
permission denied|access denied|forbidden|not authorized
sudo required|root required|insufficient privileges
```

**Network Patterns:**
```
network unreachable|host unreachable|no route to host
connection refused|connection reset|network error
```

**Rate Limiting Patterns:**
```
rate limit|too many requests|throttled|429
request limit exceeded|quota exceeded
```

**Tool Not Found Patterns:**
```
command not found|no such file or directory|not found
executable not found|binary not found
```

**Parameter Patterns:**
```
invalid argument|invalid option|unknown option
bad parameter|invalid parameter|syntax error
```

**Resource Exhausted Patterns:**
```
out of memory|memory error|disk full|no space left
resource temporarily unavailable|too many open files
```

**Authentication Patterns:**
```
authentication failed|login failed|invalid credentials
unauthorized|invalid token|expired token
```

**Target Unreachable Patterns:**
```
target unreachable|target not responding|target down
host not found|dns resolution failed
```

**Parsing Error Patterns:**
```
parse error|parsing failed|invalid format|malformed
json decode error|xml parse error|invalid json
```

### Classification Algorithm

1. **Exception Type Check (Primary)**
   - Check if exception is `TimeoutError` → TIMEOUT
   - Check if exception is `PermissionError` → PERMISSION_DENIED
   - Check if exception is `ConnectionError` → NETWORK_UNREACHABLE
   - Check if exception is `FileNotFoundError` → TOOL_NOT_FOUND

2. **Pattern Matching (Secondary)**
   - Convert error message to lowercase
   - Iterate through error patterns
   - Return first matching error type
   - Return UNKNOWN if no match

## Examples

### Classification Example
```python
from error_handler_error_handler import IntelligentErrorHandler

handler = IntelligentErrorHandler()

# Pattern-based classification
error_type = handler.classify_error("Connection timeout after 30 seconds")
# Returns: ErrorType.TIMEOUT

# Exception-based classification
try:
    open("/nonexistent/file")
except FileNotFoundError as e:
    error_type = handler.classify_error(str(e), e)
    # Returns: ErrorType.TOOL_NOT_FOUND

# Rate limiting classification
error_type = handler.classify_error("429 Too Many Requests")
# Returns: ErrorType.RATE_LIMITED
```

### Error Context Creation
```python
error_context = ErrorContext(
    tool_name="nmap",
    target="192.168.1.1",
    parameters={"ports": "1-65535"},
    error_type=ErrorType.TIMEOUT,
    error_message="Connection timeout after 30 seconds",
    attempt_count=1,
    timestamp=datetime.now(),
    stack_trace=traceback.format_exc(),
    system_resources=handler._get_system_resources()
)
```

## Related Knowledge Items
- **timeout_error_recovery** - Recovery strategies for timeout errors
- **tool_alternatives_fallback** - Alternative tool selection
- **error_escalation_to_human** - Human escalation procedures
