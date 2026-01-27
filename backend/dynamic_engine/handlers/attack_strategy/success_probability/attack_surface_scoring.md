# Attack Surface Scoring System

## Overview

- **Purpose**: Calculate quantified attack surface scores (0-10) based on target characteristics. Enables target prioritization and resource allocation.
- **Category**: tooling
- **Severity**: medium
- **Tags**: attack-surface, risk-scoring, vulnerability-assessment, target-analysis, decision-engine

## Context and Use-Cases

The attack surface scoring system is essential for:

- **Target Prioritization**: Rank targets by attack surface complexity
- **Resource Allocation**: Allocate testing resources based on score
- **Risk Assessment**: Quantify target risk for reporting
- **Scope Management**: Identify high-risk targets requiring attention
- **Trend Analysis**: Track attack surface changes over time
- **Comparative Analysis**: Compare targets within scope
- **Reporting**: Provide quantified metrics for stakeholders

## Procedure / Knowledge Detail

### Scoring Algorithm

The attack surface score is calculated using a multi-factor approach:

#### Base Score by Target Type

**Type-Specific Base Scores**:

- Web Application: 7.0 points
- Network Host: 8.0 points
- API Endpoint: 6.0 points
- Cloud Service: 5.0 points
- Binary File: 4.0 points
- Unknown: 3.0 points (default)

**Rationale**:

- Network hosts have highest base score (8.0) - direct network access
- Web applications have high score (7.0) - web-specific vulnerabilities
- API endpoints have moderate score (6.0) - limited attack surface
- Cloud services have lower score (5.0) - managed infrastructure
- Binary files have lowest score (4.0) - local analysis only

#### Technology Factor

**Calculation**:

- Points per technology: 0.5
- Formula: `score += len(profile.technologies) * 0.5`
- Maximum contribution: ~7.0 points (14 technologies)

**Rationale**:

- More technologies = larger attack surface
- Each technology introduces potential vulnerabilities
- Cumulative effect of technology stack

#### Port Factor

**Calculation**:

- Points per open port: 0.3
- Formula: `score += len(profile.open_ports) * 0.3`
- Maximum contribution: ~19.5 points (65,535 ports)

**Rationale**:

- More open ports = more services = larger attack surface
- Each port represents potential entry point
- Service enumeration increases complexity

#### Subdomain Factor

**Calculation**:

- Points per subdomain: 0.2
- Formula: `score += len(profile.subdomains) * 0.2`
- Maximum contribution: ~10.0 points (50 subdomains)

**Rationale**:

- More subdomains = distributed infrastructure
- Each subdomain represents potential target
- Increases reconnaissance scope

#### CMS Factor

**Calculation**:

- Fixed bonus if CMS detected: 1.5 points
- Formula: `if profile.cms_type: score += 1.5`

**Rationale**:

- CMS platforms have known vulnerabilities
- Plugin/theme ecosystem increases attack surface
- CMS-specific exploitation techniques available

### Score Normalization

**Capping**:

- Maximum score: 10.0 (capped)
- Formula: `return min(score, 10.0)`

**Rationale**:

- Standardized scale (0-10) for consistency
- Prevents extreme scores from skewing analysis
- Enables comparison across different targets

## Scoring Examples

### Example 1: Simple Web Application

```python
profile = TargetProfile(
    target="example.com",
    target_type=TargetType.WEB_APPLICATION,
    technologies=[TechnologyStack.PHP],
    open_ports=[80, 443],
    subdomains=[],
    cms_type=None
)

# Calculation:
# Base score (WEB_APPLICATION): 7.0
# Technologies (1 * 0.5): 0.5
# Open ports (2 * 0.3): 0.6
# Subdomains (0 * 0.2): 0.0
# CMS bonus: 0.0
# Total: 7.0 + 0.5 + 0.6 + 0.0 + 0.0 = 8.1
# Result: 8.1
```

### Example 2: WordPress Site

```python
profile = TargetProfile(
    target="blog.example.com",
    target_type=TargetType.WEB_APPLICATION,
    technologies=[TechnologyStack.WORDPRESS, TechnologyStack.PHP],
    open_ports=[80, 443],
    subdomains=["blog", "api", "admin"],
    cms_type="WordPress"
)

# Calculation:
# Base score (WEB_APPLICATION): 7.0
# Technologies (2 * 0.5): 1.0
# Open ports (2 * 0.3): 0.6
# Subdomains (3 * 0.2): 0.6
# CMS bonus: 1.5
# Total: 7.0 + 1.0 + 0.6 + 0.6 + 1.5 = 10.7
# Capped: min(10.7, 10.0) = 10.0
# Result: 10.0 (maximum)
```

### Example 3: Network Host

