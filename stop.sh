#!/bin/bash

# Stop all services

echo "🛑 Stopping AI Code Generator services..."

# Kill processes by PID if files exist
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null || true
    rm -f .backend.pid
    echo "✓ Backend server stopped"
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null || true
    rm -f .frontend.pid
    echo "✓ Frontend server stopped"
fi

# Also kill by process name as backup
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "✅ All services stopped"
