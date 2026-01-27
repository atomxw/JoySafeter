#!/bin/bash
# JEB 启动包装脚本，自动输入许可证密钥
# 使用方法: jeb_with_license.sh <jeb_script> [其他参数...]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JEB_HOME="${JEB_HOME:-$SCRIPT_DIR/jeb}"
JEB_CONFIG_FILE="${JEB_CONFIG_FILE:-$JEB_HOME/bin/jeb-client.cfg}"

# 从配置文件读取许可证密钥
LICENSE_KEY=""
if [ -f "$JEB_CONFIG_FILE" ]; then
    LICENSE_KEY=$(grep "^\.LicenseKey" "$JEB_CONFIG_FILE" | awk '{print $3}' | tr -d '\n\r ' 2>/dev/null || echo "")
fi

# 如果配置文件中没有密钥，尝试运行自动配置脚本
if [ -z "$LICENSE_KEY" ]; then
    AUTO_LICENSE_SCRIPT="$SCRIPT_DIR/auto_license.sh"
    if [ -f "$AUTO_LICENSE_SCRIPT" ]; then
        echo "[INFO] 未找到许可证密钥，尝试自动配置..." >&2
        if bash "$AUTO_LICENSE_SCRIPT" >/dev/null 2>&1; then
            LICENSE_KEY=$(grep "^\.LicenseKey" "$JEB_CONFIG_FILE" | awk '{print $3}' | tr -d '\n\r ' 2>/dev/null || echo "")
        fi
    fi
fi

# 如果还是没有密钥，尝试使用 expect（如果可用）
if [ -z "$LICENSE_KEY" ]; then
    echo "警告: 未找到许可证密钥，JEB 将提示手动输入" >&2
    # 直接执行 JEB 脚本，让用户手动输入
    exec "$@"
fi

echo "[INFO] 使用许可证密钥: ${LICENSE_KEY:0:20}..." >&2

# 检查 expect 是否可用
if command -v expect >/dev/null 2>&1; then
    # 使用 expect 自动输入许可证密钥
    expect <<EOF
set timeout 60
log_user 0
spawn "$@"
expect {
    -re "Input your license key:|输入您的许可证密钥:" {
        send "$LICENSE_KEY\r"
        exp_continue
    }
    -re "License key error|许可证密钥错误" {
        puts stderr "错误: 许可证密钥无效"
        exit 1
    }
    -re "\\[MCP\\] Server started|Server started at" {
        # JEB 启动成功，继续运行
        set timeout -1
        interact
    }
    timeout {
        # 超时后继续运行（JEB 可能在后台运行）
        set timeout -1
        interact
    }
    eof {
        catch wait result
        set exit_code [lindex \$result 3]
        if {\$exit_code == ""} { set exit_code 0 }
        exit \$exit_code
    }
}
EOF
else
    # 如果没有 expect，尝试使用简单的管道输入（可能不够可靠）
    echo "警告: 未找到 expect，尝试使用管道输入密钥（可能不够可靠）" >&2
    echo "$LICENSE_KEY" | "$@"
fi

