---
name: Knowledge Search Tool (中文版)
description: 搜索 CTF 知识库获取解题技巧
usage_context: agent/prompts
purpose: 指导代理何时以及如何使用知识搜索
version: "3.0.0"
variables: []
---

<knowledge_search>
搜索 CTF 知识库获取解题技巧。

<when>
- 基础方法失败
- 需要 WAF/过滤器绕过
- 卡在特定漏洞上
</when>

<queries>
好的查询：
- "Flask SSTI {{ }} filtered bypass"
- "IDOR ID range 1-100 nothing found"
- "SQL injection union blocked"

坏的查询：
- "how to solve this"（太宽泛）
- "help"（没有具体信息）
</queries>

<using_results>
结果来自类似挑战，不是这个具体挑战！
- 将技巧适配到当前上下文（不同的 URL、参数等）
- 不要盲目复制 payload - 先理解原理
- 结果保留在上下文中 - 需要时可以回顾
</using_results>

<rule>
先尝试基础方法。包含你已经尝试过的内容。
</rule>
</knowledge_search>
