# Bug Bounty Reconnaissance Workflow

## Overview

- Purpose: Execute comprehensive multi-phase reconnaissance to gather intelligence on target
- Category: osint
- Severity: high
- Tags: bug-bounty, reconnaissance, osint, information-gathering, workflow

## Context and Use-Cases

- Building comprehensive attack surface map before vulnerability testing
- Discovering hidden assets, subdomains, and endpoints
- Identifying technology stack and potential vulnerabilities
- Maximizing coverage to find all possible entry points

## Procedure / Knowledge detail

### Four-Phase Reconnaissance Workflow

#### Phase 1: Subdomain Discovery (300 seconds)

**Objective**: Enumerate all subdomains within target scope

**Tools**:
- amass: `{"domain": target.domain, "mode": "enum"}`
- subfinder: `{"domain": target.domain, "silent": True}`
- assetfinder: `{"domain": target.domain}`

**Expected Outputs**: subdomains.txt

**Key Findings**:
- All in-scope subdomains
- Subdomain count and patterns
- Potential acquisition targets

#### Phase 2: HTTP Service Discovery (180 seconds)

**Objective**: Identify live HTTP services and technology stack

**Tools**:
- httpx: `{"probe": True, "tech_detect": True, "status_code": True}`
- nuclei: `{"tags": "tech", "severity": "info"}`

**Expected Outputs**: live_hosts.txt, technologies.json

**Key Findings**:
- Live HTTP services
- Technology detection (web servers, frameworks, CMS)
- HTTP status codes and redirects

#### Phase 3: Content Discovery (600 seconds)

**Objective**: Discover hidden content, endpoints, and files

**Tools**:
- katana: `{"depth": 3, "js_crawl": True}` - JavaScript crawling
- gau: `{"include_subs": True}` - Historical URLs
- waybackurls: `{}` - Wayback Machine URLs
- dirsearch: `{"extensions": "php,html,js,txt,json,xml"}`

**Expected Outputs**: endpoints.txt, js_files.txt

**Key Findings**:
- Hidden endpoints and paths
- JavaScript files (potential parameter discovery)
- API endpoints
- Admin panels and debug pages

#### Phase 4: Parameter Discovery (240 seconds)

**Objective**: Discover hidden parameters in URLs and forms

**Tools**:
- paramspider: `{"level": 2}` - Historical parameter discovery
- arjun: `{"method": "GET,POST", "stable": True}` - Parameter fuzzing
- x8: `{"method": "GET"}` - Parameter discovery

**Expected Outputs**: parameters.txt

**Key Findings**:
- Hidden parameters
- Parameter patterns
- Potential injection points

### Workflow Execution Timeline

| Phase | Duration | Tools | Output |
|---|---|---|---|
| Subdomain Discovery | 300s | 3 | subdomains.txt |
| HTTP Service Discovery | 180s | 2 | live_hosts.txt, technologies.json |
| Content Discovery | 600s | 4 | endpoints.txt, js_files.txt |
| Parameter Discovery | 240s | 3 | parameters.txt |
| **Total** | **1320s (22 min)** | **12** | **5 files** |

## Examples

### Example 1: Web Application Reconnaissance

```
Target: example.com
Scope: example.com, *.example.com

Phase 1 Output:
- api.example.com
- admin.example.com
- staging.example.com
- cdn.example.com

Phase 2 Output:
- Apache 2.4.41 on api.example.com
- Nginx 1.18.0 on admin.example.com
- WordPress 5.9 on staging.example.com

Phase 3 Output:
- /api/v1/users
- /admin/login
- /wp-admin
- /assets/js

Phase 4 Output:
- id, user_id, page, limit
- search, filter, sort
```

### Example 2: API Program Reconnaissance

```
Target: api.company.io
Scope: api.company.io, api-v2.company.io

Phase 1: Discover api-v2.company.io, api-staging.company.io
Phase 2: Identify Node.js/Express, GraphQL endpoints
Phase 3: Discover /graphql, /rest/api/v1, /webhooks
Phase 4: Find user_id, org_id, token, api_key parameters
```

## Related Knowledge Items

- bug_bounty_target_classification - Target definition and scope
- vulnerability_testing_scenarios - Test cases for discovered endpoints
- bug_bounty_osint_workflow - Additional OSINT gathering

## Best Practices

1. **Run phases sequentially** - Each phase builds on previous results
2. **Combine multiple tools** - Different tools discover different assets
3. **Save all outputs** - Maintain comprehensive asset inventory
4. **Verify findings** - Cross-check results between tools
5. **Monitor for changes** - Re-run periodically for new discoveries
6. **Document scope** - Track in-scope vs out-of-scope findings
7. **Prioritize findings** - Focus on high-value endpoints first
