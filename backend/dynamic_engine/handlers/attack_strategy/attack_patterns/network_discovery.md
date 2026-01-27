# Network Discovery

## Overview

- **Purpose**: Comprehensive network reconnaissance and host enumeration
- **Category**: attack-pattern
- **Severity**: high
- **Target Types**: Network Hosts
- **Execution Time**: 60 minutes
- **Aggressiveness**: High

## Context and Use-Cases

- **Network reconnaissance**: Discover hosts and services on network
- **Service enumeration**: Identify running services and versions
- **SMB enumeration**: Enumerate Windows shares and users
- **Credential harvesting**: Capture credentials from network
- **Network mapping**: Create network topology map

## Procedure / Knowledge Detail

### Tool Sequence (8 tools)

1. **arp-scan** - Local network discovery
2. **rustscan** - Fast port scanning
3. **nmap-advanced** - Advanced scanning with OS detection
4. **masscan** - Ultra-fast scanning
5. **enum4linux-ng** - SMB enumeration
6. **nbtscan** - NetBIOS scanning
7. **smbmap** - SMB share mapping
8. **rpcclient** - RPC enumeration

## Workflow

### Phase 1: Local Network Discovery
```
arp-scan → Discover local hosts
```

### Phase 2: Port Scanning
```
rustscan → Fast port scan
masscan → Comprehensive port scan
```

### Phase 3: Service Detection
```
nmap-advanced → Detect services and OS
```

### Phase 4: SMB/Windows Enumeration
```
enum4linux-ng → SMB enumeration
smbmap → Share mapping
rpcclient → RPC enumeration
nbtscan → NetBIOS scanning
```

## Expected Outputs

- Live hosts on network
- Open ports and services
- Operating system identification
- SMB shares and users
- Domain information
- RPC endpoints

## Related Knowledge Items

- comprehensive_network_pentest
- tool_effectiveness_scoring_system
- technology_signature_detection_system

## Best Practices

1. Start with arp-scan for local network discovery
2. Use rustscan for fast initial scanning
3. Follow up with nmap-advanced for detailed information
4. Enumerate SMB shares for credential harvesting
5. Document all discovered hosts and services
6. Cross-reference findings from multiple tools
7. Monitor network traffic for detection
8. Respect network policies and authorization

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total Tools | 8 |
| Estimated Time | 60 minutes |
| Aggressiveness | High |
| Detection Risk | High |
| Coverage | Very High |
| Accuracy | 90-95% |

## Notes

- This pattern requires network access
- Can be combined with comprehensive_network_pentest
- Results should be documented carefully
- Consider network monitoring when executing
