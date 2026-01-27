#!/bin/bash
# MCP Server Container Startup Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 MCP Server Container Starting...${NC}"
echo -e "${GREEN}========================================${NC}"

# Set JAVA_HOME dynamically if not already set
if [ -z "$JAVA_HOME" ]; then
    # Try to find Java installation path
    JAVA_INSTALL_PATH=$(find /usr/lib/jvm -name "java-17-openjdk-*" -type d 2>/dev/null | head -1)
    if [ -n "$JAVA_INSTALL_PATH" ]; then
        export JAVA_HOME="$JAVA_INSTALL_PATH"
        export PATH="${PATH}:${JAVA_HOME}/bin"
        echo -e "${GREEN}✅ JAVA_HOME set to: $JAVA_HOME${NC}"
    else
        # Fallback: try to get from java command
        JAVA_CMD=$(command -v java 2>/dev/null)
        if [ -n "$JAVA_CMD" ]; then
            JAVA_HOME=$(dirname "$(dirname "$(readlink -f "$JAVA_CMD" 2>/dev/null || echo "$JAVA_CMD")")")
            export JAVA_HOME
            export PATH="${PATH}:${JAVA_HOME}/bin"
            echo -e "${GREEN}✅ JAVA_HOME inferred from java command: $JAVA_HOME${NC}"
        else
            echo -e "${YELLOW}⚠️  Warning: JAVA_HOME not set and Java installation not found${NC}"
        fi
    fi
else
    export PATH="${PATH}:${JAVA_HOME}/bin"
    echo -e "${GREEN}✅ JAVA_HOME already set to: $JAVA_HOME${NC}"
fi

# Check and create necessary directories
echo -e "${YELLOW}📁 Checking directories...${NC}"
DIRS=(
    "/export/App/supervisor/conf.d"
    "/export/App/logs"
    "/export/App/run"
    "/export/App/code"
)

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}   Creating directory: $dir${NC}"
        mkdir -p "$dir"
    fi
done

# Check if supervisor config exists
if [ ! -f "/export/App/supervisor/supervisord.conf" ]; then
    echo -e "${RED}❌ Error: supervisor config not found at /export/App/supervisor/supervisord.conf${NC}"
    exit 1
fi

# Check if any MCP server configs exist
CONFIG_COUNT=$(find /export/App/supervisor/conf.d -name "*.conf" -not -name "*.example" 2>/dev/null | wc -l || echo "0")

if [ "$CONFIG_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: No MCP server configurations found in /export/App/supervisor/conf.d/${NC}"
    echo -e "${YELLOW}   Please create .conf files (copy from .example files) to run MCP servers${NC}"
    echo -e "${YELLOW}   Container will start supervisor but no MCP servers will run${NC}"
else
    echo -e "${GREEN}✅ Found $CONFIG_COUNT MCP server configuration(s)${NC}"
fi

# Clean up any existing supervisor processes and socket files
echo -e "${YELLOW}🧹 Cleaning up any existing supervisor processes...${NC}"
# Try to shutdown existing supervisor gracefully (ignore errors)
if [ -f "/export/App/run/supervisor.sock" ]; then
    supervisorctl -c /export/App/supervisor/supervisord.conf shutdown >/dev/null 2>&1 || true
    sleep 1  # Wait for graceful shutdown
fi
# Kill any remaining supervisord processes
pkill -9 -f "supervisord.*supervisord.conf" >/dev/null 2>&1 || true
# Remove socket and pid files
rm -f /export/App/run/supervisor.sock /export/App/run/supervisord.pid 2>/dev/null || true
# Also clean up default supervisor socket if it exists
rm -f /var/run/supervisor.sock /var/run/supervisord.pid 2>/dev/null || true
# Kill any processes using MCP server ports (8001-8010)
for port in {8001..8010}; do
    lsof -ti:$port 2>/dev/null | xargs kill -9 >/dev/null 2>&1 || true
done
sleep 2  # Give processes time to clean up

# Double-check that no supervisord is still running
if pgrep -f "supervisord.*supervisord.conf" > /dev/null 2>&1; then
    echo -e "${YELLOW}   Warning: Some supervisor processes may still be running, forcing kill...${NC}"
    pkill -9 -f "supervisord.*supervisord.conf" >/dev/null 2>&1 || true
    sleep 1
fi

# Validate supervisor configuration
echo -e "${YELLOW}🔍 Validating supervisor configuration...${NC}"
# If supervisor is not running, validate config file syntax
if /usr/bin/supervisord -c /export/App/supervisor/supervisord.conf -t; then
    echo -e "${GREEN}✅ Supervisor configuration syntax is valid${NC}"
else
    echo -e "${RED}❌ Error: Supervisor configuration validation failed${NC}"
    exit 1
fi

# Start supervisor
echo -e "${GREEN}🚀 Starting supervisord in foreground mode...${NC}"
echo -e "${GREEN}   All logs will be output to stdout/stderr${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Start supervisord in foreground mode (nodaemon=true in config)
# This will block and keep the container running
exec /usr/bin/supervisord -c /export/App/supervisor/supervisord.conf
