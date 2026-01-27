#!/bin/bash
# JEB & MCP Server 启动脚本（重构版）
# 功能分区：环境检测、参数处理、依赖安装、服务启动、端口检测与重启
# 2025-09-26

############################################################
# 资源限制设置（防止 OOM Killer）
# 在 supervisor 环境下，需要显式设置 ulimit
############################################################
# 设置虚拟内存限制为 5GB（JEB 需要 4GB，留出余量）
ulimit -v 5242880 2>/dev/null || true
# 设置物理内存限制为 5GB
ulimit -m 5242880 2>/dev/null || true
# 设置文件描述符数量
ulimit -n 65536 2>/dev/null || true
# 设置栈大小（JEB 需要 4MB 栈）
ulimit -s 4096 2>/dev/null || true

############################################################
# 环境变量设置
############################################################
# 确保 JAVA_HOME 已设置（如果未设置，尝试从 java 命令推断）
if [ -z "$JAVA_HOME" ]; then
  JAVA_CMD=$(command -v java 2>/dev/null)
  if [ -n "$JAVA_CMD" ]; then
    # 从 java 命令路径推断 JAVA_HOME
    JAVA_HOME=$(dirname "$(dirname "$(readlink -f "$JAVA_CMD" 2>/dev/null || echo "$JAVA_CMD")")")
    export JAVA_HOME
  fi
fi

# 确保 PATH 包含常用路径
export PATH="${PATH}:/usr/bin:/usr/local/bin:/usr/sbin:/sbin"

############################################################
# 获取脚本所在目录（用于相对路径）
############################################################
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

############################################################
# 参数处理与环境变量优先级
# 优先级：命令行参数 > 环境变量 > 默认
############################################################

# 默认配置（可通过环境变量或参数覆盖）
# 使用脚本所在目录作为基础路径
JEB_MCP_HOME="${JEB_MCP_HOME:-$SCRIPT_DIR}"
JEB_HOME="${JEB_HOME:-$SCRIPT_DIR/jeb}"
JEB_SERVER_PORT="${JEB_SERVER_PORT:-16161}"
JEB_MCP_PORT="${JEB_MCP_PORT:-8008}"

# 解析命令行参数
PYTHON_BIN=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --jeb-home) JEB_HOME="$2"; shift 2 ;;
    --mcp-home) JEB_MCP_HOME="$2"; shift 2 ;;
    --jeb-port) JEB_SERVER_PORT="$2"; shift 2 ;;
    --mcp-port) JEB_MCP_PORT="$2"; shift 2 ;;
    --python) PYTHON_BIN="$2"; shift 2 ;;
    *) echo "[参数处理] 未知参数: $1"; exit 1 ;;
  esac
done

# 虚拟环境路径
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# 检查并创建虚拟环境（如果不存在）
if [ ! -f "$VENV_PYTHON" ]; then
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [虚拟环境] 虚拟环境不存在，正在创建..."
  if ! command -v uv >/dev/null 2>&1; then
    echo "[虚拟环境] 错误：未找到 uv，无法创建虚拟环境。请安装 uv 或手动创建虚拟环境"
    exit 1
  fi
  cd "$SCRIPT_DIR" || { echo "[虚拟环境] 无法进入脚本目录"; exit 1; }
  uv venv .venv || { echo "[虚拟环境] 创建虚拟环境失败"; exit 1; }
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [虚拟环境] 虚拟环境创建成功 ✔"
fi

