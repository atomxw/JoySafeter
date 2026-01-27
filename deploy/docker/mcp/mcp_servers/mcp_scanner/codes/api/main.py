"""
FastAPI 应用入口。
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import fastapi_cdn_host
from codes.api.routes import git, upload, pipeline, pi_scanner
from codes.api.mcp_server import mcp

# 读取环境变量
ENV = os.getenv("ENV", "").lower()

# 自动检测环境：如果未设置环境变量，尝试检测是否是生产环境
if not ENV:
    # 尝试检测生产环境路径是否可写
    prod_log_dir = Path('/export/Logs')
    try:
        prod_log_dir.mkdir(parents=True, exist_ok=True)
        # 如果可以创建，则判断为生产环境
        ENV = "production"
        IS_DEV = False
        LOG_DIR = prod_log_dir
    except (OSError, PermissionError):
        # 如果无法创建，则判断为开发环境
        ENV = "dev"
        IS_DEV = True
        LOG_DIR = Path(__file__).parent.parent.parent / "logs"
else:
    # 环境变量已设置，根据设置判断
    IS_DEV = ENV == "dev" or ENV == "development"
    
    # 根据环境配置日志路径
    if IS_DEV:
        # 开发环境：使用相对路径
        LOG_DIR = Path(__file__).parent.parent.parent / "logs"
    else:
        # 生产环境：使用绝对路径
        LOG_DIR = Path('/export/Logs')
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # 如果无法创建生产环境目录，回退到开发环境
            print(f"Warning: 无法创建生产环境日志目录 {LOG_DIR}，切换到开发模式: {e}")
            IS_DEV = True
            ENV = "dev"
            LOG_DIR = Path(__file__).parent.parent.parent / "logs"

# 确保日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'pull_run.log'

# 配置根 logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
    ],
    force=True  # 强制重新配置，避免被其他模块的配置覆盖
)

# 配置 uvicorn 的日志记录器
uvicorn_logger = logging.getLogger('uvicorn')
uvicorn_logger.setLevel(logging.INFO)
uvicorn_access_logger = logging.getLogger('uvicorn.access')
uvicorn_access_logger.setLevel(logging.INFO)
uvicorn_error_logger = logging.getLogger('uvicorn.error')
uvicorn_error_logger.setLevel(logging.INFO)

# 确保 uvicorn 的日志也输出到文件
for logger_name in ['uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    # 移除现有的 handlers
    logger.handlers.clear()
    # 添加文件 handler
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(file_handler)
    logger.propagate = False  # 防止传播到根 logger 造成重复

# 创建 MCP 服务器的 ASGI 应用
mcp_app = mcp.http_app(path='/mcp')

# 创建 FastAPI 应用，传入 MCP 的 lifespan
app = FastAPI(
    title="EverWhistler-MCPScan  API",
    description="提供文件上传和 Git 链接两种方式接收代码仓库进行扫描",
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)
fastapi_cdn_host.patch_docs(app, favicon_url='static/icon_s_en.svg')

# 配置 CORS（跨域资源共享）
# 根据环境变量调整允许的源
if IS_DEV:
    # 开发环境：允许所有来源
    allow_origins = ["*"]
else:
    # 生产环境：只允许特定域名
    allow_origins = ["http://joysafeter.xxx.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 注册路由
app.include_router(upload.router)
app.include_router(git.router)
app.include_router(pipeline.router)
app.include_router(pi_scanner.router)

# 挂载 MCP 服务器
app.mount("/mcp", mcp_app)


@app.get("/")
async def root() -> dict[str, str]:
    """根路径，返回 API 信息。"""
    return {
        "message": "EverWhistler-MCPScan  API",
        "version": "1.0.0",
        "environment": ENV,
        "docs": "/docs",
        "mcp": "/mcp",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查接口。"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


