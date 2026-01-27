# Manual Remediation Recommendations

## Overview

- Purpose: Generate context-aware manual remediation recommendations when automated tools fail, guiding analysts toward next steps.
- Category: incident_response
- Severity: medium
- Tags: manual-remediation, incident-response, fallback, analyst-guidance

## Context and Use-Cases

- Incident response workflows that escalate to human analysts with actionable guidance.
- Playbooks that provide step-by-step manual alternatives when automation fails.
- Training materials for security analysts on fallback techniques.

## Procedure / Knowledge detail

Manual recommendations are generated based on operation type and failed components:

### Base Recommendations by Operation

**Network Discovery**:

- Manually test common ports using telnet or nc
- Check for service banners manually
- Use online port scanners as alternative

**Web Discovery**:

- Manually browse common directories
- Check robots.txt and sitemap.xml
- Use browser developer tools for endpoint discovery

**Vulnerability Scanning**:

- Manually test for common vulnerabilities
- Check security headers using browser tools
- Perform manual input validation testing

**Subdomain Enumeration**:

- Use online subdomain discovery tools
- Check certificate transparency logs
- Perform manual DNS queries

### Component-Specific Recommendations

**Failed nmap**:

- Consider using online port scanners

**Failed gobuster**:

- Try manual directory browsing

**Failed nuclei**:

- Perform manual vulnerability testing

## Examples

- Command:

  ```python
  recommendations = degradation_manager._get_manual_recommendations(
      operation="network_discovery",
      failed_components=["nmap", "rustscan"]
  )
  # Returns: [
  #   "Manually test common ports using telnet or nc",
  #   "Check for service banners manually",
  #   "Use online port scanners as alternative",
  #   "Consider using online port scanners"
  # ]
  ```

- Analyst Workflow:

  ```text
  1. Receive degradation_info with failed_components: ["nmap"]
  2. Get manual_recommendations from response
  3. Execute recommended manual steps (telnet, nc, online tools)
  4. Document findings in incident report
  5. Update tool inventory if needed
  ```

- Log Query/Rule:

  ```text
  "manual_recommendations" AND "failed_components" AND "operation"
  ```
