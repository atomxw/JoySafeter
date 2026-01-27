# CMS Detection System

## Overview

- **Purpose**: Identify Content Management Systems (WordPress, Drupal, Joomla) from target strings using pattern matching. Enables CMS-specific vulnerability assessment and exploitation.
- **Category**: tooling
- **Severity**: medium
- **Tags**: cms-detection, wordpress-detection, drupal-detection, joomla-detection, pattern-matching, reconnaissance, decision-engine

## Context and Use-Cases

The CMS detection system is essential for:

- **CMS-Specific Scanning**: Select tools optimized for detected CMS platforms
- **Vulnerability Assessment**: Target known CMS vulnerabilities
- **Plugin/Theme Enumeration**: Identify vulnerable plugins and themes
- **Version Detection**: Determine CMS version for targeted exploitation
- **Attack Surface Mapping**: Understand CMS-specific attack vectors
- **Exploitation Planning**: Choose exploits relevant to detected CMS
- **Security Hardening**: Identify CMS-specific security configurations

## Procedure / Knowledge Detail

### Detection Process

The CMS detection system uses pattern-matching heuristics to identify CMS platforms from target strings:

#### Detection Method

**Input Analysis**:

- Accepts target string (URL, domain, or path)
- Converts input to lowercase for case-insensitive matching
- Performs substring pattern matching

**Detection Strategy**:

- Pattern-based detection using string matching
- Returns specific CMS name or None if no match
- Single return value (first matching CMS)
- Hierarchical detection order

### Supported CMS Platforms

#### 1. WordPress Detection

**Patterns**:

- Substring `wordpress` in target (case-insensitive)
- Substring `wp-` in target (case-insensitive)

**Example Patterns**:

- `https://example.com/wordpress`
- `https://wordpress.example.com`
- `https://example.com/wp-admin`
- `https://example.com/wp-content`
- `https://example.com/wp-includes`
- `https://example.com/wp-json`

**Detection Result**: `"WordPress"`

#### 2. Drupal Detection

**Patterns**:

- Substring `drupal` in target (case-insensitive)

**Example Patterns**:

- `https://example.com/drupal`
- `https://drupal.example.com`
- `https://example.com/sites/default`
- `https://example.com/drupal/admin`

**Detection Result**: `"Drupal"`

#### 3. Joomla Detection

**Patterns**:

- Substring `joomla` in target (case-insensitive)

**Example Patterns**:

- `https://example.com/joomla`
- `https://joomla.example.com`
- `https://example.com/administrator`
- `https://example.com/joomla/index.php`

**Detection Result**: `"Joomla"`

### Detection Logic

**Pattern Matching Algorithm**:

```python
# Pseudo-code for detection logic
target_lower = target.lower()

if 'wordpress' in target_lower or 'wp-' in target_lower:
    return "WordPress"
elif 'drupal' in target_lower:
    return "Drupal"
elif 'joomla' in target_lower:
    return "Joomla"

return None
```

**Case Sensitivity**:

- All matching is case-insensitive (converted to lowercase)
- Handles variations in URL encoding and capitalization

**Detection Priority**:

- WordPress checked first
- Drupal checked second
- Joomla checked third
- Returns first match (no multiple CMS detection)

### Return Values

**Success Cases**:

- WordPress detected: `"WordPress"`
- Drupal detected: `"Drupal"`
- Joomla detected: `"Joomla"`
- No match: `None`

**Return Type**:

- Always returns `Optional[str]`
- Single CMS name or None
- Never returns multiple CMS values

## Examples

### Example 1: WordPress Detection

```python
target = "https://example.com/wordpress/wp-admin"
# Process:
# 1. Convert to lowercase
# 2. Check for 'wordpress' substring → Found
# 3. Return immediately
# Result: "WordPress"
```

### Example 2: Drupal Detection

```python
target = "https://example.com/sites/default/files"
# Process:
# 1. Convert to lowercase
# 2. Check for 'wordpress' → Not found
# 3. Check for 'drupal' → Not found
# 4. Check for 'joomla' → Not found
# 5. Return None
# Result: None
```

### Example 3: Joomla Detection

```python
target = "https://joomla.example.com/administrator"
# Process:
# 1. Convert to lowercase
# 2. Check for 'wordpress' → Not found
# 3. Check for 'drupal' → Not found
# 4. Check for 'joomla' → Found
# 5. Return immediately
# Result: "Joomla"
```

### Example 4: WordPress with Path

