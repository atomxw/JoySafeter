# 中间件架构完整指南

## 📋 文档概述

本文档整合了中间件生成过程的完整架构设计，包括审查报告、实现总结和技术细节。提供了从节点配置到中间件实例化的完整流程图和实施指南。

---

## 🏗️ 整体架构图

```mermaid
graph TB
    %% 数据流
    subgraph "节点配置"
        A1[JSON配置] --> A2["skills: ['uuid1', 'uuid2']"]
        A2 --> A3["enableMemory: true"]
        A3 --> A4["memoryModel: 'gpt-4'"]
    end

    subgraph "BaseGraphBuilder"
        B1[resolve_middleware_for_node] --> B2{策略模式解析器}
        B2 --> B3[_resolve_skill_middleware]
        B2 --> B4[_resolve_memory_middleware]
        B2 --> B5[_resolve_custom_middleware]

        B3 --> B6[SkillMiddleware实例]
        B4 --> B7[AgentMemoryIterationMiddleware实例]
        B5 --> B8[CustomMiddleware实例]
    end

    subgraph "AgentNodeExecutor"
        C1[_ensure_agent] --> C2[调用resolve_middleware_for_node]
        C2 --> C3[获取node_middleware列表]
        C3 --> C4[传递给get_agent]
    end

    subgraph "Agent创建流程"
        D1[get_agent] --> D2[默认中间件链]
        D1 --> D3[node_middleware]
        D2 --> D4[合并中间件]
        D3 --> D4
        D4 --> D5[按优先级排序]
        D5 --> D6[create_agent(middleware=[...])]
    end

    subgraph "中间件执行顺序"
        E1[SkillMiddleware<br/>priority=50] --> E2[AgentMemoryIterationMiddleware<br/>priority=50]
        E2 --> E3[TaggingMiddleware<br/>priority=100]
    end

    subgraph "错误处理"
        F1[try-catch隔离] --> F2[失败时记录警告]
        F2 --> F3[继续处理其他中间件]
        F3 --> F4[优雅降级]
    end

    %% 连接关系
    A1 --> B1
    B6 --> C3
    B7 --> C3
    B8 --> C3
    C4 --> D3
    D6 --> E1
    B2 -.-> F1

    %% 样式
    classDef config fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef builder fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef executor fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef agent fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef execution fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px

    class A1,A2,A3,A4 config
    class B1,B2,B3,B4,B5,B6,B7,B8 builder
    class C1,C2,C3,C4 executor
    class D1,D2,D3,D4,D5,D6 agent
    class E1,E2,E3 execution
    class F1,F2,F3,F4 error
```

---

## 🔄 中间件生成完整流程

### 阶段1：配置解析
```
节点配置 (JSON) → BaseGraphBuilder.resolve_middleware_for_node()
                      ↓
               策略模式解析器列表
                      ↓
              中间件实例列表 (已排序)
```

### 阶段2：Agent构建
```
AgentNodeExecutor._ensure_agent()
         ↓
    获取node_middleware列表
         ↓
    get_agent(node_middleware=...)
         ↓
    合并到默认中间件链 + 优先级排序
         ↓
    create_agent(middleware=[...])
```

### 阶段3：执行顺序
```
模型调用前 → 中间件按优先级执行 → 模型调用 → 中间件后处理
```

---

## 🧩 核心组件详解

### 1. BaseGraphBuilder - 配置解析器

**职责**：从节点配置解析并实例化中间件

```python
class BaseGraphBuilder(ABC):
    async def resolve_middleware_for_node(
        self,
        node: GraphNode,
        user_id: Optional[str] = None,
        db_session_factory: Optional[Any] = None,
    ) -> List[Any]:
        # 策略模式：解析器列表
        _middleware_resolvers = [
            lambda n, u, d: self._resolve_skill_middleware(n, u, d),
            lambda n, u, d: self._resolve_memory_middleware(n, u),
        ]

        middleware = []
        for resolver in _middleware_resolvers:
            try:
                mw = await resolver(node, user_id, db_session_factory)
                if mw:
                    middleware.append(mw)
            except Exception as e:
                logger.warning(f"Resolver failed: {e}")

        # 按优先级排序
        middleware.sort(key=lambda mw: getattr(mw, 'priority', 100))
        return middleware
```

### 2. AgentNodeExecutor - 中间件传递器

**职责**：获取节点中间件并传递给Agent创建流程