# 使用 uv sync 同步依赖（如果 pyproject.toml 存在）
if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖同步] 检测到 pyproject.toml，使用 uv sync 同步依赖..."
  cd "$SCRIPT_DIR" || { echo "[依赖同步] 无法进入脚本目录"; exit 1; }
  if command -v uv >/dev/null 2>&1; then
    # 使用 uv sync 同步所有依赖（包括 pydantic_core 等需要编译的包）
    if [ -n "$UV_INDEX_URL" ]; then
      uv sync -i "$UV_INDEX_URL" && echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖同步] 依赖同步成功 ✔" || { echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖同步] 依赖同步失败 ✗"; exit 1; }
    else
      uv sync && echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖同步] 依赖同步成功 ✔" || { echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖同步] 依赖同步失败 ✗"; exit 1; }
    fi
    # 验证关键依赖是否已正确安装
    if [ -f "$VENV_PYTHON" ]; then
      if "$VENV_PYTHON" -c "import fastmcp; import pydantic_core" >/dev/null 2>&1; then
        echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖同步] 关键依赖验证通过 ✔"
      else
        echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖同步] 警告：依赖同步完成，但关键依赖验证失败，将在后续步骤中重试"
      fi
    fi
  else
    echo "[依赖同步] 警告：未找到 uv，跳过依赖同步"
  fi
fi

# 强制使用虚拟环境中的 Python
if [ "$PYTHON_BIN" != "$VENV_PYTHON" ]; then
  if [ -n "$PYTHON_BIN" ]; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [参数处理] 警告：指定了其他 Python ($PYTHON_BIN)，但将强制使用虚拟环境: $VENV_PYTHON"
  fi
  PYTHON_BIN="$VENV_PYTHON"
fi

# 检查 Python 路径有效性
if [ ! -f "$PYTHON_BIN" ] && ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[参数处理] 错误：指定的 Python 路径不可用: $PYTHON_BIN"
  exit 1
fi

echo "[`date '+%Y-%m-%d %H:%M:%S'`] [参数处理] 启动参数："
echo "  JEB_HOME=$JEB_HOME"
echo "  JEB_MCP_HOME=$JEB_MCP_HOME"
echo "  JEB_SERVER_PORT=$JEB_SERVER_PORT"
echo "  JEB_MCP_PORT=$JEB_MCP_PORT"
echo "  PYTHON_BIN=$PYTHON_BIN"

########################################
# 环境检测
########################################
echo "[`date '+%Y-%m-%d %H:%M:%S'`] [环境检测] 开始..."

# 检查 Java 17+
if command -v java >/dev/null 2>&1; then
  JAVA_VER=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
  JAVA_MAJOR=$(echo "$JAVA_VER" | awk -F. '{if ($1=="1") print $2; else print $1}')
  if [[ "$JAVA_MAJOR" -ge 17 ]]; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [环境检测] Java 版本 $JAVA_VER (>=17) ✔"
  else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [环境检测] Java 版本 $JAVA_VER (<17) ✗，请安装 Java 17+"
    exit 1
  fi
else
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [环境检测] 未检测到 Java，请安装 Java 17+"
  exit 1
fi

# 检查 Python3 版本 >=3.10
if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PY_VER=$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
  PY_MAJOR=$("$PYTHON_BIN" -c 'import sys; print(sys.version_info[0])')
  PY_MINOR=$("$PYTHON_BIN" -c 'import sys; print(sys.version_info[1])')
  if [[ "$PY_MAJOR" -gt 3 ]] || { [[ "$PY_MAJOR" -eq 3 ]] && [[ "$PY_MINOR" -ge 10 ]]; }; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [环境检测] Python 版本 $PY_VER (>=3.10) ✔"
  else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [环境检测] Python 版本 $PY_VER (<3.10) ✗，请安装 Python >=3.10"
    exit 1
  fi
else
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [环境检测] 未检测到 Python，请安装 Python >=3.10"
  exit 1
fi

echo "[`date '+%Y-%m-%d %H:%M:%S'`] [环境检测] 通过"

########################################
# JEB 检测与下载
########################################
echo "[`date '+%Y-%m-%d %H:%M:%S'`] [JEB检测] 检查 JEB 安装..."

# 检查 JEB 是否存在（通过检查 jeb_linux.sh 文件）
JEB_SCRIPT="$JEB_HOME/jeb_linux.sh"

