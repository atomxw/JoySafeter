# MCP 服务器文件共享配置说明

## 概述

前端上传的文件存储在 backend 容器的 `/app/data/files/{user_id}/{filename}` 目录中。通过 Docker volume 共享，MCP 容器也可以访问这些文件。

## 配置状态

### ✅ 已完成的配置

1. **生产环境** (`docker-compose.prod.yml`)
   - `backend` 容器挂载：`backend-files:/app/data/files`
   - `mcpserver` 容器挂载：`backend-files:/app/data/files`
   - ✅ 两个容器已共享同一个 volume

2. **开发环境** (`docker-compose-middleware.yml`)
   - `mcpserver` 容器挂载：`backend-files:/app/data/files`
   - ✅ 已配置文件共享 volume

## 文件路径结构

```
/app/data/files/
├── {user_id_1}/
│   ├── file1.txt
│   ├── file2.pdf
│   └── ...
├── {user_id_2}/
│   ├── file3.zip
│   └── ...
└── ...
```

## 如何在 MCP 服务器中访问文件

### 方法 1: 直接文件系统访问（推荐）

MCP 服务器可以通过 Python 的 `pathlib` 或 `os` 模块直接访问共享的文件：

```python
from pathlib import Path

# 文件存储根目录（与 backend 一致）
FILE_STORAGE_ROOT = Path("/app/data/files")

def read_user_file(user_id: str, filename: str) -> bytes:
    """
    读取用户上传的文件
    
    Args:
        user_id: 用户 ID
        filename: 文件名
        
    Returns:
        文件内容（字节）
    """
    file_path = FILE_STORAGE_ROOT / user_id / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    return file_path.read_bytes()
```

### 方法 2: 通过环境变量配置路径

可以在 MCP 容器的环境变量中设置文件存储路径：

```yaml
# docker-compose.prod.yml 或 docker-compose-middleware.yml
mcpserver:
  environment:
    # ... 其他环境变量 ...
    FILE_STORAGE_ROOT: /app/data/files
```

然后在代码中使用：

```python
import os
from pathlib import Path

FILE_STORAGE_ROOT = Path(os.getenv("FILE_STORAGE_ROOT", "/app/data/files"))
```

### 方法 3: 通过后端 API 获取文件信息

如果 MCP 服务器需要知道用户上传了哪些文件，可以通过后端 API 获取：

```python
import httpx

async def get_user_files(user_id: str, backend_url: str = "http://backend:8000"):
    """
    通过后端 API 获取用户文件列表
    
    Args:
        user_id: 用户 ID
        backend_url: 后端服务 URL
        
    Returns:
        文件列表
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{backend_url}/api/v1/files/list",
            headers={"Authorization": "Bearer <token>"}  # 需要认证
        )
        return response.json()
```

## 验证文件共享

### 1. 检查 volume 挂载

在容器中检查 volume 是否正确挂载：

```bash
# 在 backend 容器中
docker exec joysafeter-backend ls -la /app/data/files

# 在 mcpserver 容器中
docker exec joysafeter-mcpserver ls -la /app/data/files
```

两个容器应该能看到相同的目录结构。

### 2. 测试文件访问

1. **上传文件**：通过前端上传一个测试文件
2. **在 backend 容器中验证**：
   ```bash
   docker exec joysafeter-backend ls -la /app/data/files/{user_id}/
   ```
3. **在 mcpserver 容器中验证**：
   ```bash
   docker exec joysafeter-mcpserver ls -la /app/data/files/{user_id}/
   ```

两个容器应该能看到相同的文件。

### 3. 在 MCP 服务器代码中测试

创建一个测试脚本验证文件访问：

```python
# test_file_access.py
from pathlib import Path

FILE_STORAGE_ROOT = Path("/app/data/files")

# 列出所有用户目录
user_dirs = [d for d in FILE_STORAGE_ROOT.iterdir() if d.is_dir()]
print(f"找到 {len(user_dirs)} 个用户目录")

# 列出某个用户的所有文件
if user_dirs:
    user_id = user_dirs[0].name
    user_files = list(user_dirs[0].iterdir())
    print(f"用户 {user_id} 有 {len(user_files)} 个文件:")
    for f in user_files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")
```

## 注意事项

1. **权限问题**：确保 MCP 服务器进程有读取 `/app/data/files` 目录的权限
2. **用户 ID 格式**：确保 user_id 格式与 backend 存储时一致（通常是 UUID 字符串）
3. **文件路径安全**：在访问文件时，应该验证路径，防止路径遍历攻击：
   ```python
   from pathlib import Path
   
   def safe_read_file(user_id: str, filename: str) -> bytes:
       # 确保路径在允许的范围内
       file_path = FILE_STORAGE_ROOT / user_id / Path(filename).name
       
       # 验证路径是否在根目录下
       try:
           file_path.resolve().relative_to(FILE_STORAGE_ROOT.resolve())
       except ValueError:
           raise ValueError("非法文件路径")
       
       return file_path.read_bytes()
   ```

4. **文件编码**：文本文件可能需要指定编码：
   ```python
   file_path.read_text(encoding="utf-8")
   ```

## 示例：在 mcp_scanner 中使用共享文件

如果需要在 `mcp_scanner` 中读取 backend 上传的文件，可以修改相关代码：

```python
# deploy/docker/mcp/mcp_servers/mcp_scanner/codes/api/routes/scan.py
from pathlib import Path
import os

# 文件存储根目录
FILE_STORAGE_ROOT = Path(os.getenv("FILE_STORAGE_ROOT", "/app/data/files"))

@router.post("/scan-user-file")
async def scan_user_file(
    user_id: str,
    filename: str,
    # ... 其他参数
):
    """
    扫描用户上传的文件
    
    Args:
        user_id: 用户 ID
        filename: 文件名
    """
    # 读取用户文件
    file_path = FILE_STORAGE_ROOT / user_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 执行扫描
    # ... 扫描逻辑 ...
```

## 故障排查

### 问题 1: MCP 容器看不到文件

**可能原因**：
- Volume 未正确挂载
- 文件路径不正确

**解决方法**：
1. 检查 docker-compose 配置中的 volume 挂载
2. 确认两个容器使用相同的 volume 名称
3. 重启容器：`docker-compose restart mcpserver`

### 问题 2: 权限错误

**可能原因**：
- 文件所有者不匹配
- 目录权限不足

**解决方法**：
```bash
# 在容器中检查权限
docker exec joysafeter-mcpserver ls -la /app/data/files

# 如果需要，调整权限（在 backend 容器中）
docker exec joysafeter-backend chmod -R 755 /app/data/files
```

### 问题 3: 文件路径不存在

**可能原因**：
- user_id 格式不匹配
- 文件尚未上传

**解决方法**：
1. 确认 user_id 格式（检查 backend 日志）
2. 验证文件是否已成功上传到 backend

## 总结

✅ **配置已完成**：两个容器已共享 `backend-files` volume

✅ **路径一致**：两个容器中的挂载路径都是 `/app/data/files`

✅ **可以访问**：MCP 服务器可以通过 `/app/data/files/{user_id}/{filename}` 访问用户上传的文件

⚠️ **注意事项**：
- 需要知道 `user_id` 和 `filename` 才能访问文件
- 建议添加路径验证和权限检查
- 可以通过后端 API 获取文件列表，而不是直接遍历目录

