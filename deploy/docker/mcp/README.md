# MCP Server 容器使用指南

## 概述

MCP Server 容器用于运行多个 Model Context Protocol (MCP) 服务器。容器使用 supervisor 管理多个 MCP server 进程，支持 Python 和 Node.js 编写的 MCP 服务，以及多种传输方式（stdio、HTTP、SSE）。

## 目录结构

```
deploy/docker/mcp/
├── Dockerfile                      # Docker镜像定义
├── start.sh                        # 容器启动脚本
├── supervisord.conf                # Supervisor主配置文件
├── mcp_servers/                    # MCP服务源代码目录
│   └── demo-server/                # 示例MCP服务
├── supervisor/
│   └── conf.d/
│       └── mcp-servers.conf.example  # MCP服务配置示例
└── README.md                       # 本文档
```

容器内目录结构：
```
/export/App/
├── supervisor/
│   ├── supervisord.conf           # Supervisor主配置
│   └── conf.d/                    # MCP服务配置目录
├── scripts/
│   └── start.sh                   # 启动脚本
├── logs/                          # 日志目录
├── code/                          # MCP服务源代码挂载点（volume）
└── run/                           # Supervisor运行时目录
```

## 快速开始

### 1. 准备 MCP 服务代码

MCP 服务代码已经位于 `deploy/docker/mcp/mcp_servers/` 目录下。你可以在该目录下添加你的 MCP 服务：

```bash
cd deploy/docker/mcp/mcp_servers
# 在这里添加你的 MCP 服务
```

#### JEB MCP Server 特殊要求

如果你需要使用 **JEB MCP Server**（`jebmcp`），需要先下载并安装 JEB 社区版：

1. **下载 JEB 社区版**：
   - 访问 https://www.pnfsoftware.com/jeb/community-edition
   - 下载 JEB 社区版（通常是一个压缩包，如 `.zip` 或 `.7z` 格式）

2. **解压到指定目录**：
   ```bash
   # 解压下载的 JEB 压缩包
   # 将解压后的内容放到以下目录：
   deploy/docker/mcp/mcp_servers/jebmcp/jeb/
   ```
   
   确保解压后 `jeb_linux.sh` 文件位于 `deploy/docker/mcp/mcp_servers/jebmcp/jeb/jeb_linux.sh`

3. **验证安装**：
   ```bash
   # 检查 JEB 是否正确安装
   ls -la deploy/docker/mcp/mcp_servers/jebmcp/jeb/jeb_linux.sh
   ```

**注意**：JEB MCP Server 需要 Java 17+ 和 Python 3.10+ 环境，容器镜像已包含这些依赖。

### 2. 配置 Supervisor

复制示例配置文件并自定义：

```bash
cp deploy/docker/mcp/supervisor/conf.d/mcp-servers.conf.example \
   deploy/docker/mcp/supervisor/conf.d/my-mcp-server.conf
```

编辑配置文件，定义你的 MCP 服务（参考下面的配置示例）。

### 3. 启动容器

#### 构建 Docker 镜像

从项目根目录执行构建命令：

```bash
# 切换到项目根目录
cd /path/to/agent-platform

# 构建镜像（context 为项目根目录）
docker build -f deploy/docker/mcp.Dockerfile -t joysafeter-mcpserver .
```

#### 运行容器

使用 `docker run` 启动容器：

```bash
# 创建必要的本地目录（用于日志和运行时文件）
mkdir -p ./mcpserver-logs ./mcpserver-run

# 运行容器
docker run -d \
  --name joysafeter-mcpserver \
  --restart unless-stopped \
  -e BACKEND_URL=http://backend:8000 \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/deploy/docker/mcp/mcp_servers:/export/App/code \
  -v $(pwd)/deploy/docker/mcp/supervisor/conf.d:/export/App/supervisor/conf.d \
  -v $(pwd)/deploy/docker/mcp/mcpserver-logs:/export/App/logs \
  -v $(pwd)/deploy/docker/mcp/mcpserver-run:/export/App/run \
  -p 8001:8001 \
  -p 8002:8002 \
  -p 8003:8003 \
  -p 8004:8004 \
  -p 8005:8005 \
  -p 16161:16161 \
  -p 8008:8008 \
  agent-platform-mcpserver:latest
```

**参数说明**：
- `-d`: 后台运行容器
- `--name`: 容器名称
- `--restart unless-stopped`: 容器自动重启策略
- `-e`: 环境变量设置
- `-v`: 卷挂载（源代码目录、配置目录、日志目录、运行时目录）
- `-p`: 端口映射（根据实际需要的 HTTP/SSE MCP 服务器数量调整）

