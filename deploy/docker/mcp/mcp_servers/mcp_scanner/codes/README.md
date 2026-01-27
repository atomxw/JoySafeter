# Codes Directory

## Overview

The `codes` directory contains reusable libraries and modules that are independent of specific experiments. These modules are designed to be called by `evals/` and other submodules.

## Directory Structure

```
codes/
├── api/                    # API services
│   └── services/          # Service implementations
│       └── pi_scanner_service.py
├── configs/               # Configuration templates (YAML/JSON)
│   ├── default.yaml       # Default configuration file
│   └── initial_scan/      # Initial scan configurations
├── pipeline/              # Pipeline orchestration
│   ├── __init__.py
│   └── orchestrator.py    # Scan task orchestrator
└── scanner/               # Core scanning modules
    ├── __init__.py
    ├── data_types.py      # Core domain models
    ├── input_resolver.py  # Input path resolution
    ├── output_resolver.py # Output formatting
    ├── initial_scan/      # Initial scanning phase
    │   ├── llm_scanner.py      # LLM-based source file review
    │   ├── pm_scanner.py       # Pattern matching scanner (Semgrep)
    │   ├── pi_scanner.py       # Prompt Injection scanner
    │   ├── finding_filter.py   # Finding filtering and validation
    │   └── dedup.py            # Finding deduplication
    └── deep_analysis/     # Deep analysis phase
        ├── agent_orchestrator.py  # Agent orchestration logic
        ├── cpg_builder.py         # CPG construction and management
        └── sub_agent.py           # Sub-agent implementations
```

## Core Components

### Scanner Module

The scanner module provides the core functionality for code security scanning:

- **Initial Scan**: Performs initial security analysis using multiple methods:
  - **LLM Scanner**: Uses large language models to review source files for security vulnerabilities
  - **Pattern Matching Scanner**: Uses Semgrep for pattern-based static analysis
  - **Prompt Injection Scanner**: Detects Prompt Injection risks in JSON Schema description fields

- **Deep Analysis**: Performs advanced analysis using:
  - **CPG Builder**: Constructs Code Property Graphs for deeper code analysis
  - **Agent Orchestrator**: Coordinates multiple agents for comprehensive security review

### Pipeline Module

The pipeline module orchestrates the entire scanning workflow:

- **Orchestrator**: Manages the end-to-end scanning process
- **Configuration**: Supports flexible scan strategies, deduplication, filtering, and output formatting

### API Module

Provides RESTful API services for the scanning functionality:

- **PI Scanner Service**: Standalone service for Prompt Injection detection

## Configuration

Before using the modules, you need to configure the following in `configs/default.yaml`:

### LLM Configuration

Configure the LLM settings for code review:

```yaml
llm:
  api_key: YOUR_API_KEY_HERE
  model_name: Qwen3-Coder
  max_workers: 16
  base_url: YOUR_BASE_URL_HERE
  max_requests_per_minute: 2000
```

**Configuration Fields:**
- `api_key`: Your API key (e.g., `pk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
- `base_url`: API base URL (e.g., `https://api.openai.com/v1`)
- `model_name`: Model name to use for code review
- `max_workers`: Maximum number of concurrent worker threads
- `max_requests_per_minute`: Rate limiting for API requests

### PI Scanner Configuration

The Prompt Injection Scanner detects security risks in JSON Schema description fields.

```yaml
pi_scanner:
  api_key: YOUR_API_KEY_HERE
  base_url: YOUR_BASE_URL_HERE
  model: YOUR_MODEL_NAME_HERE
```

**Configuration Fields:**
- `api_key`: Your API key (can be the same as or different from LLM config)
- `base_url`: API base URL (e.g., `https://api.openai.com/v1` or OpenAI-compatible gateway)
- `model`: Model name (e.g., `gpt-4` or `Qwen3Guard-Gen-8B`)

### CPG Configuration

Configure Code Property Graph settings:

```yaml
cpg:
  backend: joern
  reuse_cache: true
  max_graph_nodes: 2000000
  executable_path: /usr/local/bin/joern
```

### Report Configuration

Configure output report settings:

```yaml
report:
  formats:
    - cli
    - json
    - markdown
  output_dir: ./reports
  severity_threshold: low
```

## Usage Examples

### Basic Scanning

```python
from scanner import resolve_scan_context
from scanner.initial_scan import OpenAILLMScanner, LocalPMScanner
from scanner.output_resolver import simple_output

# Resolve scan context
context = resolve_scan_context(
    path="/path/to/code",
    auto_detect_languages=True
)

# Run LLM scanner
llm_scanner = OpenAILLMScanner()
findings = list(llm_scanner.scan(context))

# Run pattern matching scanner
pm_scanner = LocalPMScanner()
pm_findings = list(pm_scanner.scan(context))

# Output results
all_findings = list(findings) + list(pm_findings)
simple_output(all_findings)
```

### Using Pipeline Orchestrator

```python
from pipeline.orchestrator import DefaultOrchestrator, PipelineConfig
from scanner.data_types import ScanStrategyConfig

# Configure pipeline
config = PipelineConfig(
    jobs=8,
    scan_strategy=ScanStrategyConfig(
        enable_pm=True,
        enable_llm=True
    )
)

# Create orchestrator
orchestrator = DefaultOrchestrator(config)

# Run end-to-end scan
results = orchestrator.scan("/path/to/code")
```

### Prompt Injection Scanning

```python
from api.services.pi_scanner_service import scan_schema_json
import json

# Example JSON Schema
schema = {
    "type": "object",
    "properties": {
        "param": {
            "description": "User input parameter",
            "type": "string"
        }
    }
}

# Scan for prompt injection risks
result = await scan_schema_json(json.dumps(schema))
print(result)
```

## API Server

To start the API server:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API provides endpoints for:
- Prompt Injection scanning
- Code security analysis
- Report generation

## Key Features

- **Multi-method Scanning**: Combines LLM-based analysis, pattern matching, and specialized scanners
- **Flexible Configuration**: YAML-based configuration with sensible defaults
- **Extensible Architecture**: Easy to add new scanners and analysis methods
- **Comprehensive Filtering**: Built-in filtering and deduplication capabilities
- **Multiple Output Formats**: Supports CLI, JSON, and Markdown output formats

## Dependencies

Key dependencies include:
- `openai`: For LLM API interactions
- `pyyaml`: For configuration file parsing
- `semgrep`: For pattern matching (optional, if using PM scanner)

## License

See the main project LICENSE file for details.
