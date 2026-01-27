# JEB MCP Server

JEB MCP Server 是一个基于 Model Context Protocol (MCP) 的服务器，通过 JEB 反编译引擎提供 Android APK 分析功能。该服务器将 JEB 的强大反编译能力封装为 MCP 服务，可以通过 MCP 协议与 AI 助手或其他客户端进行交互。

## 目录

- [系统要求](#系统要求)
- [项目结构](#项目结构)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [Docker 容器部署](#docker-容器部署)
- [故障排查](#故障排查)
- [相关资源](#相关资源)

## 系统要求

### 必需环境

- **Java**: 17 或更高版本
- **Python**: 3.10 或更高版本
- **JEB 社区版**: 需要有效的许可证密钥
- **uv** (推荐): 用于 Python 依赖管理（可选，脚本会自动安装）

### 可选工具

- **7z/7za**: 用于解压 JEB 安装包（如果 JEB 未预安装）
- **wget/curl**: 用于下载 JEB（如果 JEB 未预安装）

## 项目结构

```
jebmcp/
├── README.md              # 本文档
├── start_mcp_jeb.sh       # 主启动脚本
├── server.py              # MCP 服务器主程序（FastMCP）
├── MCPc.py                # JEB 客户端脚本（运行在 JEB 内部）
├── pyproject.toml          # Python 项目配置
├── uv.lock                # 依赖锁定文件
├── jeb/                   # JEB 安装目录（自动下载或手动放置）
│   ├── jeb_linux.sh       # JEB Linux 启动脚本
│   └── ...
├── logs/                  # 日志目录
│   ├── jeb_start.log      # JEB 服务日志
│   └── mcp_start.log      # MCP 服务日志
└── .venv/                 # Python 虚拟环境（自动创建）
```

## 安装步骤

### 1. 准备 JEB 许可证密钥

JEB 社区版需要有效的许可证密钥才能运行。首次运行前需要生成密钥：

```bash
cd deploy/docker/mcp/mcp_servers/jebmcp

# 如果 JEB 已安装，运行以下命令生成密钥
sh jeb/jeb_linux.sh -c --script="jeb/scripts/MCP.py"
```

**注意**: 
- 首次运行会提示输入许可证密钥
- 密钥生成后，后续启动将自动使用已保存的密钥
- 如果密钥文件已存在（`.jeb_license_data`），可以跳过此步骤

### 2. 自动安装（推荐）

使用启动脚本自动完成所有安装步骤：

```bash
cd deploy/docker/mcp/mcp_servers/jebmcp
bash start_mcp_jeb.sh
```

脚本会自动：
- 检测并创建 Python 虚拟环境
- 安装 Python 依赖（fastmcp 等）
- 检测或下载 JEB（如果不存在）
- 启动 JEB 服务器和 MCP 服务器

### 3. 手动安装

如果需要手动控制安装过程：

```bash
# 1. 创建虚拟环境
cd deploy/docker/mcp/mcp_servers/jebmcp
uv venv .venv  # 或使用 python -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 3. 安装依赖
uv pip install fastmcp  # 或使用 pip install fastmcp

# 4. 确保 JEB 已安装
# 将 JEB 解压到 jeb/ 目录，或让脚本自动下载
```

## 配置说明

### 环境变量

可以通过环境变量配置服务参数：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `JEB_HOME` | `./jeb` | JEB 安装目录路径 |
| `JEB_MCP_HOME` | 脚本所在目录 | MCP 服务器工作目录 |
| `JEB_SERVER_PORT` | `16161` | JEB 服务器监听端口 |
| `JEB_MCP_PORT` | `8008` | MCP 服务器监听端口 |
| `JEB_SERVER_IP` | `localhost` | JEB 服务器 IP 地址 |

### 命令行参数

启动脚本支持以下命令行参数：

```bash
bash start_mcp_jeb.sh \
  --jeb-home /path/to/jeb \
  --mcp-home /path/to/jebmcp \
  --jeb-port 16161 \
  --mcp-port 8008 \
  --python /path/to/python
```

**优先级**: 命令行参数 > 环境变量 > 默认值

## 使用方法

### 本地运行

#### 方式一：使用启动脚本（推荐）

```bash
cd deploy/docker/mcp/mcp_servers/jebmcp
bash start_mcp_jeb.sh
```

#### 方式二：手动启动

```bash
# 1. 启动 JEB 服务器
cd jeb
nohup sh jeb_linux.sh -c --script="../MCPc.py" > ../logs/jeb_start.log 2>&1 &

# 2. 等待 JEB 服务器启动（约 5-10 秒）
sleep 10

# 3. 启动 MCP 服务器
cd ..
source .venv/bin/activate
nohup python server.py > logs/mcp_start.log 2>&1 &
```

### 验证服务状态

检查服务是否正常运行：

```bash
# 检查 JEB 服务器端口
lsof -i :16161

# 检查 MCP 服务器端口
lsof -i :8008

# 查看日志
tail -f logs/jeb_start.log
tail -f logs/mcp_start.log
```

### 停止服务

```bash
# 停止 JEB 服务器
lsof -ti :16161 | xargs kill -9

# 停止 MCP 服务器
lsof -ti :8008 | xargs kill -9
```

## Docker 容器部署

### 在 MCP Server 容器中使用

JEB MCP Server 已配置在 MCP Server 容器中，通过 Supervisor 管理。

#### 1. 配置文件

Supervisor 配置文件位于 `deploy/docker/mcp/supervisor/conf.d/mcp-servers.conf`：

```ini
[program:mcp-jeb]
command=bash /export/App/code/jebmcp/start_mcp_jeb.sh
directory=/export/App/code/jebmcp
autostart=true
autorestart=true
startsecs=20
startretries=3
stopwaitsecs=30
stdout_logfile=/export/App/logs/mcp-jeb.stdout.log
stderr_logfile=/export/App/logs/mcp-jeb.stderr.log
stdout_logfile_maxbytes=50MB
stderr_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile_backups=10
environment=PYTHONUNBUFFERED="1",PYTHONIOENCODING="utf-8",JEB_SERVER_PORT="16161",JEB_MCP_PORT="8008"
user=root
```

#### 2. 端口映射

在 `docker-compose.yml` 中确保映射了必要的端口：

```yaml
ports:
  - "16161:16161"  # JEB 服务器端口
  - "8008:8008"     # MCP 服务器端口
```

#### 3. 启动容器

```bash
# 使用 docker-compose
docker-compose --profile mcpserver up -d mcpserver

# 或使用 docker run
docker run -d \
  --name joysafeter-mcpserver \
  -p 16161:16161 \
  -p 8008:8008 \
  -v $(pwd)/deploy/docker/mcp/mcp_servers:/export/App/code \
  joysafeter-mcpserver:latest
```

#### 4. 管理服务

```bash
# 查看服务状态
docker exec joysafeter-mcpserver \
  supervisorctl -c /export/App/supervisor/supervisord.conf status

# 重启 JEB MCP 服务
docker exec joysafeter-mcpserver \
  supervisorctl -c /export/App/supervisor/supervisord.conf restart mcp-jeb

# 查看日志
docker exec joysafeter-mcpserver \
  tail -f /export/App/logs/mcp-jeb.stdout.log
```

### 首次运行注意事项

在 Docker 容器中首次运行时，需要生成 JEB 许可证密钥：

1. **进入容器**：
   ```bash
   docker exec -it joysafeter-mcpserver bash
   ```

2. **生成密钥**：
   ```bash
   cd /export/App/code/jebmcp
   sh jeb/jeb_linux.sh -c --script="jeb/scripts/MCP.py"
   ```

3. **退出容器**，服务会自动重启并加载密钥

## 故障排查

### 问题 1: JEB 许可证密钥未找到

**症状**: 启动时提示需要许可证密钥

**解决方案**:
```bash
# 运行密钥生成命令
cd deploy/docker/mcp/mcp_servers/jebmcp
sh jeb/jeb_linux.sh -c --script="jeb/scripts/MCP.py"
```

### 问题 2: Java 版本不兼容

**症状**: 错误提示 "Java 版本 <17"

**解决方案**:
- 安装 Java 17 或更高版本
- 设置 `JAVA_HOME` 环境变量
- 确保 `java -version` 显示正确的版本

### 问题 3: Python 依赖安装失败

**症状**: `fastmcp` 安装失败

**解决方案**:
```bash
# 手动安装依赖
cd deploy/docker/mcp/mcp_servers/jebmcp
source .venv/bin/activate
pip install fastmcp
```

### 问题 4: 端口被占用

**症状**: 端口 16161 或 8008 已被占用

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :16161
lsof -i :8008

# 杀死进程或修改端口配置
export JEB_SERVER_PORT=16162
export JEB_MCP_PORT=8009
```

### 问题 5: JEB 服务器无法启动

**症状**: JEB 服务器端口未监听

**解决方案**:
1. 检查 JEB 日志：`tail -f logs/jeb_start.log`
2. 确认 JEB 安装完整：`ls -la jeb/jeb_linux.sh`
3. 检查 Java 环境：`java -version`
4. 手动测试 JEB 启动：`cd jeb && sh jeb_linux.sh -c`

### 问题 6: MCP 服务器无法连接 JEB

**症状**: MCP 服务器启动但无法与 JEB 通信

**解决方案**:
1. 确认 JEB 服务器已启动：`lsof -i :16161`
2. 检查环境变量：`echo $JEB_SERVER_PORT $JEB_SERVER_IP`
3. 测试连接：`curl http://localhost:16161/mcp`
4. 查看 MCP 日志：`tail -f logs/mcp_start.log`

### 问题 7: Docker 容器中服务无法启动

**症状**: Supervisor 显示服务状态为 FATAL 或 EXITED

**解决方案**:
1. 查看容器日志：`docker logs joysafeter-mcpserver`
2. 查看服务日志：`docker exec ... cat /export/App/logs/mcp-jeb.stderr.log`
3. 检查文件权限：确保脚本有执行权限
4. 检查挂载卷：确保源代码目录正确挂载

## 相关资源

- [JEB 官方文档](https://www.pnfsoftware.com/jeb/manual/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [Supervisor 文档](http://supervisord.org/)

## 开发说明

### 项目依赖

主要依赖（见 `pyproject.toml`）：
- `fastmcp>=2.14.2`: MCP 服务器框架
- `pydantic>=2.0.0`: 数据验证

### 代码结构

- `server.py`: MCP 服务器主程序，使用 FastMCP 框架
- `MCPc.py`: JEB 客户端脚本，运行在 JEB 内部，提供 JSON-RPC 接口
- `start_mcp_jeb.sh`: 启动脚本，处理环境检测、依赖安装、服务启动

### 扩展功能

要添加新的 MCP 工具或资源，编辑 `server.py` 文件，使用 FastMCP 的装饰器：

```python
@mcp.tool()
def your_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result
```

## 许可证

本项目使用 JEB 社区版，需要遵守 JEB 的许可证条款。请参考 [PNF Software 许可证信息](https://www.pnfsoftware.com/jeb/license/)。
