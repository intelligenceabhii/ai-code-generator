#!/bin/bash

# Stop the AI Code Generator application

echo "🛑 Stopping AI Code Generator..."

# Kill process by PID if file exists
if [ -f .app.pid ]; then
    APP_PID=$(cat .app.pid)
    kill $APP_PID 2>/dev/null || true
    rm -f .app.pid
    echo "✓ Application stopped (PID: $APP_PID)"
fi

# Also kill by process name as backup
pkill -f "python gradio_app.py" 2>/dev/null || true

echo "✅ Application stopped"
