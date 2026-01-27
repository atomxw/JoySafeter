# Technology Detection System

## Overview
- Purpose: Advanced technology detection for context-aware parameter selection in security tools
- Category: tooling
- Severity: medium
- Tags: technology-detection, fingerprinting, context-aware, web-servers, frameworks, cms, databases, languages, security-tools

## Context and Use-Cases
- Automatically identify target technologies to optimize tool parameters
- Detect web servers, frameworks, CMS platforms, databases, programming languages, and security solutions
- Enable technology-specific tool configuration and attack vector selection
- Support intelligent parameter tuning based on detected technology stack

## Detection Methods

### 1. Header-Based Detection
Analyzes HTTP response headers to identify technologies:
- Web servers: Apache, Nginx, IIS, Tomcat, Jetty, Lighttpd
- Frameworks: Django, Flask, Express, Laravel, Symfony, Rails, Spring, Struts
- CMS: WordPress, Drupal, Joomla, Magento, PrestaShop, OpenCart
- Databases: MySQL, PostgreSQL, MSSQL, Oracle, MongoDB, Redis
- Languages: PHP, Python, Java, ASP.NET, Node.js, Ruby, Go, Rust
- Security: WAF (Cloudflare, Incapsula, Sucuri), Load Balancers, CDN

### 2. Content-Based Detection
Analyzes response body content for technology indicators:
- URL patterns (e.g., `/wp-admin/`, `/sites/default/`)
- Technology-specific strings and signatures
- Framework-specific cookies and session identifiers
- CMS-specific paths and configuration files

### 3. Port-Based Service Detection
Maps open ports to common services:
```
21: ftp
22: ssh
23: telnet
25: smtp
53: dns
80: http
110: pop3
143: imap
443: https
993: imaps
995: pop3s
1433: mssql
3306: mysql
5432: postgresql
6379: redis
27017: mongodb
8080: http-alt
8443: https-alt
9200: elasticsearch
11211: memcached
```

## Procedure / Knowledge Detail

### Detection Pattern Categories

**Web Servers:**
- Apache: Apache, apache, httpd
- Nginx: nginx, Nginx
- IIS: Microsoft-IIS, IIS
- Tomcat: Tomcat, Apache-Coyote
- Jetty: Jetty
- Lighttpd: lighttpd

**Frameworks:**
- Django: Django, django, csrftoken
- Flask: Flask, Werkzeug
- Express: Express, X-Powered-By: Express
- Laravel: Laravel, laravel_session
- Symfony: Symfony, symfony
- Rails: Ruby on Rails, rails, _session_id
- Spring: Spring, JSESSIONID
- Struts: Struts, struts

**CMS Platforms:**
- WordPress: wp-content, wp-includes, WordPress, /wp-admin/
- Drupal: Drupal, drupal, /sites/default/, X-Drupal-Cache
- Joomla: Joomla, joomla, /administrator/, com_content
- Magento: Magento, magento, Mage.Cookies
- PrestaShop: PrestaShop, prestashop
- OpenCart: OpenCart, opencart

**Security Technologies:**
- WAF: cloudflare, CloudFlare, X-CF-Ray, incapsula, Incapsula, sucuri, Sucuri
- Load Balancers: F5, BigIP, HAProxy, nginx, AWS-ALB
- CDN: CloudFront, Fastly, KeyCDN, MaxCDN, Cloudflare

## Examples

### Detection Output Structure
```python
{
    "web_servers": ["nginx"],
    "frameworks": ["express"],
    "cms": [],
    "databases": ["mysql"],
    "languages": ["nodejs"],
    "security": ["cloudflare"],
    "services": ["http", "https", "mysql"]
}
```

### Usage in Parameter Optimization
When WordPress is detected on Apache:
- Gobuster: Add extensions `php,html,txt,xml` and paths `/wp-content/,/wp-admin/,/wp-includes/`
- Nuclei: Add WordPress-specific tags for template matching
- WPScan: Enable WordPress enumeration options

When WAF (Cloudflare) is detected:
- Enable stealth mode across all tools
- Reduce thread counts to avoid detection
- Increase delays between requests
- Apply randomization to requests

## Related Items
- parameter_optimization_advanced
- rate_limit_detection_system
- technology_specific_optimizations
- tool_failure_recovery_system
