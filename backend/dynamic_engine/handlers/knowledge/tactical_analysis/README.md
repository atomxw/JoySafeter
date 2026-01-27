# Tactical Analysis Knowledge Base

This directory contains structured tactical analysis knowledge extracted from `engine/knowledge/vul_correlators.py` using the extraction prompt `docs/prompts/extract_cybersecurity_knowledge_prompt_v2.md`.

## Overview

All knowledge items follow the standardized format with paired YAML (metadata) and Markdown (documentation) files, optimized for penetration testing and red/blue team operations.

## Knowledge Items

### 1. Attack Chain Pattern Taxonomy
- **Files**: `attack_chain_pattern_taxonomy.yaml` + `.md`
- **Severity**: Info
- **Description**: Keyword-based taxonomy for classifying CVE descriptions into MITRE ATT&CK tactical stages
- **Key Features**:
  - 11 tactical stage definitions (TA0001-TA0011)
  - Extended keyword lists for each stage (Initial Access, Execution, Persistence, etc.)
  - CVE classification workflow with confidence scoring
  - Multi-label classification support
  - Attack chain discovery methodology
- **Use Cases**:
  - Automated CVE categorization
  - Threat modeling and attack path analysis
  - Red team vulnerability selection
  - Blue team defensive prioritization
  - Threat intelligence enrichment

### 2. Software Ecosystem Relationships
- **Files**: `software_ecosystem_relationships.yaml` + `.md`
- **Severity**: Info
- **Description**: Software dependency and co-deployment relationship mapping for attack surface analysis
- **Key Features**:
  - Extended ecosystem mappings (Windows, Linux, Web, Database, Cloud, Container)
  - Technology stack definitions (LAMP, MEAN, MERN, Kubernetes)
  - Lateral movement path discovery
  - Cross-ecosystem bridge identification
  - Vulnerability propagation analysis
- **Use Cases**:
  - Lateral movement planning
  - Attack surface mapping
  - Vulnerability impact assessment
  - Red team reconnaissance
  - Blue team network segmentation
  - Supply chain risk analysis

### 3. Multi-Stage Attack Chain Modeling
- **Files**: `multi_stage_attack_chain_modeling.yaml` + `.md`
- **Severity**: Medium
- **Description**: Probabilistic framework for discovering and evaluating multi-stage attack chains
- **Key Features**:
  - Kill chain sequence modeling (Initial Access → Privilege Escalation → Persistence)
  - Probabilistic success scoring (multiplicative stage probabilities)
  - Chain complexity calculation
  - Red team attack planning workflows
  - Blue team defense prioritization
  - Patching impact analysis
- **Use Cases**:
  - Red team attack path planning
  - Threat modeling and risk assessment
  - Vulnerability patching prioritization
  - Purple team exercise design
  - Security architecture validation
  - Incident response prediction

## Optimization Enhancements

Compared to the original source code, the extracted knowledge includes:

### 1. **Extended Taxonomies**
- Original: 5 tactical stages
- Enhanced: 11 MITRE ATT&CK tactical stages with comprehensive keywords
- Added: Defense Evasion, Credential Access, Discovery, Collection, Impact

### 2. **Detailed Ecosystem Mappings**
- Original: 4 basic ecosystems (Windows, Linux, Web, Database)
- Enhanced: 15+ ecosystem categories including:
  - Cloud platforms (AWS, Azure, GCP)
  - Container orchestration (Kubernetes, Docker)
  - Development stacks (Java, Python, Ruby)
  - Enterprise suites (Microsoft 365, Google Workspace)
  - CI/CD pipelines

### 3. **Practical Workflows**
- Added: Complete Python implementation examples
- Added: Red team planning procedures
- Added: Blue team defense prioritization algorithms
- Added: Detection rules (Splunk, Sigma, Python)
- Added: Mitigation strategies with code examples

### 4. **Real-World Scenarios**
- Added: IIS compromise → Windows lateral movement example
- Added: LAMP stack attack chain scenario
- Added: Log4j vulnerability propagation analysis
- Added: Cross-ecosystem authentication detection

### 5. **Detection Engineering**
- Added: SIEM correlation rules for multi-stage attacks
- Added: Sigma rules for attack chain detection
- Added: Python-based event correlation logic
- Added: Behavioral analytics patterns

## MITRE ATT&CK Mapping

### Tactics Covered
- **TA0001** - Initial Access
- **TA0002** - Execution
- **TA0003** - Persistence
- **TA0004** - Privilege Escalation
- **TA0005** - Defense Evasion
- **TA0006** - Credential Access
- **TA0007** - Discovery
- **TA0008** - Lateral Movement
- **TA0009** - Collection
- **TA0010** - Exfiltration
- **TA0011** - Impact

### Techniques Referenced
- **T1190** - Exploit Public-Facing Application
- **T1210** - Exploitation of Remote Services
- **T1021** - Remote Services (SMB, RDP, SSH, WinRM)
- **T1078** - Valid Accounts
- **T1068** - Exploitation for Privilege Escalation
- **T1543** - Create or Modify System Process

## File Structure

Each knowledge item consists of:

