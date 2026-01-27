# Multi-Cloud Assessment

## Overview

- **Purpose**: Cross-cloud security evaluation
- **Category**: attack-pattern
- **Severity**: high
- **Target Types**: Cloud Services
- **Execution Time**: 60 minutes
- **Aggressiveness**: Low

## Context and Use-Cases

- **Multi-cloud auditing**: Comprehensive cross-cloud assessment
- **Misconfiguration detection**: Find misconfigurations across clouds
- **Compliance verification**: Verify compliance across platforms
- **Security posture**: Overall multi-cloud security
- **Infrastructure assessment**: Complete infrastructure evaluation

## Procedure / Knowledge Detail

### Tool Sequence (4 tools)

1. **scout-suite** - Multi-cloud scanning
2. **prowler** - AWS auditing
3. **checkov** - IaC scanning
4. **terrascan** - Terraform analysis

## Expected Outputs

- Multi-cloud security findings
- Misconfiguration reports
- Compliance status across clouds
- Security recommendations
- Risk assessment
- Remediation guidance

## Related Knowledge Items

- aws_security_assessment
- kubernetes_security_assessment
- container_security_assessment
- iac_security_assessment

## Best Practices

1. Start with scout-suite for multi-cloud overview
2. Use prowler for AWS-specific assessment
3. Run checkov for IaC scanning
4. Use terrascan for Terraform analysis
5. Document all findings
6. Prioritize by severity
7. Create unified remediation plan
8. Monitor continuously

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total Tools | 4 |
| Estimated Time | 60 minutes |
| Aggressiveness | Low |
| Detection Risk | Low |
| Coverage | Very High |
| Accuracy | 85-90% |

## Notes

- Requires access to multiple cloud platforms
- Combines multiple cloud-specific assessments
- Results depend on cloud configuration complexity
- Compliance standards vary by cloud provider
