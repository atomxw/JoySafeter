# MCP 安全工具集成指南

本文档说明如何将后端 MCP 工具转换为前端 Skills 格式，并集成到默认技能中。

---

## 一、转换 MCP 工具为 Skills

### 转换脚本

`backend/scripts/convert_mcp_to_skills.py`

### 使用方法

```bash
cd backend

# 转换核心类别（默认 60 个工具）
python scripts/convert_mcp_to_skills.py

# 转换所有 108 个工具
python scripts/convert_mcp_to_skills.py --all

# 指定类别
python scripts/convert_mcp_to_skills.py --categories=web_security,network_scanning

# 限制数量
python scripts/convert_mcp_to_skills.py --max=20
```

### 输出文件

- `backend/scripts/converted_skills.json` - 转换输出（临时）
- `backend/data/initial_skills.json` - Git 跟踪的技能数据
- `frontend/public/converted_skills.json` - 前端访问副本

### 核心类别

| 类别 | 工具数 |
|------|--------|
| web_security | 14 |
| network_scanning | 15 |
| binary_analysis | 15 |
| container_security | 7 |
| vulnerability_scanning | 5 |
| authentication_testing | 4 |

---

## 二、集成到前端

### 修改的文件

`frontend/services/skillService.ts`

**关键修改**：

1. 添加 `ConvertedSkillsData` 接口
2. 添加 `loadMCPSkills()` 函数
3. 修改 `getSkills()` 方法：首次加载时自动合并演示技能 + MCP 技能

```typescript
// 加载 MCP 安全工具
async function loadMCPSkills(): Promise<Skill[]> {
  try {
    const res = await fetch('/converted_skills.json');
    if (!res.ok) {
      console.warn('MCP skills file not found, using demo skills only');
      return [];
    }
    const data: ConvertedSkillsData = await res.json();
    console.log(`✅ 已加载 ${data.total || data.skills?.length || 0} 个 MCP 安全工具`);
    return data.skills || [];
  } catch (err) {
    console.warn('Failed to load MCP skills, using demo skills only:', err);
    return [];
  }
}

export const skillService = {
  async getSkills(): Promise<Skill[]> {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      // 首次加载：合并演示技能 + MCP 技能
      const demoSkills = INITIAL_SKILLS;
      const mcpSkills = await loadMCPSkills();
      const allSkills = [...demoSkills, ...mcpSkills];

      localStorage.setItem(STORAGE_KEY, JSON.stringify(allSkills));
      console.log(`✅ 技能初始化完成: ${allSkills.length} 个（演示: ${demoSkills.length}, MCP: ${mcpSkills.length}）`);
      return allSkills;
    }
    return JSON.parse(stored);
  },
  // ... 其他方法
};
```

---

## 三、文件清单

### Git 跟踪的文件

| 文件 | 说明 |
|------|------|
| `frontend/services/skillService.ts` | 技能服务（自动加载 MCP 工具）|
| `frontend/public/converted_skills.json` | 60 个 MCP 安全工具 |
| `backend/data/initial_skills.json` | 后端技能数据副本 |
| `backend/scripts/convert_mcp_to_skills.py` | 转换脚本 |

### 临时文件（不提交）

| 文件 | 说明 |
|------|------|
| `backend/scripts/converted_skills.json` | 转换输出，可重新生成 |

---

## 四、新用户体验

新用户 clone 项目后，首次打开前端会看到：

- **5 个演示技能**：web scraper, narrative architect, react pro, devops, market analyzer
- **60 个 MCP 安全工具**：nmap, nuclei, jaeles, clair, dirsearch 等
- **总计：65 个技能**

Console 输出示例：

```
✅ 已加载 60 个 MCP 安全工具
✅ 技能初始化完成: 65 个（演示: 5, MCP: 60）
```

---

## 五、更新 MCP 工具

当后端新增或修改 MCP 工具时：

```bash
# 1. 重新转换
cd backend
python scripts/convert_mcp_to_skills.py --all

# 2. 复制到前端
cp scripts/converted_skills.json ../frontend/public/
cp scripts/converted_skills.json data/initial_skills.json

# 3. 提交更新
git add frontend/public/converted_skills.json backend/data/initial_skills.json
git commit -m "feat: update MCP skills"
git push
```

---

## 六、技能数据结构

```typescript
interface Skill {
  id: string;                  // 格式: "category-tool_name"
  name: string;                // 显示名称
  description: string;         // 描述
  license: string;             // 许可证
  content: string;             // manifest.md 内容
  files: SkillFile[];          // 文件列表
  source?: 'local' | 'git' | 'aws' | 'mcp';
  sourceUrl?: string;
  updatedAt: number;
}

interface SkillFile {
  name: string;
  content: string;
  language?: string;
}
```

### manifest.md 格式

```markdown
---
name: tool_name
capabilities: [param1, param2]
category: category_name
tags: [tag1, tag2]
---

# Tool Name

Description

## Parameters
- **param1** (type, Required): description
- **param2** (type, Optional): description
```

---

## 七、故障排查

### 问题：看不到 MCP 技能

**原因**：LocalStorage 已有旧数据

**解决**：
1. 打开 DevTools → Application → Local Storage
2. 删除 `joysafeter_skills` 键
3. 刷新页面

### 问题：MCP 技能加载失败

**原因**：`frontend/public/converted_skills.json` 不存在或路径错误

**解决**：
```bash
ls frontend/public/converted_skills.json
# 如果不存在，运行转换脚本并复制
```

---

## 八、相关文档

- `batch-create-mcp-tools.md` - 批量创建 MCP 工具
