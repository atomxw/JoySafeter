# Semgrep 规则目录

本目录包含用于 `LocalPMScanner` 模式匹配扫描的 Semgrep 规则文件。这些规则用于快速发现代码中的已知安全漏洞模式和潜在风险。

## 目录结构

```
rules/
├── gitlab/          # GitLab 官方 Semgrep 规则集
│   ├── c/           # C 语言规则
│   ├── java/        # Java 规则
│   ├── python/      # Python 规则
│   ├── javascript/  # JavaScript 规则
│   ├── go/          # Go 语言规则
│   └── ...          # 其他语言规则
└── README.md        # 本文件
```

## 规则管理

### 方式一：使用 semgrep-rules-manager（推荐）

使用 [semgrep-rules-manager](https://github.com/iosifache/semgrep-rules-manager) 工具来管理和更新规则：

```bash
# 安装工具
pip install semgrep-rules-manager

# 使用工具管理规则
semgrep-rules-manager --help
```

### 方式二：直接克隆官方仓库

直接从 [Semgrep 官方规则仓库](https://github.com/semgrep/semgrep) 克隆规则：

```bash
# 克隆 Semgrep 官方规则
git clone https://github.com/semgrep/semgrep.git
# 将规则文件复制到本目录
```

### 方式三：使用 GitLab 规则集

当前目录中的 `gitlab/` 子目录包含来自 [GitLab Semgrep 规则仓库](https://gitlab.com/gitlab-org/security-products/analyzers/semgrep-rules) 的规则集，这些规则已经过优化和测试。

## 添加新规则

1. **创建规则文件**：在相应的语言目录下创建 `.yml` 规则文件
2. **遵循格式**：
   - 使用 `"` 作为字符串引号
   - 缩进使用 2 个空格
   - 最大行长度：100 字符
   - 每个规则文件以 `---` 开头
   - 为每个规则提供对应的测试用例

3. **规则文件示例**：
```yaml
---
rules:
  - id: example-rule
    message: "发现潜在安全问题"
    languages: [python]
    severity: ERROR
    patterns:
      - pattern: dangerous_function($X)
```

## 使用说明

规则会在 `LocalPMScanner` 初始化时自动加载。默认情况下，扫描器会从 `configs/initial_scan/rules` 目录加载所有规则。

如需指定特定规则路径，可在代码中显式指定：

```python
from scanner.initial_scan.pm_scanner import LocalPMScanner
from pathlib import Path

# 使用默认规则目录
scanner = LocalPMScanner()

# 或指定自定义规则路径
scanner = LocalPMScanner(
    rule_paths=[Path("path/to/custom/rules")]
)
```

## 规则更新

定期更新规则以获取最新的安全检测能力：

1. 检查官方仓库的更新
2. 测试新规则是否与现有代码库兼容
3. 更新规则文件后重新运行扫描验证

## 相关文档

- [初筛引擎文档](../../../docs/static_scanner/initial_scan.md)
- [Semgrep 官方文档](https://semgrep.dev/docs/)
- [GitLab Semgrep 规则仓库](https://gitlab.com/gitlab-org/security-products/analyzers/semgrep-rules)