**注意**：
- 端口映射（`-p`）仅在使用 HTTP/SSE 传输方式的 MCP 服务器时需要
- 如果使用 stdio 传输方式，可以移除端口映射
- 确保在运行容器前已创建配置文件（参考步骤 2）

## 配置示例

### Python MCP Server (stdio transport)

假设你有一个 Python MCP 服务在 `deploy/docker/mcp/mcp_servers/python-server/`：

```ini
[program:mcp-python-example]
command=python3 /export/App/code/python-server/server.py
directory=/export/App/code/python-server
autostart=true
autorestart=true
startsecs=5
startretries=3
stopwaitsecs=10
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1",PYTHONIOENCODING="utf-8"
```

### Python MCP Server with uv

如果使用 uv 管理 Python 依赖：

```ini
[program:mcp-python-uv]
command=uv run python /export/App/code/python-server-uv/server.py
directory=/export/App/code/python-server-uv
autostart=true
autorestart=true
startsecs=5
startretries=3
environment=PYTHONUNBUFFERED="1",VIRTUAL_ENV="/export/App/code/python-server-uv/.venv",PATH="/export/App/code/python-server-uv/.venv/bin:%(ENV_PATH)s"
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
```

### FastMCP Server

使用 FastMCP 框架的服务器：

```ini
[program:mcp-fastmcp]
command=python3 -m fastmcp /export/App/code/fastmcp-server/server.py
directory=/export/App/code/fastmcp-server
autostart=true
autorestart=true
startsecs=5
startretries=3
environment=PYTHONUNBUFFERED="1"
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
```

### Node.js MCP Server (stdio transport)

```ini
[program:mcp-nodejs-example]
command=node /export/App/code/nodejs-server/index.js
directory=/export/App/code/nodejs-server
autostart=true
autorestart=true
startsecs=5
startretries=3
environment=NODE_ENV="production"
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
```

### Node.js MCP Server with npx

使用 npx 运行已发布的 MCP 服务器：

```ini
[program:mcp-nodejs-npx]
command=npx --yes @modelcontextprotocol/server-filesystem /export/App/code
directory=/export/App/code
autostart=true
autorestart=true
startsecs=5
startretries=3
environment=NODE_ENV="production"
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
```

### Python MCP Server (HTTP transport)

对于 HTTP/streamable-http 传输方式，需要暴露端口：

```ini
[program:mcp-python-http]
command=python3 -m uvicorn server:app --host 0.0.0.0 --port 8001
directory=/export/App/code/python-server-http
autostart=true
autorestart=true
startsecs=5
startretries=3
environment=PYTHONUNBUFFERED="1"
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
```

**注意**：HTTP 服务器需要：
1. 在 supervisor 配置中绑定到 `0.0.0.0`
2. 在 docker-compose.yml 中映射端口（默认端口范围：8001-8010）

### JEB MCP Server

JEB MCP Server 用于 Android APK 分析和反编译。配置示例：

```ini
[program:mcp-jeb]
command=/export/App/code/jebmcp/start_mcp_jeb.sh
directory=/export/App/code/jebmcp
autostart=true
autorestart=true
startsecs=10
startretries=3
stopwaitsecs=30
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1",JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
```

**重要提示**：
- **使用前必须下载 JEB 社区版**：访问 https://www.pnfsoftware.com/jeb/community-edition 下载，并解压到 `deploy/docker/mcp/mcp_servers/jebmcp/jeb/` 目录
- JEB Server 默认使用端口 `16161`，MCP Server 使用端口 `8008`
- 需要在 docker-compose.yml 中映射这两个端口（见上面的运行容器示例）
- 确保 `jeb_linux.sh` 文件位于 `jebmcp/jeb/` 目录下

## 管理 MCP 服务

### 查看服务状态

```bash
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf status
```

### 启动/停止/重启单个服务

```bash
# 启动
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf start mcp-python-example

# 停止
docker exec joysafeter supervisorctl -c /export/App/supervisor/supervisord.conf stop mcp-python-example

# 重启
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf restart mcp-python-example
```

### 动态添加 MCP Server（容器运行中）

容器启动后，可以直接在配置目录中添加新的配置文件，然后重新加载配置，无需重启容器。

#### 添加新的 MCP Server

1. **在配置文件目录创建新的配置文件**：

```bash
# 进入配置目录
cd deploy/docker/mcp/supervisor/conf.d

# 复制示例配置并编辑
cp mcp-servers.conf.example my-new-server.conf
# 编辑 my-new-server.conf，配置你的MCP服务器
```

