# 前端 DockerSandbox 配置修复总结

## 修复内容

### 1. 创建 DockerConfigField 组件 ✅

**文件**: `frontend/app/workspace/[workspaceId]/[agentId]/components/fields/DockerConfigField.tsx`

- 可折叠的 Docker 配置面板
- 支持所有 docker_config 字段：
  - `image`: Docker 镜像
  - `memory_limit`: 内存限制
  - `cpu_quota`: CPU 配额
  - `network_mode`: 网络模式（none/bridge）
  - `working_dir`: 工作目录
  - `auto_remove`: 自动删除
  - `max_output_size`: 最大输出大小
  - `command_timeout`: 命令超时

### 2. 更新节点注册表 ✅

**文件**: `frontend/app/workspace/[workspaceId]/[agentId]/services/nodeRegistry.tsx`

#### 2.1 添加默认配置
- `backend_type`: 默认 `'filesystem'`
- `docker_config`: 包含所有默认值的对象

#### 2.2 添加配置 Schema
- `backend_type`: select 类型，选项：`['filesystem', 'docker']`
  - 仅在 `useDeepAgents: true` 时显示
- `docker_config`: dockerConfig 类型
  - 仅在 `backend_type: 'docker'` 时显示

#### 2.3 更新类型定义
- 添加 `'dockerConfig'` 到 `FieldType` 联合类型
- 更新 `showWhen.values` 类型为 `(string | boolean | number)[]`

### 3. 更新 PropertiesPanel ✅

**文件**: `frontend/app/workspace/[workspaceId]/[agentId]/components/PropertiesPanel.tsx`

#### 3.1 添加 DockerConfigField 导入
```typescript
import { DockerConfigField } from './fields/DockerConfigField'
```

#### 3.2 添加 dockerConfig 类型渲染
在 `SchemaFieldRenderer` 的 switch 语句中添加：
```typescript
case 'dockerConfig':
  input = (
    <DockerConfigField
      label={translatedLabel}
      value={(value as Record<string, unknown>) || {}}
      onChange={(val) => onChange(val)}
      description={schema.description}
      disabled={disabled}
    />
  )
  break
```

#### 3.3 增强 showWhen 条件检查
- 支持 boolean、string、number 类型的值比较
- 正确处理字符串 'true'/'false' 到 boolean 的转换
- 确保条件显示逻辑正确工作

## 配置流程

### 用户操作流程

1. **启用 DeepAgents 模式**
   - 在 Agent 节点配置中，将 `useDeepAgents` 设置为 `true`
   - 此时会显示 `backend_type` 和 `description` 字段

2. **选择 Backend 类型**
   - 选择 `backend_type` 为 `'docker'`
   - 此时会显示 `docker_config` 配置面板

3. **配置 Docker 参数**
   - 展开 `docker_config` 面板
   - 配置各项 Docker 参数（镜像、内存、CPU 等）

4. **配置 Skills（可选）**
   - 在 `skills` 字段中选择要预加载的 skills
   - Skills 会在沙箱创建时自动加载到 `/workspace/skills/`

### 数据流

```
前端 PropertiesPanel
  → updateConfig('backend_type', 'docker')
  → updateConfig('docker_config', {...})
  → builderStore.updateNode()
  → API: POST /api/v1/graphs/{graphId}/state
  → 存储到 node.data.config (JSONB)
  ↓
后端 DeepAgentsGraphBuilder
  → 读取 node.data.config.backend_type
  → 读取 node.data.config.docker_config
  → 创建 PydanticSandboxAdapter
  → 预加载 skills 到沙箱
  → 创建 FilesystemMiddleware
  → 创建 CompiledSubAgent
```

## 配置示例

### 完整配置对象

```json
{
  "useDeepAgents": true,
  "backend_type": "docker",
  "docker_config": {
    "image": "python:3.12-slim",
    "memory_limit": "512m",
    "cpu_quota": 50000,
    "network_mode": "none",
    "working_dir": "/workspace",
    "auto_remove": true,
    "max_output_size": 100000,
    "command_timeout": 30
  },
  "skills": ["skill-uuid-1", "skill-uuid-2"]
}
```

## 测试检查清单

- [ ] 启用 `useDeepAgents` 后，`backend_type` 字段显示
- [ ] 选择 `backend_type: 'docker'` 后，`docker_config` 面板显示
- [ ] Docker 配置字段可以正常编辑和保存
- [ ] 配置保存后，重新加载图时配置保留
- [ ] 后端正确读取配置并创建 DockerSandbox
- [ ] Skills 正确预加载到沙箱

## 注意事项

1. **条件显示**: `backend_type` 和 `docker_config` 只在特定条件下显示
   - `backend_type`: 需要 `useDeepAgents: true`
   - `docker_config`: 需要 `backend_type: 'docker'`

2. **默认值**: 如果未配置 `docker_config`，后端会使用默认值

3. **向后兼容**: 如果节点没有 `backend_type` 配置，默认使用 `filesystem` backend

4. **类型安全**: TypeScript 类型定义已更新，确保类型安全

## 相关文件

- `frontend/app/workspace/[workspaceId]/[agentId]/components/fields/DockerConfigField.tsx` - Docker 配置组件
- `frontend/app/workspace/[workspaceId]/[agentId]/services/nodeRegistry.tsx` - 节点注册表
- `frontend/app/workspace/[workspaceId]/[agentId]/components/PropertiesPanel.tsx` - 属性面板
- `backend/app/core/graph/deep_agents_builder.py` - 后端配置读取和执行
