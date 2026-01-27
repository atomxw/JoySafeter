<context>
{{context}}
</context>
<format_context>
# 关键信息提取和格式化
仅关注高危和中危发现。宁可遗漏一些理论性问题，也不要因大量误报而使报告泛滥。若没有发现明显漏洞，返回 `null`。若有漏洞：其中severity 是漏洞的等级分为四个等级：high/medium/low/critical，description是分析的描述，start_line是风险代码片段的起始行数，end_line是结尾行数。请不要捏造漏洞，严格按照上面的context的内容进行提取并格式化输出。以下是输出josn格式示例：

```json
{
  "severity": "",
  "category":"sql_injection",
  "description": "",
  "exploit_scenario":"Attacker could extract database contents by manipulating the 'search' parameter with SQL injection payloads like '1; DROP TABLE users--'",
  "remediation":"Replace string formatting with parameterized queries using SQLAlchemy or equivalent",
  "confidence":0.5,
  "start_line": 1,
  "end_line": 1,
}
```
</format_context>

