# Domain Resolution System

## Overview

- **Purpose**: Convert domain names and URLs to IP addresses using DNS resolution. Enables network-level reconnaissance and target identification.
- **Category**: tooling
- **Severity**: medium
- **Tags**: dns-resolution, domain-lookup, ip-address-resolution, reconnaissance, network-analysis, decision-engine

## Context and Use-Cases

The domain resolution system is essential for:

- **Target Identification**: Map domain names to IP addresses for network scanning
- **Network Reconnaissance**: Identify infrastructure hosting the target
- **Multi-IP Scenarios**: Detect when a domain resolves to multiple IP addresses (load balancing, CDN)
- **Attack Surface Mapping**: Understand the network infrastructure behind a target
- **Scope Validation**: Verify targets are within authorized scope before testing
- **Infrastructure Analysis**: Identify shared hosting and related services

## Procedure / Knowledge Detail

### Resolution Process

The domain resolution system follows a two-step process:

#### Step 1: Hostname Extraction

**Input Processing**:

- Check if input is a URL (starts with `http://` or `https://`)
- If URL: Extract hostname using `urllib.parse.urlparse(target).hostname`
- If not URL: Use input directly as hostname

**Supported Input Formats**:

- Direct domain names: `example.com`, `api.example.com`, `subdomain.example.co.uk`
- HTTP URLs: `http://example.com`, `http://example.com:8080/path`
- HTTPS URLs: `https://example.com`, `https://example.com/api/v1`
- URLs with paths: `https://example.com/path/to/resource`
- URLs with ports: `https://example.com:8443/endpoint`

#### Step 2: DNS Resolution

**Resolution Method**:

- Uses `socket.gethostbyname(hostname)` for DNS lookup
- Performs synchronous DNS resolution
- Returns single IP address (first result from DNS response)

**Return Values**:

- Success: List containing single IP address `[ip_address]`
- Failure: Empty list `[]`

### Error Handling

**Exception Handling**:

- Catches all exceptions during resolution
- Returns empty list on any error
- Silently fails without logging or raising exceptions

**Common Failure Scenarios**:

- Invalid hostname format
- DNS server unreachable
- Domain name does not exist
- Network connectivity issues
- Malformed URL input
- Hostname extraction failure

### Implementation Details

**URL Parsing**:
- Uses `urllib.parse.urlparse()` to extract hostname component
- Automatically handles URL schemes, ports, and paths
- Extracts only the hostname portion for DNS lookup

**DNS Lookup**:
- `socket.gethostbyname()` performs A record lookup
- Returns IPv4 address only (not IPv6)
- Blocks until resolution completes or times out
- Uses system DNS configuration
