# Confidence Scoring System

## Overview

- **Purpose**: Quantify the reliability and completeness of target analysis through incremental scoring. Enables data-driven confidence assessment for attack planning.
- **Category**: tooling
- **Severity**: medium
- **Tags**: confidence-scoring, target-analysis, data-quality, reliability-assessment, decision-engine, probabilistic-analysis

## Context and Use-Cases

The confidence scoring system is essential for:

- **Analysis Reliability**: Measure how confident we are in reconnaissance findings
- **Probability Adjustment**: Scale success probabilities based on data quality
- **Resource Prioritization**: Focus additional reconnaissance on low-confidence targets
- **Decision Making**: Inform strategy selection based on information completeness
- **Risk Assessment**: Adjust risk calculations based on analysis certainty
- **Reporting**: Communicate analysis reliability to stakeholders
- **Reconnaissance Planning**: Identify gaps in target information
- **Contingency Planning**: Prepare alternatives for uncertain scenarios

## Procedure / Knowledge Detail

### Confidence Scoring Algorithm

**Base Confidence**: 0.5 (50% - neutral starting point)

**Incremental Scoring**:

Each data point adds confidence based on its significance:

#### 1. IP Address Resolution (+0.1)

**Trigger**: `if profile.ip_addresses:`

**Significance**:

- Confirms target is resolvable
- Enables network-level testing
- Validates domain/hostname accuracy
- Prerequisite for many tools

**Rationale**: 10% increase for having resolved IP addresses

#### 2. Technology Detection (+0.2)

**Trigger**: `if profile.technologies and profile.technologies[0] != TechnologyStack.UNKNOWN:`

**Significance**:

- Identifies technology stack
- Enables technology-specific tools
- Highest confidence impact
- Guides exploitation strategy

**Rationale**: 20% increase (highest) for confirmed technologies

#### 3. CMS Detection (+0.1)

**Trigger**: `if profile.cms_type:`

**Significance**:

- Identifies CMS platform
- Enables CMS-specific testing
- Indicates web application
- Guides plugin/theme enumeration

**Rationale**: 10% increase for CMS identification

#### 4. Target Type Classification (+0.1)

**Trigger**: `if profile.target_type != TargetType.UNKNOWN:`

**Significance**:

- Confirms target categorization
- Enables type-specific tools
- Guides tool selection
- Informs attack strategy

**Rationale**: 10% increase for confirmed target type

### Confidence Score Ranges

**Interpretation**:


| Score | Range | Interpretation | Recommendation |
|---|---|---|---|
| 0.5 | 50% | Minimal Data | Gather more reconnaissance |
| 0.6 | 60% | Limited Data | Proceed with caution |
| 0.7 | 70% | Moderate Data | Proceed with confidence |
| 0.8 | 80% | Good Data | Proceed with high confidence |
| 0.9 | 90% | Excellent Data | Execute optimally |
| 1.0 | 100% | Complete Data | Maximum confidence |

### Confidence Impact on Success Probability

**Relationship**:

```text
Step Success Probability = Tool Effectiveness × Confidence Score
```

**Example Impact**:

| Confidence | Tool Effectiveness | Step Success | Impact |
|---|---|---|---|
| 0.50 | 0.90 | 0.45 | Low |
| 0.60 | 0.90 | 0.54 | Moderate |
| 0.70 | 0.90 | 0.63 | Good |
| 0.80 | 0.90 | 0.72 | High |
| 0.90 | 0.90 | 0.81 | Very High |
| 1.00 | 0.90 | 0.90 | Maximum |

**Key Insight**: 50% confidence reduction = 50% success probability reduction