```python
class AgentNodeExecutor:
    async def _ensure_agent(self) -> Runnable:
        # 获取节点配置的中间件
        node_middleware = []
        if self.builder:
            node_middleware = await self.builder.resolve_middleware_for_node(
                node=self.node,
                user_id=self.user_id,
            )

        # 传递给get_agent
        agent = await get_agent(
            model=self.resolved_model,
            system_prompt=self.system_prompt,
            tools=node_tools,
            agent_name=self.node_id,
            node_middleware=node_middleware,  # 关键参数
        )
        return agent
```

### 3. get_agent - 中间件合并器

**职责**：合并默认中间件和节点中间件，按优先级排序

```python
async def get_agent(
    model,
    system_prompt=None,
    tools=None,
    agent_name=None,
    node_middleware=None,  # 新增参数
):
    # 默认中间件链
    middleware = [skill_middleware, todo_list_middleware]

    # 添加节点中间件 (按优先级排序)
    if node_middleware:
        node_middleware.sort(key=lambda mw: getattr(mw, 'priority', 100))
        middleware.extend(node_middleware)

    # 创建Agent
    return create_agent(model, middleware=middleware, ...)
```

---

## 📦 当前支持的中间件

### 1. SkillMiddleware (优先级: 50)

**配置**：
```json
{
  "config": {
    "skills": ["uuid1", "uuid2", "uuid3"]
  }
}
```

**功能**：
- 从技能UUID列表加载技能描述
- 将技能信息注入系统提示
- 支持渐进式技能发现

**执行阶段**：模型调用前注入系统提示

### 2. AgentMemoryIterationMiddleware (优先级: 50)

**配置**：
```json
{
  "config": {
    "enableMemory": true,
    "memoryModel": "gpt-4",
    "memoryPrompt": "记住用户偏好：喜欢详细回答"
  }
}
```

**功能**：
- **前处理**：检索用户相关记忆并注入系统提示
- **后处理**：将用户输入提交给记忆管理系统

**执行阶段**：模型调用前后都执行

### 3. TaggingMiddleware (优先级: 100)

**配置**：通过代码设置标签

**功能**：
- 为Agent调用添加标签
- 支持可观测性和监控

**执行阶段**：模型调用时添加标签

---

## ⚡ 架构优势

### ✅ 清晰度
1. **职责分离明确**
   - BaseGraphBuilder：配置解析和中间件创建
   - AgentNodeExecutor：中间件获取和传递
   - get_agent：中间件合并和执行

2. **代码一致性**
   - 所有解析器遵循相同模式
   - 统一的错误处理和日志记录
   - 清晰的命名约定

### ✅ 可扩展性
1. **易于添加新类型**
   ```python
   # 只需添加新方法和一行注册
   async def _resolve_custom_middleware(self, node, user_id):
       # 解析逻辑
       return CustomMiddleware(...)

   _middleware_resolvers.append(
       lambda n, u, d: self._resolve_custom_middleware(n, u)
   )
   ```

2. **灵活的配置**
   - 每个中间件可自定义配置结构
   - 支持可选配置和默认值
   - 配置验证和错误提示

### ✅ 健壮性
1. **错误隔离**
   ```python
   try:
       mw = await resolver(node, user_id, db_factory)
       if mw:
           middleware.append(mw)
   except Exception as e:
       logger.warning(f"Resolver {resolver.__name__} failed: {e}")
       # 继续处理其他中间件
   ```

2. **向后兼容**
   - 新功能不影响现有代码
   - 可选参数设计
   - 默认行为保持不变

---

## 🔧 扩展指南

### 添加新的中间件类型

#### 步骤 1：实现中间件类
```python
class CustomMiddleware(AgentMiddleware):
    """自定义中间件"""

    priority = 75  # 设置优先级

    def __init__(self, config: dict, user_id: str):
        self.config = config
        self.user_id = user_id

    async def abefore_model(self, state, runtime):
        # 前处理逻辑
        pass

    async def aafter_model(self, state, runtime):
        # 后处理逻辑
        pass
```

#### 步骤 2：添加解析器方法
```python
async def _resolve_custom_middleware(
    self,
    node: GraphNode,
    user_id: Optional[str] = None,
) -> Optional[CustomMiddleware]:
    """解析并创建 CustomMiddleware"""
    data = node.data or {}
    config = data.get("config", {})

    # 检查是否启用
    if not config.get("enableCustom", False):
        return None

    # 解析配置
    custom_config = config.get("customConfig")
    if not custom_config:
        logger.warning("enableCustom=True but customConfig not specified")
        return None

    try:
        middleware = CustomMiddleware(
            config=custom_config,
            user_id=user_id or self.user_id,
        )
        logger.debug(f"Created CustomMiddleware for node '{data.get('label')}'")
        return middleware
    except Exception as e:
        logger.warning(f"Failed to create CustomMiddleware: {e}")
        return None
```

