#!/bin/bash

# Agent FastAPI Server Startup Script

set -e

# Configuration
HOST=${AGENT_HOST:-0.0.0.0}
PORT=${AGENT_PORT:-8000}
WORKERS=${AGENT_WORKERS:-1}
RELOAD=${AGENT_RELOAD:-false}
LOG_LEVEL=${LOG_LEVEL:-info}

echo "🚀 Starting Agent FastAPI Server"
echo "================================"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Reload: $RELOAD"
echo "Log Level: $LOG_LEVEL"
echo "================================"
echo ""

# Check if running in development mode
if [ "$RELOAD" = "true" ]; then
    echo "📝 Running in development mode (with auto-reload)"
    uvicorn agent.server:app \
        --host $HOST \
        --port $PORT \
        --reload \
        --log-level $LOG_LEVEL
else
    echo "🏭 Running in production mode"
    if [ "$WORKERS" -gt 1 ]; then
        echo "Using $WORKERS worker processes"
        gunicorn agent.server:app \
            --workers $WORKERS \
            --worker-class uvicorn.workers.UvicornWorker \
            --bind $HOST:$PORT \
            --log-level $LOG_LEVEL
    else
        echo "Using single worker process"
        uvicorn agent.server:app \
            --host $HOST \
            --port $PORT \
            --log-level $LOG_LEVEL
    fi
fi
