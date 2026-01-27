# Graceful Degradation Fallback Chains

## Overview

- Purpose: Preserve mission-critical reconnaissance steps by dynamically switching to pre-defined fallback tool chains when preferred automation fails.
- Category: incident_response
- Severity: high
- Tags: graceful-degradation, fallback, reconnaissance, incident-response

## Context and Use-Cases

- Automated scanning pipelines that must continue providing coverage even when primary tools crash or become unavailable.
- Response playbooks that require deterministic substitution paths for discovery and enumeration stages.
- Situations where maintaining partial visibility is preferable to aborting the operation entirely.

## Procedure / Knowledge detail

1. Maintain fallback chains per critical operation with multi-level alternatives:
   - **network_discovery**: [nmap, rustscan, masscan] → [rustscan, nmap] → [ping, telnet]
   - **web_discovery**: [gobuster, feroxbuster, dirsearch] → [feroxbuster, ffuf] → [curl, wget]
   - **vulnerability_scanning**: [nuclei, jaeles, nikto] → [nikto, w3af] → [curl]
   - **subdomain_enumeration**: [subfinder, amass, assetfinder] → [amass, findomain] → [dig, nslookup]
   - **parameter_discovery**: [arjun, paramspider, x8] → [ffuf, wfuzz] → [manual_testing]

2. Flag operations that must never fully fail: network_discovery, web_discovery, vulnerability_scanning, subdomain_enumeration. The system always attempts degradation paths for these critical operations.

3. When a tool fails, build the first viable chain that excludes the failed components and log the choice, or fall back to the basic substitutes (e.g., network_discovery → ping) if none remain.

## Examples

- Command:

  ```python
  chain = degradation_manager.create_fallback_chain(
      operation="web_discovery",
      failed_tools=["gobuster"]
  )
  # -> ["feroxbuster", "ffuf"]
  ```

- Log Query/Rule:

  ```text
  "Graceful degradation applied" AND "Fallback chain for network_discovery"
  ```