#### 步骤 3：注册到解析器列表
```python
async def resolve_middleware_for_node(self, node, user_id=None, db_session_factory=None):
    # 解析器列表
    _middleware_resolvers = [
        lambda n, u, d: self._resolve_skill_middleware(n, u, d),
        lambda n, u, d: self._resolve_memory_middleware(n, u),
        lambda n, u, d: self._resolve_custom_middleware(n, u),  # 新增
    ]

    middleware = []
    for resolver in _middleware_resolvers:
        try:
            mw = await resolver(node, user_id, db_session_factory)
            if mw:
                middleware.append(mw)
        except Exception as e:
            logger.warning(f"Resolver failed: {e}")

    # 按优先级排序
    middleware.sort(key=lambda mw: getattr(mw, 'priority', 100))
    return middleware
```

#### 步骤 4：更新文档
在本文档的"当前支持的中间件"部分添加新中间件的说明。

---

## 📋 最佳实践

### 1. 解析器方法命名
- 遵循模式：`_resolve_<middleware_name>_middleware`
- 示例：`_resolve_skill_middleware`, `_resolve_memory_middleware`

### 2. 返回值约定
- **成功**：返回中间件实例
- **未配置**：返回 `None`
- **失败**：记录警告日志，返回 `None`

### 3. 日志记录标准
```python
# 成功创建
logger.debug(f"Created {MiddlewareName} for node '{label}'")

# 配置错误
logger.warning(f"enableFeature=True but config not specified for node '{label}'")

# 创建失败
logger.warning(f"Failed to create {MiddlewareName} for node '{label}': {e}")
```

### 4. 配置验证
```python
# 检查必需配置
required_config = config.get("requiredField")
if not required_config:
    logger.warning(f"requiredField not specified for {MiddlewareName}")
    return None

# 验证配置值
if not isinstance(required_config, (str, int)):  # 期望的类型
    logger.warning(f"Invalid requiredField type for {MiddlewareName}")
    return None
```

### 5. 优先级设置
- 0-10：系统级中间件（安全、监控）
- 50：功能中间件（技能、记忆）
- 100：辅助中间件（标签、日志）

### 6. 错误处理
```python
try:
    # 可能失败的操作
    middleware = SomeMiddleware(config=config)
    return middleware
except Exception as e:
    logger.warning(f"Failed to create {MiddlewareName}: {e}")
    return None  # 优雅降级
```

---

## 🔍 架构评估

| 维度 | 评分 | 说明 |
|------|------|------|
| **职责分离** | ⭐⭐⭐⭐⭐ | 各组件职责清晰，模块化良好 |
| **代码一致性** | ⭐⭐⭐⭐ | 已实现策略模式，基本一致 |
| **可扩展性** | ⭐⭐⭐⭐⭐ | 策略模式支持轻松扩展 |
| **错误处理** | ⭐⭐⭐⭐ | 隔离完善，但日志格式需统一 |
| **向后兼容** | ⭐⭐⭐⭐⭐ | 新功能完全向后兼容 |
| **测试覆盖** | ⭐⭐ | 缺乏自动化测试，风险较高 |
| **性能效率** | ⭐⭐⭐ | 无缓存机制，存在优化空间 |
| **类型安全** | ⭐⭐⭐⭐ | 类型注解完善，但缺乏运行时验证 |
| **DeepAgents集成** | ⭐⭐⭐⭐⭐ | 已修复参数传递问题 |
| **中间件优先级** | ⭐⭐⭐⭐ | 已实现基础优先级控制 |

**总体评分**: ⭐⭐⭐⭐ (4/5)

---

## 🚀 未来改进方向

### 高优先级
1. **完善测试覆盖** - 为所有中间件解析器添加单元测试
2. **添加配置验证机制** - 使用Pydantic验证配置结构

### 中优先级
1. **实现中间件缓存机制** - 避免重复解析相同配置
2. **统一错误处理和日志** - 标准化日志格式

### 低优先级
1. **文档自动化生成** - 从代码生成配置文档
2. **插件化架构支持** - 支持动态加载第三方中间件

---

*本文档整合了 `middleware-architecture-review.md` 和 `middleware-architecture-summary.md` 的内容，并新增了完整的架构图和实施指南。*
