#!/bin/bash
# Docker 中间件停止脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$DEPLOY_DIR"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 停止服务...${NC}"
docker-compose -f docker-compose-middleware.yml down

echo -e "${GREEN}✅ 服务已停止${NC}"
echo ""
echo "提示：使用 'docker-compose -f docker-compose-middleware.yml down -v' 可删除数据卷"
