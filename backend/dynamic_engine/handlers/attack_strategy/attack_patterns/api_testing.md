# API Testing

## Overview

- **Purpose**: Comprehensive API security testing and parameter discovery
- **Category**: attack-pattern
- **Severity**: high
- **Target Types**: API Endpoints, Web Applications
- **Execution Time**: 20 minutes
- **Aggressiveness**: Medium

## Context and Use-Cases

- **API reconnaissance**: Discover API endpoints and parameters
- **Parameter discovery**: Identify hidden or undocumented parameters
- **API vulnerability testing**: Test for common API vulnerabilities
- **Authentication bypass**: Identify authentication weaknesses
- **Data exposure**: Discover sensitive data exposure in APIs

## Procedure / Knowledge Detail

### Tool Sequence (6 tools)

#### 1. httpx - Endpoint Probing (Priority 1)
- **Purpose**: Probe API endpoints and detect technologies
- **Parameters**: probe: True, tech_detect: True
- **Output**: Live endpoints, HTTP status codes, technology detection
- **Time**: 5 minutes

#### 2. arjun - Parameter Discovery (Priority 2)
- **Purpose**: Discover hidden parameters
- **Parameters**: method: "GET,POST", stable: True
- **Output**: Discovered parameters, parameter types
- **Time**: 5 minutes

#### 3. x8 - Parameter Fuzzing (Priority 3)
- **Purpose**: Fuzz parameters with wordlist
- **Parameters**: method: "GET", wordlist: "/usr/share/wordlists/x8/params.txt"
- **Output**: Additional parameters, fuzzing results
- **Time**: 5 minutes

#### 4. paramspider - Parameter Collection (Priority 4)
- **Purpose**: Collect parameters from various sources
- **Parameters**: level: 2
- **Output**: Collected parameters, parameter sources
- **Time**: 5 minutes

#### 5. nuclei - API Vulnerability Scanning (Priority 5)
- **Purpose**: Scan for API-specific vulnerabilities
- **Parameters**: tags: "api,graphql,jwt", severity: "high,critical"
- **Output**: Vulnerability findings, API issues
- **Time**: 5 minutes

#### 6. ffuf - Parameter Fuzzing (Priority 6)
- **Purpose**: Fuzz POST parameters
- **Parameters**: mode: "parameter", method: "POST"
- **Output**: Additional parameters, fuzzing results
- **Time**: 5 minutes

## Workflow

### Phase 1: Endpoint Probing (5 min)
```
httpx → Probe API endpoints
```

### Phase 2: Parameter Discovery (15 min)
```
arjun → Discover parameters
x8 → Fuzz parameters
paramspider → Collect parameters
ffuf → Fuzz POST parameters
```

### Phase 3: Vulnerability Scanning (5 min)
```
nuclei → Scan for API vulnerabilities
```

## Implementation Example

```python
# API Testing Pattern
pattern = {
    "api_testing": [
        {"tool": "httpx", "priority": 1, "params": {"probe": True, "tech_detect": True}},
        {"tool": "arjun", "priority": 2, "params": {"method": "GET,POST", "stable": True}},
        {"tool": "x8", "priority": 3, "params": {"method": "GET", "wordlist": "/usr/share/wordlists/x8/params.txt"}},
        {"tool": "paramspider", "priority": 4, "params": {"level": 2}},
        {"tool": "nuclei", "priority": 5, "params": {"tags": "api,graphql,jwt", "severity": "high,critical"}},
        {"tool": "ffuf", "priority": 6, "params": {"mode": "parameter", "method": "POST"}}
    ]
}

# Execute pattern
for tool_config in pattern["api_testing"]:
    tool_name = tool_config["tool"]
    params = tool_config["params"]
    result = execute_tool(tool_name, params)
    process_results(result)
```

## Expected Outputs

### Parameter Discovery
- GET parameters
- POST parameters
- Header parameters
- Cookie parameters
- Path parameters

### Vulnerability Findings
- Authentication bypass
- Authorization issues
- Data exposure
- Injection vulnerabilities
- API misconfigurations

### API Information
- API endpoints
- API versions
- API documentation
- API authentication methods

## Related Knowledge Items

- **web_reconnaissance**: For web application reconnaissance
- **vulnerability_assessment**: For deeper vulnerability scanning
- **bug_bounty_vulnerability_hunting**: For comprehensive vulnerability hunting
- **tool_effectiveness_scoring_system**: Tool effectiveness ratings

## Best Practices

1. **Start with httpx**: Probe endpoints first to understand API structure
2. **Use multiple parameter discovery tools**: Combine different tools for comprehensive coverage
3. **Test different HTTP methods**: Try GET, POST, PUT, DELETE, PATCH
4. **Check authentication**: Test with and without authentication
5. **Verify parameters**: Confirm discovered parameters are valid
6. **Document findings**: Record all discovered parameters and endpoints
7. **Test for injection**: Try SQL injection, command injection, etc.
8. **Check response codes**: Analyze HTTP response codes for clues

## Mitigation & Best Practices

### For Defense

1. **Input Validation**: Validate all input parameters
2. **Rate Limiting**: Implement rate limiting on API endpoints
3. **Authentication**: Require strong authentication for all endpoints
4. **Authorization**: Implement proper authorization checks
5. **Logging**: Log all API access attempts
6. **Monitoring**: Alert on suspicious API activity
7. **Documentation**: Keep API documentation up to date
8. **Versioning**: Use API versioning to manage changes
9. **Error Handling**: Don't expose sensitive information in error messages
10. **CORS**: Configure CORS properly to prevent unauthorized access

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total Tools | 6 |
| Estimated Time | 20 minutes |
| Aggressiveness | Medium |
| Detection Risk | Medium |
| Coverage | High |
| Accuracy | 80-85% |

## Notes

- This pattern is suitable for API security testing
- Can be combined with Web Reconnaissance for comprehensive coverage
- Results should be verified before proceeding to exploitation
- Consider API rate limiting when selecting tool parameters
