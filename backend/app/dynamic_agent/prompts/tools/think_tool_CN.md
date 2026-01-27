---
name: Think Tool (中文版)
description: 显式结构化推理工具
usage_context: agent/prompts
purpose: 指导结构化推理和任务分析
version: "3.0.0"
variables: []
---

<think_tool>
结构化推理。无操作，无状态变更。

<when>
- 复杂/模糊的任务
- 意外结果或错误
- 规划下一步
</when>

<structure>
1. **发生了什么** - 当前情况
2. **意味着什么** - 解读
3. **下一步做什么** - 决策
</structure>

<rule>
不要过度思考。思考 → 行动 → 观察 → 重复。
</rule>
</think_tool>
