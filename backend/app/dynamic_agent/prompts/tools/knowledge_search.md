---
name: Knowledge Search Tool
description: Search CTF knowledge base for solving tricks
usage_context: agent/prompts
purpose: Guide agent on when and how to use knowledge search
version: "3.0.0"
variables: []
---

<knowledge_search>
Search CTF knowledge base for challenge-solving tricks.

<when>
- Basic methods failed
- WAF/filter bypass needed
- Stuck on specific vulnerability
</when>

<queries>
Good:
- "Flask SSTI {{ }} filtered bypass"
- "IDOR ID range 1-100 nothing found"
- "SQL injection union blocked"

Bad:
- "how to solve this" (too broad)
- "help" (no specifics)
</queries>

<using_results>
Results are from SIMILAR challenges, not this exact one!
- Adapt tricks to current context (different URL, params, etc.)
- Don't blindly copy payloads - understand the principle first
- Results stay in context - refer back when needed
</using_results>

<rule>
Try basic methods first. Include what you've tried.
</rule>
</knowledge_search>