### YAML File (Metadata)
- `name`: Machine-readable identifier
- `category`: tactical_analysis
- `description`: Concise functional summary
- `tags`: Keywords including MITRE ATT&CK techniques
- `severity`: info|low|medium|high|critical
- `prerequisites`: Required tools, permissions, knowledge
- `indicators`: IOC patterns for detection
- `detection`: Log sources and detection rules
- `mitigation`: Security controls and countermeasures
- `limitations`: Caveats and assumptions
- `references`: External documentation links
- `source`: Origin traceability (vul_correlators.py)
- `last_updated`: ISO8601 timestamp
- `related`: Links to related knowledge items

### Markdown File (Documentation)
- **Overview**: Purpose, category, severity, tags
- **Context and Use-Cases**: When and why to use
- **Key Parameters and Inputs**: Required configuration
- **Procedure**: Step-by-step methodology
- **Examples**: Complete code implementations and scenarios
- **Indicators / Detection**: Log sources, patterns, queries, Sigma rules
- **Mitigation Strategies**: Preventive, detective, and responsive controls
- **Limitations and Caveats**: Known constraints
- **Source Excerpts**: Verbatim code snippets with line references
- **References**: External resources and standards

## Integration with Exploitation Knowledge

These tactical analysis items complement the exploitation knowledge base:

```
Tactical Analysis (Strategic/Tactical)
    ↓
    ├─ Attack Chain Pattern Taxonomy
    │  └─ Identifies which exploits enable which tactical stages
    │
    ├─ Software Ecosystem Relationships
    │  └─ Maps which exploits are relevant for which platforms
    │
    └─ Multi-Stage Attack Chain Modeling
       └─ Chains individual exploits into complete attack paths

Exploitation Knowledge (Technical)
    ↓
    ├─ SQL Injection Exploit Generation
    ├─ XSS Exploit Generation
    ├─ RCE Exploit Generation
    └─ [Other exploit techniques]
```

## Usage Examples

### Red Team: Plan Attack Chain
```python
# 1. Use Attack Chain Pattern Taxonomy to classify available CVEs
cves = classify_cves_by_stage(target_cves, attack_patterns)

# 2. Use Software Ecosystem Relationships to identify lateral movement targets
lateral_targets = find_related_software(compromised_software, software_relationships)

# 3. Use Multi-Stage Attack Chain Modeling to build complete attack path
attack_chain = find_attack_chains(target, cves, max_depth=5)

# 4. Select highest probability chain and prepare exploits
selected_chain = attack_chain["attack_chains"][0]  # Highest probability
```

### Blue Team: Prioritize Defenses
```python
# 1. Analyze attack chains against your environment
chains = find_attack_chains(your_infrastructure, known_vulns)

# 2. Calculate patching impact
patching_priority = prioritize_defenses(chains)

# 3. Implement defense-in-depth per stage
for stage in ["initial_access", "privilege_escalation", "persistence"]:
    deploy_controls(stage, defense_in_depth_controls[stage])

# 4. Deploy detection rules
deploy_siem_rules(attack_chain_correlation_rules)
```

### Threat Intelligence: Enrich CVE Feeds
```python
# 1. Classify new CVEs by tactical stage
for cve in new_cves:
    stages = classify_cve(cve["description"], attack_patterns)
    cve["mitre_tactics"] = stages

# 2. Assess ecosystem impact
    affected_software = assess_ecosystem_impact(cve, software_relationships)
    cve["affected_ecosystem"] = affected_software

# 3. Calculate attack chain potential
    chain_potential = calculate_chain_potential(cve, existing_vulns)
    cve["chain_risk_score"] = chain_potential
```

## Extraction Metadata

- **Source**: `engine/knowledge/vul_correlators.py`
- **Extraction Prompt**: `docs/prompts/extract_cybersecurity_knowledge_prompt_v2.md`
- **Extraction Date**: 2025-11-07
- **Total Items**: 3 knowledge items (6 files: 3 YAML + 3 Markdown)
- **Total Size**: ~53KB
- **Enhancements**: Extended taxonomies, practical workflows, detection rules, real-world scenarios

## Related Knowledge

See also:
- `engine/handlers/knowledge/exploitation/` - Technical exploit generation knowledge
- `engine/handlers/knowledge/payloads/` - Payload templates and patterns
- `engine/knowledge/` - Original source code and templates
- `docs/prompts/` - Knowledge extraction guidelines

## Maintenance

When updating `vul_correlators.py`:
1. Re-run extraction using the v2 prompt template
2. Update `last_updated` timestamps in YAML files
3. Verify all source excerpt line numbers remain accurate
4. Update related knowledge item links if new items are added
5. Extend taxonomies with new MITRE ATT&CK techniques as they are published

## References

- **MITRE ATT&CK Framework** - https://attack.mitre.org/
- **Lockheed Martin Cyber Kill Chain** - https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html
- **NIST Cybersecurity Framework** - https://www.nist.gov/cyberframework
- **NIST SP 800-30 Rev. 1 - Risk Assessment** - https://csrc.nist.gov/publications/detail/sp/800-30/rev-1/final
- **CVE Program** - https://www.cve.org/
- **NVD - National Vulnerability Database** - https://nvd.nist.gov/