2. **重新加载配置**：

```bash
# 让supervisor重新读取配置
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf reread

# 更新并启动新添加的服务
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf update
```

3. **验证新服务是否启动**：

```bash
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf status
```

#### 删除 MCP Server

1. **停止服务**（可选，supervisor会自动处理）：

```bash
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf stop my-server-name
```

2. **删除配置文件**：

```bash
rm deploy/docker/mcp/supervisor/conf.d/my-server-name.conf
```

3. **重新加载配置**：

```bash
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf reread
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf update
```

### 重新加载配置

修改现有配置文件后，重新加载：

```bash
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf reread
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf update
```

### 查看日志

容器配置为将所有日志输出到 stdout/stderr，因此可以直接使用 `docker logs` 查看：

```bash
# 查看所有日志（包括 supervisor 和所有 MCP 服务）
docker logs joysafeter-mcpserver

# 实时跟踪日志
docker logs -f joysafeter-mcpserver

# 查看最近 100 行日志
docker logs --tail 100 joysafeter-mcpserver

# 查看带时间戳的日志
docker logs -t joysafeter-mcpserver
```

**日志说明**：
- ✅ **Supervisor 日志**：supervisor 进程的启动、管理日志
- ✅ **MCP 服务日志**：所有 MCP 服务的 stdout 和 stderr 输出
- ✅ **启动脚本日志**：容器启动时的初始化日志

所有日志都会输出到 `docker logs`，方便使用 Docker 原生工具进行日志管理和监控。

## 环境变量

在 docker-compose.yml 中可以配置以下环境变量：

- `BACKEND_URL`: 后端服务URL（默认为 `http://backend:8000`）
- `TZ`: 时区（默认为 `Asia/Shanghai`）

## 端口配置

对于 HTTP/SSE 传输方式的 MCP 服务器，需要在 docker-compose.yml 中配置端口映射：

```yaml
ports:
  - "8001:8001"  # 第一个HTTP MCP服务器
  - "8002:8002"  # 第二个HTTP MCP服务器
  # ...
```

默认配置了端口范围 8001-8010，可以通过环境变量 `MCP_SERVER_PORT_START` 和 `MCP_SERVER_PORT_END` 调整。

## Volume 挂载

容器使用以下 volume：

1. **源代码目录** (`./docker/mcp/mcp_servers:/export/App/code`): 可读写挂载 MCP 服务源代码
2. **配置文件目录** (`./docker/mcp/supervisor/conf.d:/export/App/supervisor/conf.d`): 可写挂载 supervisor 配置，支持动态添加/删除 server
3. **日志目录** (`mcpserver-logs:/export/App/logs`): 持久化日志
4. **运行时目录** (`mcpserver-run:/export/App/run`): supervisor 运行时文件

## 网络配置

容器连接到 `joysafeter-network`，可以：
- 通过服务名访问其他服务（如 `backend`、`db`、`redis`）
- 被其他服务访问（通过服务名 `mcpserver`）

## 健康检查

容器配置了健康检查，检查 supervisor 是否正常运行：

```yaml
healthcheck:
  test: ["CMD", "supervisorctl", "-c", "/export/App/supervisor/supervisord.conf", "status"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

## 故障排查

### 容器无法启动

1. 检查 supervisor 配置文件语法：
```bash
docker run --rm -v $(pwd)/deploy/docker/mcp/supervisor:/export/App/supervisor \
  joysafeter-mcpserver \
  supervisord -c /export/App/supervisor/supervisord.conf -t
```

2. 查看容器日志：
```bash
docker logs joysafeter-mcpserver
```

### MCP 服务无法启动

1. 检查服务配置是否正确：
```bash
docker exec joysafeter-mcpserver supervisorctl -c /export/App/supervisor/supervisord.conf status
```

2. 查看服务日志（所有日志都会输出到 docker logs）：
```bash
docker logs joysafeter-mcpserver
```

3. 检查源代码路径是否正确（确保 volume 挂载正确）

### 端口冲突

如果 HTTP MCP 服务器端口冲突：
1. 修改 supervisor 配置中的端口号
2. 更新 docker-compose.yml 中的端口映射

## 最佳实践

1. **配置文件管理**：每个 MCP 服务使用独立的配置文件，便于管理
2. **日志管理**：配置日志轮转，避免日志文件过大
3. **资源限制**：在生产环境中配置 CPU 和内存限制
4. **健康检查**：为重要的 MCP 服务配置自定义健康检查
5. **环境变量**：使用环境变量配置敏感信息和可变参数

## 相关资源

- [Supervisor 文档](http://supervisord.org/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