```python
profile = TargetProfile(
    target="192.168.1.100",
    target_type=TargetType.NETWORK_HOST,
    technologies=[TechnologyStack.APACHE, TechnologyStack.PHP, TechnologyStack.MYSQL],
    open_ports=[22, 80, 443, 3306, 8080],
    subdomains=[],
    cms_type=None
)

# Calculation:
# Base score (NETWORK_HOST): 8.0
# Technologies (3 * 0.5): 1.5
# Open ports (5 * 0.3): 1.5
# Subdomains (0 * 0.2): 0.0
# CMS bonus: 0.0
# Total: 8.0 + 1.5 + 1.5 + 0.0 + 0.0 = 11.0
# Capped: min(11.0, 10.0) = 10.0
# Result: 10.0 (maximum)
```

### Example 4: API Endpoint

```python
profile = TargetProfile(
    target="api.example.com/v1",
    target_type=TargetType.API_ENDPOINT,
    technologies=[TechnologyStack.NODEJS],
    open_ports=[443],
    subdomains=[],
    cms_type=None
)

# Calculation:
# Base score (API_ENDPOINT): 6.0
# Technologies (1 * 0.5): 0.5
# Open ports (1 * 0.3): 0.3
# Subdomains (0 * 0.2): 0.0
# CMS bonus: 0.0
# Total: 6.0 + 0.5 + 0.3 + 0.0 + 0.0 = 6.8
# Result: 6.8
```

## Score Interpretation

| Score Range | Risk Level | Interpretation |
|-------------|-----------|-----------------|
| 0.0 - 2.0 | Minimal | Very limited attack surface |
| 2.0 - 4.0 | Low | Small attack surface |
| 4.0 - 6.0 | Medium | Moderate attack surface |
| 6.0 - 8.0 | High | Large attack surface |
| 8.0 - 10.0 | Critical | Very large attack surface |

## Related Knowledge Items

- **target_type_classification**: Provides base score by target type
- **technology_detection_heuristics**: Contributes technology count
- **cms_detection_system**: Triggers CMS bonus
- **determine_risk_level**: Uses score for risk classification

## Best Practices

1. **Regular Updates**: Recalculate scores as target changes
2. **Threshold Tuning**: Adjust weights based on organization needs
3. **Comparative Analysis**: Use scores to compare targets
4. **Trend Tracking**: Monitor score changes over time
5. **Documentation**: Document scoring rationale
6. **Validation**: Validate scores against actual findings
7. **Feedback Loop**: Adjust weights based on results
8. **Reporting**: Include scores in security reports

## Limitations and Considerations

### Current Limitations

- **Static Weights**: Fixed point values don't adapt to context
- **No Temporal Data**: Doesn't consider historical changes
- **Limited Factors**: Only considers 5 factors
- **No Severity Weighting**: All factors weighted equally
- **No Exploit Availability**: Doesn't consider known exploits
- **No Patch Status**: Doesn't consider patch levels
- **No Threat Intelligence**: Doesn't incorporate threat data
- **No Custom Weights**: Weights cannot be customized

### Improvement Opportunities

1. **Dynamic Weights**: Adjust weights based on context
2. **Temporal Analysis**: Track score changes over time
3. **Additional Factors**: Include patch status, exploit availability
4. **Threat Intelligence**: Incorporate threat data
5. **Custom Weights**: Allow organization-specific weighting
6. **Confidence Scoring**: Return confidence in score
7. **Sensitivity Analysis**: Show impact of each factor
8. **Machine Learning**: Train models for better scoring

## Performance Metrics

| Metric | Value |
|--------|-------|
| Calculation Latency | <1ms |
| Accuracy | Depends on input data |
| Score Range | 0.0 - 10.0 |
| Maximum Factors | 5 |
| Customization | Limited |

## Notes

- Scores are normalized to 0-10 scale for consistency
- Higher scores indicate larger attack surfaces
- Scores should be used for prioritization, not absolute risk
- Actual risk depends on many factors not captured in score
- Regular validation against real findings is recommended
- Weights may need adjustment for specific environments

## Integration Points

**Called By**:

- `analyze_target()` - Main target analysis workflow
- Target profile enrichment pipeline
- Risk assessment and reporting

**Calls**:

- Arithmetic operations (built-in Python)
- TargetProfile data access

**Data Flow**:

```text
TargetProfile (with characteristics)
    ↓
[Base Score by Type]
    ↓
[Add Technology Factor]
    ↓
[Add Port Factor]
    ↓
[Add Subdomain Factor]
    ↓
[Add CMS Factor]
    ↓
[Normalize to 0-10]
    ↓
Output (Attack Surface Score)
```

## Future Enhancements

1. **Dynamic Weighting**: Adjust weights based on threat landscape
2. **Temporal Analysis**: Track score trends
3. **Exploit Availability**: Incorporate known exploits
4. **Patch Status**: Consider patch levels
5. **Threat Intelligence**: Use threat data
6. **Custom Weights**: Allow user-defined weights
7. **Confidence Scoring**: Return confidence levels
8. **Machine Learning**: Train models for improved accuracy
