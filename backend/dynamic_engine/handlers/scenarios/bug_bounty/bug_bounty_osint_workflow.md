# Bug Bounty OSINT Workflow

## Overview

- Purpose: Gather comprehensive open-source intelligence on target organization
- Category: osint
- Severity: medium
- Tags: bug-bounty, osint, intelligence-gathering, reconnaissance, information-gathering

## Context and Use-Cases

- Building organizational profile before technical testing
- Identifying employees, infrastructure, and technology stack
- Discovering email patterns and user information
- Finding publicly exposed information and credentials
- Estimated time: 240 minutes (4 hours)

## Procedure / Knowledge detail

### Four OSINT Phases

#### Phase 1: Domain Intelligence

**Objective**: Gather technical information about target domain

**Tools**:
- whois: `{"domain": target.domain}` - Domain registration info
- dnsrecon: `{"domain": target.domain}` - DNS records and zone transfers
- certificate_transparency: `{"domain": target.domain}` - SSL certificate history

**Information Gathered**:
- Domain registrant information
- DNS records (A, MX, NS, TXT)
- Historical SSL certificates
- Subdomain history
- IP address associations

#### Phase 2: Social Media Intelligence

**Objective**: Identify organization and employees on social platforms

**Tools**:
- sherlock: `{"username": "target_company"}` - Username enumeration
- social_mapper: `{"company": target.domain}` - Social media mapping
- linkedin_scraper: `{"company": target.domain}` - LinkedIn employee enumeration

**Information Gathered**:
- Company social media accounts
- Employee names and titles
- Organizational structure
- Technology stack mentions
- Security practices insights

#### Phase 3: Email Intelligence

**Objective**: Discover email addresses and breach information

**Tools**:
- hunter_io: `{"domain": target.domain}` - Email pattern discovery
- haveibeenpwned: `{"domain": target.domain}` - Breach database lookup
- email_validator: `{"domain": target.domain}` - Email validation

**Information Gathered**:
- Email address patterns
- Valid email addresses
- Breach history
- Compromised credentials
- Employee email lists

#### Phase 4: Technology Intelligence

**Objective**: Identify technology stack and infrastructure

**Tools**:
- builtwith: `{"domain": target.domain}` - Technology detection
- wappalyzer: `{"domain": target.domain}` - Web technology identification
- shodan: `{"query": f"hostname:{target.domain}"}` - Internet-wide scanning

**Information Gathered**:
- Web server and frameworks
- CMS and plugins
- Analytics and tracking
- Hosting provider
- Open ports and services
- Exposed devices

### OSINT Intelligence Types

| Intelligence Type | Sources | Value |
|---|---|---|
| Technical | whois, dnsrecon, CT | Infrastructure mapping |
| Social | LinkedIn, Twitter, Facebook | Organizational structure |
| Business | Company websites, news | Business model, partnerships |
| Infrastructure | Shodan, Censys, Zoomeye | Exposed services, devices |

## Examples

### Example 1: Domain Intelligence Gathering

```
Target: example.com

WHOIS Output:
- Registrant: John Doe
- Registrar: GoDaddy
- Created: 2015-03-15
- Updated: 2024-01-10

DNS Records:
- A: 192.0.2.1
- MX: mail.example.com
- NS: ns1.example.com, ns2.example.com

SSL Certificates:
- 2024-01-10: *.example.com (Let's Encrypt)
- 2023-01-10: example.com (DigiCert)
- 2022-01-10: example.com (Comodo)
```

### Example 2: Employee Discovery

```
Target: example.com

LinkedIn Results:
- 250 employees found
- CTO: Jane Smith (jane.smith@example.com)
- DevOps Lead: Bob Johnson (bob.johnson@example.com)
- Security Engineer: Alice Williams (alice.williams@example.com)

Email Pattern: firstname.lastname@example.com
```

### Example 3: Technology Stack Discovery

```
Target: example.com

Builtwith Results:
- Web Server: Nginx 1.24.0
- Framework: Django 4.2
- CMS: WordPress 6.4
- Analytics: Google Analytics
- CDN: Cloudflare

Shodan Results:
- Open Ports: 80, 443, 8080, 3306
- Services: HTTP, HTTPS, MySQL
- Exposed: Jenkins (port 8080), MongoDB (port 27017)
```

## Related Knowledge Items

- bug_bounty_target_classification - Target definition and scope
- bug_bounty_reconnaissance_workflow - Technical reconnaissance
- vulnerability_testing_scenarios - Vulnerability testing

## Best Practices

1. **Start with OSINT** - Gather intelligence before technical testing
2. **Use multiple sources** - Cross-reference information
3. **Document findings** - Maintain comprehensive intelligence database
4. **Identify patterns** - Look for email patterns, naming conventions
5. **Monitor for changes** - Re-run OSINT periodically
6. **Respect scope** - Only target in-scope domains
7. **Combine with technical recon** - Link OSINT with technical findings
8. **Identify key personnel** - Find security contacts and decision makers
