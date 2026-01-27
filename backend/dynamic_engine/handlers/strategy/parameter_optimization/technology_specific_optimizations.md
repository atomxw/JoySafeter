# Technology-Specific Optimizations

## Overview

- Purpose: Apply technology-specific parameter optimizations based on detected web servers, CMS platforms, frameworks, and security technologies
- Category: tooling
- Severity: high
- Tags: technology-specific, optimization, web-servers, cms, frameworks, languages, waf-detection, stealth-mode

## Context and Use-Cases

- Customize tool parameters based on detected target technologies
- Optimize scanning strategies for specific web servers and CMS platforms
- Detect and adapt to Web Application Firewalls (WAF)
- Improve scanning effectiveness through technology-aware configuration

## Web Server Optimizations

### Apache

When Apache is detected:
- **Gobuster**: Add extensions `php,html,txt,xml,conf`
- **Nuclei**: Add Apache-specific tags for template matching

### Nginx

When Nginx is detected:
- **Gobuster**: Add extensions `php,html,txt,json,conf`
- **Nuclei**: Add Nginx-specific tags for template matching

## CMS Platform Optimizations

### WordPress

When WordPress is detected:
- **Gobuster**:
  - Extensions: `php,html,txt,xml`
  - Additional paths: `/wp-content/`, `/wp-admin/`, `/wp-includes/`
- **Nuclei**: Add WordPress-specific tags
- **WPScan**: Enable enumeration options `ap,at,cb,dbe` (all plugins, all themes, config backups, database exports)

### Drupal

When Drupal is detected:
- **Gobuster**: Add Drupal-specific paths and extensions
- **Nuclei**: Add Drupal-specific tags

### Joomla

When Joomla is detected:
- **Gobuster**: Add Joomla-specific paths and extensions
- **Nuclei**: Add Joomla-specific tags

## Language-Specific Optimizations

### PHP

When PHP is detected:
- **Gobuster**: Extensions `php,php3,php4,php5,phtml,html`
- **SQLMap**: Set DBMS to `mysql`

### ASP.NET

When ASP.NET (.NET) is detected:
- **Gobuster**: Extensions `aspx,asp,html,txt`
- **SQLMap**: Set DBMS to `mssql`

### Node.js

When Node.js is detected:
- **Gobuster**: Extensions `js,json,html,txt`
- **Nuclei**: Add Node.js-specific tags

## Security Technology Adaptations

### WAF Detection

When WAF is detected (Cloudflare, Incapsula, Sucuri):
- Enable stealth mode across all tools
- Reduce thread counts to minimum (5 threads)
- Increase delays between requests (2 seconds)
- Enable request randomization
- Apply conservative timing profile

**Gobuster adjustments**:
- threads: 5 (reduced from 20)
- delay: 2s
- _stealth_mode: True

**SQLMap adjustments**:
- delay: 2 (seconds)
- randomize: True
- _stealth_mode: True

### Load Balancer Detection

When load balancer is detected (F5, BigIP, HAProxy):
- Adjust connection pooling
- Implement session handling
- Distribute requests across endpoints

### CDN Detection

When CDN is detected (CloudFront, Fastly, KeyCDN):
- Adjust request timing
- Handle cache-related responses
- Account for geographic routing

## Examples

### WordPress on Apache Optimization

Detected technologies: Apache, WordPress, PHP, MySQL

Applied optimizations:
```python
{
    "tool": "gobuster",
    "extensions": "php,html,txt,xml",
    "additional_paths": "/wp-content/,/wp-admin/,/wp-includes/",
    "threads": 20,
    "delay": "0s"
}
```

### ASP.NET with Cloudflare WAF

Detected technologies: IIS, ASP.NET, MSSQL, Cloudflare WAF

Applied optimizations:
```python
{
    "tool": "sqlmap",
    "dbms": "mssql",
    "level": 1,
    "risk": 1,
    "threads": 1,
    "delay": 2,
    "randomize": True,
    "_stealth_mode": True
}
```

## Related Items

- technology_detection_system
- parameter_optimization_advanced
- rate_limit_detection_system