# 检查 JEB 是否存在
if [[ -f "$JEB_SCRIPT" ]]; then
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [JEB检测] JEB 已存在 ✔ ($JEB_SCRIPT)"
else
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [JEB检测] JEB 未找到，开始处理..."
  
  # 创建 JEB 目录
  mkdir -p "$JEB_HOME" || { echo "[JEB检测] 无法创建目录: $JEB_HOME"; exit 1; }
  
  # 检查 JEB_CE.zip 是否存在
  JEB_ARCHIVE="$SCRIPT_DIR/JEB_CE.zip"
  JEB_URL="https://www.pnfsoftware.com/dl?jeb4ce"
  
  if [[ -f "$JEB_ARCHIVE" ]]; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [JEB检测] 发现已存在的 JEB_CE.zip，直接使用: $JEB_ARCHIVE"
  else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [JEB检测] JEB_CE.zip 不存在，开始下载到: $JEB_ARCHIVE"
    if command -v wget >/dev/null 2>&1; then
      wget -O "$JEB_ARCHIVE" "$JEB_URL" || { echo "[JEB检测] 下载失败 ✗"; exit 1; }
    elif command -v curl >/dev/null 2>&1; then
      curl -L -o "$JEB_ARCHIVE" "$JEB_URL" || { echo "[JEB检测] 下载失败 ✗"; exit 1; }
    else
      echo "[JEB检测] 错误：未找到 wget 或 curl，无法下载 JEB"
      exit 1
    fi
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [JEB检测] 下载完成 ✔"
  fi
  
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [JEB检测] 开始解压..."
  
  # 检查解压工具（使用 unzip，因为下载的是 zip 格式）
  if ! command -v unzip >/dev/null 2>&1; then
    echo "[JEB检测] 错误：未找到 unzip 解压工具，请安装 unzip"
    exit 1
  fi
  EXTRACT_CMD="unzip -q"
  
  # 直接解压到 JEB_HOME 目录
  cd "$JEB_HOME" || { echo "[JEB检测] 无法进入 JEB_HOME 目录"; exit 1; }
  $EXTRACT_CMD "$JEB_ARCHIVE" >/dev/null 2>&1 || { 
    echo "[JEB检测] 解压失败 ✗"; 
    rm -f "$JEB_ARCHIVE"
    exit 1
  }
  
  # 清理下载的压缩包
  rm -f "$JEB_ARCHIVE"
  
  # 再次检查
  if [[ -f "$JEB_SCRIPT" ]]; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [JEB检测] JEB 安装成功 ✔"
    chmod +x "$JEB_SCRIPT" 2>/dev/null
  else
    echo "[JEB检测] 错误：安装后仍未找到 jeb_linux.sh"
    exit 1
  fi
fi

########################################
# 创建必要的目录
########################################
echo "[`date '+%Y-%m-%d %H:%M:%S'`] [目录准备] 创建必要的目录..."
mkdir -p "${JEB_MCP_HOME}/logs" || { echo "[目录准备] 无法创建日志目录"; exit 1; }
echo "[`date '+%Y-%m-%d %H:%M:%S'`] [目录准备] 目录准备完成 ✔"

########################################
# 依赖验证（检查关键包是否已安装）
########################################
echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 检查关键 Python 包..."
# 检查 fastmcp 和 pydantic_core 是否已正确安装
if "$PYTHON_BIN" -c "import fastmcp; import pydantic_core" >/dev/null 2>&1; then
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 关键依赖已安装 ✔"
else
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 关键依赖未正确安装，尝试重新同步..."
  # 如果使用虚拟环境且有 pyproject.toml，使用 uv sync 重新同步
  if [ -f "$SCRIPT_DIR/pyproject.toml" ] && [ "$PYTHON_BIN" = "$VENV_PYTHON" ] && command -v uv >/dev/null 2>&1; then
    cd "$SCRIPT_DIR" || { echo "[依赖验证] 无法进入脚本目录"; exit 1; }
    if [ -n "$UV_INDEX_URL" ]; then
      uv sync -i "$UV_INDEX_URL" && echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 依赖重新同步成功 ✔" || { echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 依赖重新同步失败 ✗"; exit 1; }
    else
      uv sync && echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 依赖重新同步成功 ✔" || { echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 依赖重新同步失败 ✗"; exit 1; }
    fi
    # 再次验证依赖
    if "$PYTHON_BIN" -c "import fastmcp; import pydantic_core" >/dev/null 2>&1; then
      echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 依赖重新同步后验证通过 ✔"
    else
      echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 错误：依赖重新同步后仍无法导入关键包，请检查编译环境"
      exit 1
    fi
  else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [依赖验证] 错误：无法重新同步依赖，请检查虚拟环境和 pyproject.toml"
    exit 1
  fi
