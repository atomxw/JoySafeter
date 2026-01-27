# Codes 目录

## 概述

`codes` 目录包含可复用的库与模块，这些模块独立于具体实验，供 `evals/` 与子模块调用。

## 目录结构

```
codes/
├── api/                    # API 服务
│   └── services/          # 服务实现
│       └── pi_scanner_service.py
├── configs/               # 配置模板（YAML/JSON）
│   ├── default.yaml       # 默认配置文件
│   └── initial_scan/      # 初始扫描配置
├── pipeline/              # 流水线编排
│   ├── __init__.py
│   └── orchestrator.py    # 扫描任务编排器
└── scanner/               # 核心扫描模块
    ├── __init__.py
    ├── data_types.py      # 核心领域模型
    ├── input_resolver.py  # 输入路径解析
    ├── output_resolver.py # 输出格式化
    ├── initial_scan/      # 初始扫描阶段
    │   ├── llm_scanner.py      # 基于大模型的源文件审阅
    │   ├── pm_scanner.py       # 模式匹配扫描器（Semgrep）
    │   ├── pi_scanner.py       # 提示词注入扫描器
    │   ├── finding_filter.py   # 发现项过滤和验证
    │   └── dedup.py            # 发现项去重
    └── deep_analysis/     # 深度分析阶段
        ├── agent_orchestrator.py  # Agent 协同逻辑
        ├── cpg_builder.py         # CPG 构建与管理
        └── sub_agent.py           # 子 Agent 实现
```

## 核心组件

### Scanner 模块

Scanner 模块提供代码安全扫描的核心功能：

- **初始扫描**：使用多种方法进行初始安全分析：
  - **LLM 扫描器**：使用大语言模型审阅源代码文件，查找安全漏洞
  - **模式匹配扫描器**：使用 Semgrep 进行基于模式的静态分析
  - **提示词注入扫描器**：检测 JSON Schema 描述字段中的提示词注入风险

- **深度分析**：使用以下方法进行高级分析：
  - **CPG 构建器**：构建代码属性图（Code Property Graph）进行更深入的代码分析
  - **Agent 编排器**：协调多个 Agent 进行全面的安全审查

### Pipeline 模块

Pipeline 模块编排整个扫描工作流：

- **编排器**：管理端到端的扫描过程
- **配置**：支持灵活的扫描策略、去重、过滤和输出格式化

### API 模块

为扫描功能提供 RESTful API 服务：

- **PI 扫描器服务**：用于提示词注入检测的独立服务

## 配置说明

在使用模块之前，需要在 `configs/default.yaml` 中配置以下信息：

### LLM 配置

配置用于代码审阅的 LLM 设置：

```yaml
llm:
  api_key: YOUR_API_KEY_HERE
  model_name: Qwen3-Coder
  max_workers: 16
  base_url: YOUR_BASE_URL_HERE
  max_requests_per_minute: 2000
```

**配置字段：**
- `api_key`: 你的 API 密钥（例如：`pk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）
- `base_url`: API 基础 URL（例如：`https://api.openai.com/v1`）
- `model_name`: 用于代码审阅的模型名称
- `max_workers`: 最大并发工作线程数
- `max_requests_per_minute`: API 请求的速率限制

### PI Scanner 配置

提示词注入扫描器用于检测 JSON Schema 描述字段中的安全风险。

```yaml
pi_scanner:
  api_key: YOUR_API_KEY_HERE
  base_url: YOUR_BASE_URL_HERE
  model: YOUR_MODEL_NAME_HERE
```

**配置字段：**
- `api_key`: 你的 API 密钥（可以与 LLM 配置相同或不同）
- `base_url`: API 基础 URL（例如：`https://api.openai.com/v1` 或兼容 OpenAI API 的网关地址）
- `model`: 模型名称（例如：`gpt-4` 或 `Qwen3Guard-Gen-8B`）

### CPG 配置

配置代码属性图设置：

```yaml
cpg:
  backend: joern
  reuse_cache: true
  max_graph_nodes: 2000000
  executable_path: /usr/local/bin/joern
```

### 报告配置

配置输出报告设置：

```yaml
report:
  formats:
    - cli
    - json
    - markdown
  output_dir: ./reports
  severity_threshold: low
```

## 使用示例

### 基础扫描

```python
from scanner import resolve_scan_context
from scanner.initial_scan import OpenAILLMScanner, LocalPMScanner
from scanner.output_resolver import simple_output

# 解析扫描上下文
context = resolve_scan_context(
    path="/path/to/code",
    auto_detect_languages=True
)

# 运行 LLM 扫描器
llm_scanner = OpenAILLMScanner()
findings = list(llm_scanner.scan(context))

# 运行模式匹配扫描器
pm_scanner = LocalPMScanner()
pm_findings = list(pm_scanner.scan(context))

# 输出结果
all_findings = list(findings) + list(pm_findings)
simple_output(all_findings)
```

### 使用流水线编排器

```python
from pipeline.orchestrator import DefaultOrchestrator, PipelineConfig
from scanner.data_types import ScanStrategyConfig

# 配置流水线
config = PipelineConfig(
    jobs=8,
    scan_strategy=ScanStrategyConfig(
        enable_pm=True,
        enable_llm=True
    )
)

# 创建编排器
orchestrator = DefaultOrchestrator(config)

# 运行端到端扫描
results = orchestrator.scan("/path/to/code")
```

### 提示词注入扫描

```python
from api.services.pi_scanner_service import scan_schema_json
import json

# 示例 JSON Schema
schema = {
    "type": "object",
    "properties": {
        "param": {
            "description": "用户输入参数",
            "type": "string"
        }
    }
}

# 扫描提示词注入风险
result = await scan_schema_json(json.dumps(schema))
print(result)
```

## API 服务器

启动 API 服务器：

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

API 提供以下端点：
- 提示词注入扫描
- 代码安全分析
- 报告生成

## 主要特性

- **多方法扫描**：结合基于 LLM 的分析、模式匹配和专用扫描器
- **灵活配置**：基于 YAML 的配置，提供合理的默认值
- **可扩展架构**：易于添加新的扫描器和分析方法
- **全面过滤**：内置过滤和去重功能
- **多种输出格式**：支持 CLI、JSON 和 Markdown 输出格式

## 依赖项

主要依赖包括：
- `openai`: 用于 LLM API 交互
- `pyyaml`: 用于配置文件解析
- `semgrep`: 用于模式匹配（可选，如果使用 PM 扫描器）

## 许可证

详细信息请参阅主项目的 LICENSE 文件。
