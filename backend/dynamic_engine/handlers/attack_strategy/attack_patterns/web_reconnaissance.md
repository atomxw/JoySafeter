# Web Reconnaissance

## Overview

- **Purpose**: Comprehensive web application reconnaissance and technology discovery
- **Category**: attack-pattern
- **Severity**: high
- **Target Types**: Web Applications, API Endpoints
- **Execution Time**: 45 minutes
- **Aggressiveness**: Medium

## Context and Use-Cases

- **Initial reconnaissance**: Discover web application structure and technologies
- **Technology identification**: Identify web servers, frameworks, and CMS platforms
- **Vulnerability discovery**: Find potential security issues through scanning
- **Attack surface mapping**: Understand the complete attack surface
- **Baseline assessment**: Establish baseline for security testing

## Procedure / Knowledge Detail

### Tool Sequence (8 tools)

#### 1. nmap - Port Scanning (Priority 1)
- **Purpose**: Identify open ports and services
- **Parameters**: scan_type: "-sV -sC", ports: "80,443,8080,8443"
- **Output**: Open ports, service versions, basic fingerprinting
- **Time**: 5-10 minutes

#### 2. httpx - HTTP Probing (Priority 2)
- **Purpose**: Probe HTTP endpoints and detect technologies
- **Parameters**: probe: True, tech_detect: True
- **Output**: Live hosts, HTTP status codes, technology detection
- **Time**: 5-10 minutes

#### 3. katana - Web Crawling (Priority 3)
- **Purpose**: Crawl web application and discover endpoints
- **Parameters**: depth: 3, js_crawl: True
- **Output**: Discovered URLs, endpoints, JavaScript files
- **Time**: 10-15 minutes

#### 4. gau - URL Collection (Priority 4)
- **Purpose**: Collect historical URLs from archives
- **Parameters**: include_subs: True
- **Output**: Historical URLs, potential endpoints
- **Time**: 5-10 minutes

#### 5. waybackurls - Historical URLs (Priority 5)
- **Purpose**: Retrieve URLs from Wayback Machine
- **Parameters**: get_versions: False
- **Output**: Historical versions, old endpoints
- **Time**: 5-10 minutes

#### 6. nuclei - Vulnerability Scanning (Priority 6)
- **Purpose**: Scan for known vulnerabilities
- **Parameters**: severity: "critical,high", tags: "tech"
- **Output**: Vulnerability findings, technology confirmation
- **Time**: 10-15 minutes

#### 7. dirsearch - Directory Enumeration (Priority 7)
- **Purpose**: Enumerate common directories
- **Parameters**: extensions: "php,html,js,txt", threads: 30
- **Output**: Found directories, files
- **Time**: 10-15 minutes

#### 8. gobuster - Directory Brute-Force (Priority 8)
- **Purpose**: Brute-force directory names
- **Parameters**: mode: "dir", extensions: "php,html,js,txt"
- **Output**: Additional directories, hidden content
- **Time**: 10-15 minutes

## Workflow

### Phase 1: Initial Scanning (5-10 min)
```
nmap → Identify open ports and services
```

### Phase 2: HTTP Probing (5-10 min)
```
httpx → Probe endpoints and detect technologies
```

### Phase 3: Content Discovery (20-30 min)
```
katana → Crawl web application
gau → Collect historical URLs
waybackurls → Retrieve archived URLs
```

### Phase 4: Vulnerability Scanning (10-15 min)
```
nuclei → Scan for known vulnerabilities
```

### Phase 5: Directory Enumeration (20-30 min)
```
dirsearch → Enumerate common directories
gobuster → Brute-force additional directories
```

## Implementation Example