fi

########################################
# 工具函数定义
########################################
function kill_port_process() {
  local port=$1
  local pids
  pids=$(lsof -i tcp:"$port" | awk 'NR>1 {print $2}' | sort | uniq)
  if [[ -n "$pids" ]]; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [端口管理] 关闭端口 $port 的进程: $pids"
    kill -9 $pids 2>/dev/null
  else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [端口管理] 端口 $port 未检测到进程"
  fi
}

function is_port_listen() {
  local port=$1
  if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    "$PYTHON_BIN" -c "import socket; import sys; s=socket.socket(); sys.exit(0) if s.connect_ex(('localhost', $port)) == 0 else sys.exit(1)" >/dev/null 2>&1 && return 0 || return 1
  fi
  if command -v lsof >/dev/null 2>&1; then
    lsof -i tcp:"$port" | grep LISTEN >/dev/null 2>&1 && return 0 || return 1
  fi
  return 1
}

function wait_for_port() {
  local port=$1
  local timeout=${2:-20}
  local count=0
  while ! is_port_listen "$port"; do
    sleep 1
    count=$((count+1))
    if [[ $count -ge $timeout ]]; then
      echo "[`date '+%Y-%m-%d %H:%M:%S'`] [端口管理] 端口 $port 未在 $timeout 秒内启动"
      return 1
    fi
  done
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [端口管理] 端口 $port 已启动"
  return 0
}

function check_and_restart_service() {
  local name="$1"
  local port="$2"
  local start_cmd="$3"
  local home="$4"
  local max_retry=3
  local count=0
  while ! is_port_listen "$port"; do
    if [[ $count -ge $max_retry ]]; then
      echo "[`date '+%Y-%m-%d %H:%M:%S'`] [$name] 端口 $port 未监听，重试 $max_retry 次后仍失败"
      return 1
    fi
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [$name] 端口 $port 未监听，尝试重启第 $((count+1)) 次"
    kill_port_process "$port"
    cd "$home" || { echo "[$name] 路径不存在: $home"; return 1; }
    eval "$start_cmd"
    sleep 5
    count=$((count+1))
  done
  echo "[`date '+%Y-%m-%d %H:%M:%S'`] [$name] 端口 $port 已监听"
  return 0
}

########################################
# JEB 许可证配置
########################################
echo "[`date '+%Y-%m-%d %H:%M:%S'`] [许可证配置] 检查 JEB 许可证..."
AUTO_LICENSE_SCRIPT="$JEB_MCP_HOME/auto_license.sh"
JEB_CONFIG_FILE="$JEB_HOME/bin/jeb-client.cfg"

# 检查是否需要配置许可证
NEED_LICENSE=false
if [ ! -f "$JEB_CONFIG_FILE" ]; then
    NEED_LICENSE=true
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [许可证配置] JEB 配置文件不存在，需要配置许可证"
elif ! grep -q "^\.LicenseKey" "$JEB_CONFIG_FILE" 2>/dev/null || [ -z "$(grep "^\.LicenseKey" "$JEB_CONFIG_FILE" | awk '{print $3}')" ]; then
    NEED_LICENSE=true
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [许可证配置] JEB 配置文件中未找到有效的许可证密钥"
fi

if [ "$NEED_LICENSE" = true ] && [ -f "$AUTO_LICENSE_SCRIPT" ]; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [许可证配置] 自动配置许可证..."
    if bash "$AUTO_LICENSE_SCRIPT" >> "${JEB_MCP_HOME}/logs/license.log" 2>&1; then
        echo "[`date '+%Y-%m-%d %H:%M:%S'`] [许可证配置] 许可证配置成功 ✔"
    else
        echo "[`date '+%Y-%m-%d %H:%M:%S'`] [许可证配置] 许可证配置失败，但继续启动（可能需要手动配置）"
    fi
