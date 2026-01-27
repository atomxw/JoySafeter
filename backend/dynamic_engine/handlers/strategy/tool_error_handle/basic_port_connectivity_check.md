# Basic Port Connectivity Check

## Overview

- Purpose: Perform fallback port scanning using raw socket connections when primary network scanners (nmap, rustscan) fail.
- Category: incident_response
- Severity: medium
- Tags: port-scanning, fallback, network-discovery, incident-response

## Context and Use-Cases

- Graceful degradation when nmap or rustscan timeout or crash.
- Quick connectivity validation to common service ports.
- Lightweight alternative for resource-constrained environments.

## Procedure / Knowledge detail

Socket-based port scanning performs the following steps:

1. Accept target hostname or IP address.
2. Iterate through common ports: 21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995.
3. For each port, create a TCP socket with 2-second timeout.
4. Attempt connection which returns success (0) or failure (non-zero).
5. Collect open ports in a list and close the socket.
6. Return list of open ports or empty list if target is invalid.

## Examples

- Command:

  ```python
  open_ports = degradation_manager._basic_port_check("192.168.1.100")
  # Returns: [22, 80, 443]
  ```

- Code Snippet:

  ```python
  for port in common_ports:
      try:
          sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          sock.settimeout(2)
          result = sock.connect_ex((target, port))
          if result == 0:
              open_ports.append(port)
          sock.close()
      except Exception:
          continue
  ```

- Log Query/Rule:

  ```text
  "Basic port check" AND "open_ports" AND "degradation"
  ```
