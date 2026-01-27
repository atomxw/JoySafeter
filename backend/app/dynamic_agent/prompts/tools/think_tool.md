---
name: Think Tool
description: Tool for explicit structured reasoning
usage_context: agent/prompts
purpose: Guide structured reasoning and task analysis
version: "3.0.0"
variables: []
---

<think_tool>
Structured reasoning. No actions, no state changes.

<when>
- Complex/ambiguous task
- Unexpected results or errors
- Planning next steps
</when>

<structure>
1. **What happened** - Current situation
2. **What it means** - Interpretation
3. **What next** - Decision
</structure>


<rule>
Do NOT overthink. Think → Act → Observe → Repeat.
</rule>
</think_tool>