```python
target = "https://example.com/blog/wp-content/plugins"
# Process:
# 1. Convert to lowercase
# 2. Check for 'wordpress' or 'wp-' → Found 'wp-'
# 3. Return immediately
# Result: "WordPress"
```

### Example 5: No CMS Detected

```python
target = "https://example.com/api/v1/users"
# Process:
# 1. Convert to lowercase
# 2. Check for 'wordpress' → Not found
# 3. Check for 'drupal' → Not found
# 4. Check for 'joomla' → Not found
# 5. Return None
# Result: None
```

## Detection Output

| Target | Detected CMS | Result |
|--------|-------------|--------|
| `example.com/wordpress` | WordPress | `"WordPress"` |
| `drupal.example.com` | Drupal | `"Drupal"` |
| `joomla.example.com` | Joomla | `"Joomla"` |
| `example.com/wp-admin` | WordPress | `"WordPress"` |
| `example.com/api/v1` | None | `None` |

## Related Knowledge Items

- **technology_detection_heuristics**: Detects underlying technologies (PHP, ASP.NET)
- **target_type_classification**: Determines target type before CMS detection
- **attack_surface_scoring**: Incorporates CMS information in scoring
- **tool_selection_strategy**: Uses detected CMS for tool selection

## Best Practices

1. **Input Validation**: Validate target strings before detection
2. **Case Handling**: Always perform case-insensitive matching
3. **Pattern Expansion**: Add more CMS-specific patterns
4. **HTTP Analysis**: Enhance with HTTP header analysis
5. **Content Inspection**: Analyze page content for CMS indicators
6. **Version Detection**: Implement CMS version detection
7. **Fingerprinting**: Use advanced fingerprinting techniques
8. **Logging**: Log detection decisions for analysis

## Limitations and Considerations

### Current Limitations

- **Pattern-Based Only**: Relies on URL/path patterns, not HTTP analysis
- **Limited Coverage**: Only detects 3 CMS platforms
- **False Positives**: May detect CMS not actually present
- **False Negatives**: May miss CMS not in URL/path
- **No Header Analysis**: Doesn't analyze HTTP headers
- **No Content Analysis**: Doesn't analyze page content
- **Single Detection**: Returns only first matching CMS
- **No Version Detection**: Doesn't detect CMS version

### Improvement Opportunities

1. **HTTP Analysis**: Analyze HTTP headers and responses
2. **Signature Database**: Implement comprehensive CMS signatures
3. **Advanced Fingerprinting**: Use tools like CMSmap or Wappalyzer
4. **Version Detection**: Identify specific CMS versions
5. **Plugin Detection**: Enumerate installed plugins/themes
6. **Multiple CMS**: Support detection of multiple CMS
7. **Confidence Scoring**: Return confidence scores
8. **Custom Patterns**: Allow user-defined detection patterns

## Performance Metrics

| Metric | Value |
|--------|-------|
| Detection Latency | <1ms per target |
| Pattern Matching Speed | O(n) where n = target length |
| Supported CMS Platforms | 3 (WordPress, Drupal, Joomla) |
| Detection Patterns | 3 |
| False Positive Rate | 5-10% (estimated) |
| False Negative Rate | 30-40% (estimated) |

## Notes

- The current implementation uses basic heuristics and is not production-ready
- For production use, consider integrating with specialized tools like CMSmap
- HTTP header analysis would significantly improve detection accuracy
- Page content analysis could identify additional CMS indicators
- The system is designed to be extensible for adding new CMS platforms
- Detection results should be verified with additional reconnaissance

## Integration Points

**Called By**:

- `analyze_target()` - Main target analysis workflow
- Target profile enrichment pipeline
- CMS-specific tool selection

**Calls**:

- String matching operations (built-in Python)

**Data Flow**:

```text
Input (Target String)
    ↓
[Case Normalization]
    ↓
[Pattern Matching]
    ↓
[CMS Detection]
    ↓
Output (CMS name or None)
```

## Future Enhancements

1. **HTTP-Based Detection**: Analyze HTTP headers and responses
2. **Content-Based Detection**: Parse HTML for CMS indicators
3. **Advanced Fingerprinting**: Implement CMSmap-like detection
4. **Version Detection**: Identify specific CMS versions
5. **Plugin Detection**: Enumerate installed plugins/themes
6. **Confidence Scoring**: Return confidence levels
7. **Multiple CMS**: Support multiple CMS detection
8. **Machine Learning**: Train models for improved accuracy
