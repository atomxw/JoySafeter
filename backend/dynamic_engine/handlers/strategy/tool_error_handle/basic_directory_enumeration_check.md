# Basic Directory Enumeration Check

## Overview

- Purpose: Perform fallback web directory discovery using HTTP HEAD requests when primary tools (gobuster, feroxbuster) fail.
- Category: incident_response
- Severity: medium
- Tags: directory-discovery, fallback, web-discovery, incident-response

## Context and Use-Cases

- Graceful degradation when gobuster or feroxbuster timeout or crash.
- Quick validation of common web paths and endpoints.
- Lightweight alternative for resource-constrained environments.

## Procedure / Knowledge detail

HTTP-based directory discovery performs the following steps:

1. Accept target URL.
2. Iterate through common directories: /admin, /login, /api, /wp-admin, /phpmyadmin, /robots.txt.
3. For each directory, construct full URL and send HEAD request with 5-second timeout.
4. Accept responses with status codes 200, 301, 302, or 403 as "found".
5. Collect found directories in a list.
6. Return list of found directories or empty list if target is invalid.

## Examples

- Command:

  ```python
  found_dirs = degradation_manager._basic_directory_check("https://example.com")
  # Returns: ["/admin", "/api", "/robots.txt"]
  ```

- Code Snippet:

  ```python
  for directory in common_dirs:
      try:
          url = f"{target.rstrip('/')}{directory}"
          response = requests.head(url, timeout=5, allow_redirects=True)
          if response.status_code in [200, 301, 302, 403]:
              found_dirs.append(directory)
      except Exception:
          continue
  ```

- Log Query/Rule:

  ```text
  "Basic directory check" AND "directories" AND "degradation"
  ```
