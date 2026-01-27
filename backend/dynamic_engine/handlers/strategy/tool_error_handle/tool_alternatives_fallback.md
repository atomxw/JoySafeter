# Tool Alternatives Fallback

## Overview

- Purpose: Provide fallback chains for security tools to enable automatic tool substitution on failure
- Category: incident_response
- Severity: high
- Tags: tool-alternatives, fallback, incident-response

## Context and Use-Cases

- Automatic tool substitution when primary tool fails
- Handling missing tool installations
- Bypassing tool-specific limitations
- Maintaining scan continuity during tool failures

## Procedure / Knowledge detail

### Tool Alternative Mappings

The system maintains fallback chains for 30+ security tools across 11 categories:

#### Network Scanning Tools

```
nmap → [rustscan, masscan, zmap]
rustscan → [nmap, masscan]
masscan → [nmap, rustscan, zmap]
```

#### Directory/File Discovery Tools

```
gobuster → [feroxbuster, dirsearch, ffuf, dirb]
feroxbuster → [gobuster, dirsearch, ffuf]
dirsearch → [gobuster, feroxbuster, ffuf]
ffuf → [gobuster, feroxbuster, dirsearch]
```

#### Vulnerability Scanning Tools

```
nuclei → [jaeles, nikto, w3af]
jaeles → [nuclei, nikto]
nikto → [nuclei, jaeles, w3af]
```

#### Web Crawling Tools

```
katana → [gau, waybackurls, hakrawler]
gau → [katana, waybackurls, hakrawler]
waybackurls → [gau, katana, hakrawler]
```

#### Parameter Discovery Tools

```
arjun → [paramspider, x8, ffuf]
paramspider → [arjun, x8]
x8 → [arjun, paramspider]
```

#### SQL Injection Tools

```
sqlmap → [sqlninja, jsql-injection]
```

#### XSS Testing Tools

```
dalfox → [xsser, xsstrike]
```

#### Subdomain Enumeration Tools

```
subfinder → [amass, assetfinder, findomain]
amass → [subfinder, assetfinder, findomain]
assetfinder → [subfinder, amass, findomain]
```

#### Cloud Security Tools

```
prowler → [scout-suite, cloudmapper]
scout-suite → [prowler, cloudmapper]
```

#### Container Security Tools

```
trivy → [clair, docker-bench-security]
clair → [trivy, docker-bench-security]
```

#### Binary Analysis Tools

```
ghidra → [radare2, ida, binary-ninja]
radare2 → [ghidra, objdump, gdb]
gdb → [radare2, lldb]
```

#### Exploitation Tools

```
pwntools → [ropper, ropgadget]
ropper → [ropgadget, pwntools]
ropgadget → [ropper, pwntools]
```

### Fallback Selection Algorithm

1. **Get alternatives** for failed tool
2. **Filter alternatives** based on context requirements:
   - If `require_no_privileges` is set, skip privilege-requiring tools
   - If `prefer_faster_tools` is set, skip slower tools
   - If `prefer_offline_tools` is set, skip network-dependent tools
3. **Return first available** alternative from filtered list
4. **Return None** if no alternatives available

## Examples

### Tool Fallback Example

```python
from error_handler_error_handler import IntelligentErrorHandler

handler = IntelligentErrorHandler()

# Get alternative for failed nmap
alt_tool = handler.get_alternative_tool("nmap", {})
# Returns: "rustscan"

# Get alternative with context requirements
alt_tool = handler.get_alternative_tool(
    "nmap",
    {"require_no_privileges": True, "prefer_faster_tools": True}
)
# Returns: "rustscan" (filtered alternatives)

# Get alternative for gobuster
alt_tool = handler.get_alternative_tool("gobuster", {})
# Returns: "feroxbuster"
```

### Tool Substitution in Recovery

```python
from error_handler_error_handler import IntelligentErrorHandler, ErrorType

handler = IntelligentErrorHandler()

# Simulate tool failure
failed_tool = "nmap"
error_type = ErrorType.TIMEOUT
context = {"prefer_faster_tools": True}

# Get recovery strategy
strategies = handler.recovery_strategies[error_type]
best_strategy = handler._select_best_strategy(strategies, error_context)

# If strategy is SWITCH_TO_ALTERNATIVE_TOOL
if best_strategy.action.value == "switch_to_alternative_tool":
    alt_tool = handler.get_alternative_tool(failed_tool, context)
    print(f"Switching from {failed_tool} to {alt_tool}")
    # Execute alt_tool with similar parameters
```

## Tool Categories and Characteristics

### Fast Tools (for timeout scenarios)
- rustscan (faster than nmap)
- feroxbuster (concurrent requests)
- ffuf (fast fuzzing)
- masscan (mass scanning)

### Privilege-Free Tools (for permission denied scenarios)
- gau (web archive)
- waybackurls (historical URLs)
- subfinder (passive subdomain)
- assetfinder (passive reconnaissance)

### Offline Tools (for network unreachable scenarios)
- ghidra (binary analysis)
- radare2 (binary analysis)
- gdb (debugging)
- pwntools (exploitation)

## Related Knowledge Items

- **error_classification_patterns** - Error type detection
- **timeout_error_recovery** - Timeout handling
- **parameter_auto_adjustment** - Parameter optimization
