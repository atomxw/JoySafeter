# Bug Bounty Reconnaissance

## Overview

- **Purpose**: Comprehensive reconnaissance for bug bounty programs
- **Category**: attack-pattern
- **Severity**: high
- **Target Types**: Web Applications, API Endpoints
- **Execution Time**: 90 minutes
- **Aggressiveness**: Medium

## Context and Use-Cases

- **Subdomain enumeration**: Discover subdomains
- **HTTP probing**: Probe discovered endpoints
- **Web crawling**: Crawl web application
- **URL collection**: Collect historical URLs
- **Parameter discovery**: Discover hidden parameters
- **Attack surface mapping**: Map complete attack surface

## Procedure / Knowledge Detail

### Tool Sequence (8 tools)

1. **amass** - Subdomain enumeration
2. **subfinder** - Subdomain discovery
3. **httpx** - HTTP probing
4. **katana** - Web crawling
5. **gau** - URL collection
6. **waybackurls** - Historical URLs
7. **paramspider** - Parameter discovery
8. **arjun** - Parameter discovery

## Expected Outputs

- Discovered subdomains
- Live endpoints
- Crawled URLs
- Historical URLs
- Discovered parameters
- Complete attack surface map

## Related Knowledge Items

- web_reconnaissance
- bug_bounty_vulnerability_hunting
- bug_bounty_high_impact
- tool_effectiveness_scoring_system

## Best Practices

1. Start with amass and subfinder for subdomains
2. Probe with httpx for live endpoints
3. Crawl with katana for URL discovery
4. Collect historical URLs with gau and waybackurls
5. Discover parameters with paramspider and arjun
6. Document all findings
7. Organize by subdomain
8. Prepare for vulnerability hunting

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total Tools | 8 |
| Estimated Time | 90 minutes |
| Aggressiveness | Medium |
| Detection Risk | Medium |
| Coverage | Very High |
| Accuracy | 85-90% |

## Notes

- This is comprehensive reconnaissance phase
- Can be combined with vulnerability hunting
- Results depend on target scope
- Requires careful scope management