elif [ "$NEED_LICENSE" = true ]; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [许可证配置] 警告：需要配置许可证，但未找到自动配置脚本: $AUTO_LICENSE_SCRIPT"
else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [许可证配置] 许可证已配置 ✔"
fi

########################################
# 服务启动流程
########################################
echo "[`date '+%Y-%m-%d %H:%M:%S'`] [服务启动] 杀死 JEB 端口进程 and MCP 端口进程 ..."
kill_port_process "$JEB_SERVER_PORT"

kill_port_process "$JEB_MCP_PORT"

echo "[`date '+%Y-%m-%d %H:%M:%S'`] [服务启动] 启动 JEB Server..."
cd "$JEB_HOME" || { echo "[服务启动] JEB_HOME 路径不存在: $JEB_HOME"; exit 1; }
nohup sh jeb_linux.sh -c --script="${JEB_MCP_HOME}/MCPc.py" >> "${JEB_MCP_HOME}/logs/jeb_start.log" 2>&1 &
sleep 2
wait_for_port "$JEB_SERVER_PORT" 120 || exit 1

echo "[`date '+%Y-%m-%d %H:%M:%S'`] [服务启动] 启动 MCP Server..."
cd "$JEB_MCP_HOME" || { echo "[服务启动] JEB_MCP_HOME 路径不存在: $JEB_MCP_HOME"; exit 1; }
nohup "$PYTHON_BIN" server.py >> "${JEB_MCP_HOME}/logs/mcp_start.log" 2>&1 &
sleep 2
wait_for_port "$JEB_MCP_PORT" 15 || exit 1

echo "[`date '+%Y-%m-%d %H:%M:%S'`] [服务启动] 启动完成！"

########################################
# 服务端口监听与自动重启
########################################
check_and_restart_service "JEB Server" "$JEB_SERVER_PORT" "nohup sh jeb_linux.sh -c --script='${JEB_MCP_HOME}/MCPc.py' >> '${JEB_MCP_HOME}/logs/jeb_start.log' 2>&1 &" "$JEB_HOME"
check_and_restart_service "MCP Server" "$JEB_MCP_PORT" "nohup $PYTHON_BIN server.py >> '${JEB_MCP_HOME}/logs/mcp_start.log' 2>&1 &" "$JEB_MCP_HOME"

########################################
# 保持脚本运行，定期检查服务状态
# 这样 supervisor 可以正确监控进程
########################################
echo "[`date '+%Y-%m-%d %H:%M:%S'`] [监控] 开始监控服务状态..."
JEB_PID=""
MCP_PID=""

# 获取进程 PID
get_service_pids() {
  JEB_PID=$(lsof -ti tcp:"$JEB_SERVER_PORT" 2>/dev/null | head -1 || echo "")
  MCP_PID=$(lsof -ti tcp:"$JEB_MCP_PORT" 2>/dev/null | head -1 || echo "")
}

# 监控循环
while true; do
  sleep 30
  get_service_pids
  
  # 检查 JEB Server
  if ! is_port_listen "$JEB_SERVER_PORT"; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [监控] JEB Server 端口 $JEB_SERVER_PORT 未监听，尝试重启..."
    kill_port_process "$JEB_SERVER_PORT"
    cd "$JEB_HOME" || continue
    nohup sh jeb_linux.sh -c --script="${JEB_MCP_HOME}/MCPc.py" >> "${JEB_MCP_HOME}/logs/jeb_start.log" 2>&1 &
    sleep 5
  fi
  
  # 检查 MCP Server
  if ! is_port_listen "$JEB_MCP_PORT"; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] [监控] MCP Server 端口 $JEB_MCP_PORT 未监听，尝试重启..."
    kill_port_process "$JEB_MCP_PORT"
    cd "$JEB_MCP_HOME" || continue
    nohup "$PYTHON_BIN" server.py >> "${JEB_MCP_HOME}/logs/mcp_start.log" 2>&1 &
    sleep 5
  fi
done
