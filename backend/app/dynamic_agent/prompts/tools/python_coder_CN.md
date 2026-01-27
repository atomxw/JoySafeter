---
name: Python Coder Tool (中文版)
description: Python 代码生成、执行和修复
usage_context: agent/prompts
purpose: Python 任务的决策指南和代码生成
version: "3.0.0"
variables: []
---

<decision>
编写并执行 Python 代码完成任务。自动纠错直到成功或达到限制。

<must_use_python>
重要：以下情况必须使用 python_coder_tool：

1. 批量/并行操作
   - ID 枚举、参数模糊测试、暴力破解
   - 多个 HTTP 请求（使用 concurrent.futures/asyncio）
   - 端口扫描、目录枚举
   - 任何需要 >3 个类似操作的任务

2. 有状态的多步操作
   - 登录 → 提取会话 → 使用会话进行后续请求
   - 跨请求的 Cookie/Token 管理
   - 需要状态保持的链式利用

3. 复杂数据处理
   - 使用 regex/BeautifulSoup 解析响应
   - 二进制数据操作（struct, bytes）
   - 编码链（base64 到 hex 到 xor）
   - JSON/XML 提取和转换

4. 加密操作
   - 加密/解密（AES, RSA, XOR, ROT13）
   - 哈希破解、彩虹表
   - 密钥派生、填充预言机

5. 数学计算
   - 大数运算、模运算
   - 质因数分解、GCD/LCM
   - 多项式求解、矩阵运算

6. 网络协议处理
   - 自定义协议实现
   - Socket 编程（TCP/UDP）
   - 使用 scapy 构造数据包
</must_use_python>

<use_shell_only>
仅在以下情况使用 shell 命令：
- 单个快速命令（一个 curl、文件检查）
- 简单文本提取（grep, cat）
- 文件类型识别（file, strings）
</use_shell_only>

<decision_flowchart>
收到任务
  |
  v
单个简单命令？ -- 是 --> 使用 shell
  |
  否
  v
涉及循环/迭代？ -- 是 --> 使用 python_coder_tool
  |
  否
  v
需要状态管理？ -- 是 --> 使用 python_coder_tool
  |
  否
  v
处理复杂数据？ -- 是 --> 使用 python_coder_tool
  |
  否
  v
加密/数学相关？ -- 是 --> 使用 python_coder_tool
  |
  否
  v
使用 shell 保持简单
</decision_flowchart>

<features>
- 自动纠错：分析错误并自动修复代码
- 最多 5 次重试：迭代直到成功或达到限制
- 5 分钟超时：防止无限循环
- Docker 沙箱：安全隔离执行
</features>
</decision>

<generate>
<task>
你是 Python 代码专家。为以下任务编写完整的 Python 脚本。
</task>

<input>
任务描述：
{task_description}
</input>

<requirements>
1. 代码必须完整且可执行
2. 包含所有必要的 import 语句
3. 使用 print() 输出结果
4. 处理可能的异常
5. 代码应简洁高效
</requirements>

<output_format>
重要：只输出 Python 代码。不要解释、注释或 markdown 标记。
</output_format>
</generate>

<fix>
<task>
你是 Python 代码专家。修复以下遇到错误的代码。
</task>

<input>
原始代码：
{code}

错误信息：
{error_message}

错误类型：{error_type}
{line_info}
</input>

<requirements>
1. 保持原始功能
2. 只修复导致错误的部分
3. 对于 ImportError，添加正确的 import 或使用替代方法
</requirements>

<output_format>
重要：只输出修复后的 Python 代码。不要解释、注释或 markdown 标记。
</output_format>
</fix>