```python
# Web Reconnaissance Pattern
pattern = {
    "web_reconnaissance": [
        {"tool": "nmap", "priority": 1, "params": {"scan_type": "-sV -sC", "ports": "80,443,8080,8443"}},
        {"tool": "httpx", "priority": 2, "params": {"probe": True, "tech_detect": True}},
        {"tool": "katana", "priority": 3, "params": {"depth": 3, "js_crawl": True}},
        {"tool": "gau", "priority": 4, "params": {"include_subs": True}},
        {"tool": "waybackurls", "priority": 5, "params": {"get_versions": False}},
        {"tool": "nuclei", "priority": 6, "params": {"severity": "critical,high", "tags": "tech"}},
        {"tool": "dirsearch", "priority": 7, "params": {"extensions": "php,html,js,txt", "threads": 30}},
        {"tool": "gobuster", "priority": 8, "params": {"mode": "dir", "extensions": "php,html,js,txt"}}
    ]
}

# Execute pattern
for tool_config in pattern["web_reconnaissance"]:
    tool_name = tool_config["tool"]
    params = tool_config["params"]
    result = execute_tool(tool_name, params)
    process_results(result)
```

## Expected Outputs

### Technology Discovery
- Web server identification (Apache, Nginx, IIS, etc.)
- Framework detection (PHP, Python, Node.js, etc.)
- CMS identification (WordPress, Drupal, Joomla, etc.)
- Frontend framework detection (React, Angular, Vue, etc.)

### Vulnerability Findings
- Known vulnerabilities
- Misconfigurations
- Outdated software versions
- Security header issues

### Endpoint Discovery
- Web application endpoints
- API endpoints
- Hidden directories
- Historical endpoints

## Related Knowledge Items

- **api_testing**: For API-specific testing
- **vulnerability_assessment**: For deeper vulnerability scanning
- **bug_bounty_reconnaissance**: For comprehensive reconnaissance
- **tool_effectiveness_scoring_system**: Tool effectiveness ratings
- **technology_signature_detection_system**: Technology detection methods

## Best Practices

1. **Start with nmap**: Always begin with port scanning to identify services
2. **Use multiple tools**: Combine different tools for comprehensive coverage
3. **Monitor resources**: Watch CPU and network usage during crawling
4. **Respect rate limits**: Adjust threads and delays to avoid detection
5. **Document findings**: Record all discovered endpoints and technologies
6. **Verify results**: Cross-reference findings from multiple tools
7. **Update signatures**: Keep nuclei templates and wordlists updated
8. **Combine results**: Merge findings from all tools for complete picture

## Mitigation & Best Practices

### For Defense

1. **Hide Technology Signatures**: Remove identifying headers and banners
2. **Implement WAF**: Deploy Web Application Firewall to block scanning
3. **Rate Limiting**: Implement rate limiting to slow down enumeration
4. **Honeypots**: Deploy fake endpoints to detect reconnaissance
5. **Monitoring**: Alert on suspicious scanning activity
6. **Security Headers**: Implement proper security headers
7. **Content Security Policy**: Restrict resource loading
8. **Regular Updates**: Keep software patched and updated
9. **Access Control**: Restrict access to sensitive directories
10. **Logging**: Maintain detailed logs of all access attempts

## Troubleshooting

### Issue: Tools running slowly
- **Solution**: Reduce thread count, increase timeout values
- **Alternative**: Run tools in parallel on different machines

### Issue: Rate limiting detected
- **Solution**: Reduce request rate, add delays between requests
- **Alternative**: Use different IP addresses or proxies

### Issue: Firewall blocking requests
- **Solution**: Use different ports, protocols, or user agents
- **Alternative**: Use VPN or proxy service

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total Tools | 8 |
| Estimated Time | 45 minutes |
| Aggressiveness | Medium |
| Detection Risk | Medium |
| Coverage | High |
| Accuracy | 85-90% |

## Notes

- This pattern is suitable for initial reconnaissance
- Can be combined with API Testing for comprehensive coverage
- Results should be verified before proceeding to exploitation
- Consider target's security posture when selecting aggressiveness level
