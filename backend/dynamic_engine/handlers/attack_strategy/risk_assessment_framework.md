# Risk Assessment Framework

## Overview

- **Purpose**: Comprehensive risk assessment combining quantified attack surface scores with categorical risk classifications. Enables data-driven target prioritization and resource allocation.
- **Category**: tooling
- **Severity**: high
- **Tags**: risk-assessment, attack-surface, risk-scoring, vulnerability-assessment, target-analysis, decision-engine, prioritization

## Context and Use-Cases

The risk assessment framework is essential for:

- **Target Prioritization**: Rank targets by quantified risk scores
- **Resource Allocation**: Allocate testing resources based on risk level
- **Risk Reporting**: Provide quantified and categorical risk metrics
- **Scope Management**: Identify critical targets requiring immediate attention
- **Trend Analysis**: Track risk changes over time
- **Comparative Analysis**: Compare targets within scope
- **Executive Reporting**: Communicate risk in business terms
- **Compliance**: Document risk assessment methodology

## Procedure / Knowledge Detail

### Two-Tier Risk Assessment System

The framework combines two complementary approaches:

#### Tier 1: Attack Surface Scoring (Quantitative)

**Scoring Algorithm**:

Calculates numerical score (0-10) based on target characteristics:

**Base Score by Target Type**:

- Web Application: 7.0
- Network Host: 8.0
- API Endpoint: 6.0
- Cloud Service: 5.0
- Binary File: 4.0
- Unknown: 3.0 (default)

**Additional Factors**:

- Technology count: +0.5 per technology
- Open ports: +0.3 per port
- Subdomains: +0.2 per subdomain
- CMS presence: +1.5 (if detected)

**Normalization**:

- Maximum score: 10.0 (capped)
- Formula: `min(base_score + factors, 10.0)`

#### Tier 2: Risk Level Classification (Categorical)

**Risk Classification Thresholds**:

| Score Range | Risk Level | Description |
|-------------|-----------|-------------|
| 8.0 - 10.0 | Critical | Immediate action required |
| 6.0 - 7.9 | High | Significant risk, prioritize testing |
| 4.0 - 5.9 | Medium | Moderate risk, standard testing |
| 2.0 - 3.9 | Low | Limited risk, basic testing |
| 0.0 - 1.9 | Minimal | Negligible risk, minimal testing |

**Classification Logic**:

```text
if score >= 8.0:
    return "critical"
elif score >= 6.0:
    return "high"
elif score >= 4.0:
    return "medium"
elif score >= 2.0:
    return "low"
else:
    return "minimal"
```

### Integrated Assessment Workflow

**Step 1: Collect Target Characteristics**:

- Target type (URL, IP, domain, binary)
- Detected technologies
- Open ports and services
- Subdomains and infrastructure
- CMS platform (if applicable)

**Step 2: Calculate Attack Surface Score**:

- Apply base score for target type
- Add points for each technology
- Add points for each open port
- Add points for each subdomain
- Add CMS bonus if applicable
- Normalize to 0-10 scale

**Step 3: Classify Risk Level**:

- Compare score against thresholds
- Assign categorical risk level
- Map to testing strategy

**Step 4: Generate Assessment Report**:

- Quantified attack surface score
- Categorical risk level
- Contributing factors
- Recommended actions
