#!/bin/bash
# JEB 许可证自动获取和配置脚本
# 功能：从许可证数据自动生成密钥并配置到 JEB

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JEB_HOME="${JEB_HOME:-$SCRIPT_DIR/jeb}"
# 优先从 JEB 目录读取许可证数据（JEB 会在这里生成）
LICENSE_DATA_FILE="${LICENSE_DATA_FILE:-$JEB_HOME/.jeb_license_data}"
# 如果 JEB 目录不存在，尝试从脚本目录读取
if [ ! -f "$LICENSE_DATA_FILE" ]; then
    LICENSE_DATA_FILE="$SCRIPT_DIR/.jeb_license_data"
fi
JEB_CONFIG_FILE="${JEB_CONFIG_FILE:-$JEB_HOME/bin/jeb-client.cfg}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查许可证数据文件是否存在
if [ ! -f "$LICENSE_DATA_FILE" ]; then
    log_error "许可证数据文件不存在: $LICENSE_DATA_FILE"
    log_info "尝试查找其他位置的许可证数据文件..."
    # 尝试查找许可证数据文件
    POSSIBLE_FILES=(
        "$JEB_HOME/.jeb_license_data"
        "$SCRIPT_DIR/.jeb_license_data"
        "$SCRIPT_DIR/jeb/.jeb_license_data"
    )
    for file in "${POSSIBLE_FILES[@]}"; do
        if [ -f "$file" ]; then
            log_info "找到许可证数据文件: $file"
            LICENSE_DATA_FILE="$file"
            break
        fi
    done
    if [ ! -f "$LICENSE_DATA_FILE" ]; then
        log_error "未找到许可证数据文件，请先运行 JEB 以生成许可证数据文件"
        exit 1
    fi
fi

# 读取许可证数据
LICENSE_DATA=$(cat "$LICENSE_DATA_FILE" | tr -d '\n\r ')

if [ -z "$LICENSE_DATA" ]; then
    log_error "许可证数据文件为空: $LICENSE_DATA_FILE"
    exit 1
fi

log_info "读取许可证数据: ${LICENSE_DATA:0:20}..."

# 检查 curl 是否可用
if ! command -v curl >/dev/null 2>&1; then
    log_error "未找到 curl 命令，请先安装 curl"
    exit 1
fi

# 请求生成许可证密钥
log_info "正在请求生成许可证密钥..."

RESPONSE=$(curl -s 'https://www.pnfsoftware.com/genlkrequest' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Origin: https://www.pnfsoftware.com' \
  -H 'Pragma: no-cache' \
  -H 'Referer: https://www.pnfsoftware.com/genlk' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --data-raw "keyname=test&licdata=$LICENSE_DATA")

if [ $? -ne 0 ]; then
    log_error "请求失败，请检查网络连接"
    exit 1
fi

# 从 HTML 响应中提取许可证密钥
# 匹配格式: <h4>Your license key: <b>...</b></h4>
# 兼容 macOS 和 Linux 的提取方式
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS 使用 sed 提取
    LICENSE_KEY=$(echo "$RESPONSE" | sed -n 's/.*<h4>Your license key: <b>\([^<]*\)<\/b><\/h4>.*/\1/p' | head -1)
else
    # Linux 尝试使用 grep -P (如果支持)
    if echo "test" | grep -oP 'test' >/dev/null 2>&1; then
        LICENSE_KEY=$(echo "$RESPONSE" | grep -oP '<h4>Your license key: <b>\K[^<]+' | head -1)
    else
        # 回退到 sed
        LICENSE_KEY=$(echo "$RESPONSE" | sed -n 's/.*<h4>Your license key: <b>\([^<]*\)<\/b><\/h4>.*/\1/p' | head -1)
    fi
fi

# 如果还是没提取到，尝试更宽松的匹配
if [ -z "$LICENSE_KEY" ]; then
    # 尝试匹配 <b>标签内的内容，并验证格式（数字Z数字）
    LICENSE_KEY=$(echo "$RESPONSE" | grep -o '<b>[^<]*</b>' | sed 's/<b>//;s/<\/b>//' | grep -E '^[0-9]+Z[0-9]+$' | head -1)
fi

if [ -z "$LICENSE_KEY" ]; then
    log_error "未能从响应中提取许可证密钥"
    log_warn "响应内容（前500字符）:"
    echo "$RESPONSE" | head -c 500
    echo ""
    exit 1
fi

log_info "成功获取许可证密钥: $LICENSE_KEY"

# 检查 JEB 配置目录是否存在
JEB_CONFIG_DIR=$(dirname "$JEB_CONFIG_FILE")
if [ ! -d "$JEB_CONFIG_DIR" ]; then
    log_warn "JEB 配置目录不存在，正在创建: $JEB_CONFIG_DIR"
    mkdir -p "$JEB_CONFIG_DIR" || {
        log_error "无法创建配置目录: $JEB_CONFIG_DIR"
        exit 1
    }
fi

# 更新或创建配置文件
if [ -f "$JEB_CONFIG_FILE" ]; then
    log_info "更新现有配置文件: $JEB_CONFIG_FILE"
    # 如果存在 .LicenseKey 行，则更新它；否则追加
    if grep -q "^\.LicenseKey" "$JEB_CONFIG_FILE"; then
        # 使用 sed 更新（兼容 macOS 和 Linux）
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^\.LicenseKey.*|.LicenseKey = $LICENSE_KEY|" "$JEB_CONFIG_FILE"
        else
            sed -i "s|^\.LicenseKey.*|.LicenseKey = $LICENSE_KEY|" "$JEB_CONFIG_FILE"
        fi
        log_info "已更新许可证密钥"
    else
        # 追加许可证密钥
        echo ".LicenseKey = $LICENSE_KEY" >> "$JEB_CONFIG_FILE"
        log_info "已添加许可证密钥"
    fi
else
    log_info "创建新配置文件: $JEB_CONFIG_FILE"
    # 创建基本配置文件
    cat > "$JEB_CONFIG_FILE" <<EOF
.Uuid = $(date +%s)
=
.EulaAccepted = true
.FirstRun = $(date +%s)
.LastRun = $(date +%s)
.RunCount = 1
.CheckUpdates = false
.UploadErrorLogs = false
.TelemetryReporting = false
.LicenseKey = $LICENSE_KEY
.LastVersionRun = 5.34.0.202512152059
EOF
    log_info "已创建配置文件并设置许可证密钥"
fi

log_info "许可证配置完成！"
log_info "配置文件位置: $JEB_CONFIG_FILE"
log_info "许可证密钥: $LICENSE_KEY"

