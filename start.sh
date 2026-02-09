#!/bin/bash

# AI Code Generator - Quick Start
# Starts the Gradio application with proper health checks

set -e  # Exit on error

echo "🚀 AI Code Generator - Quick Start"
echo "=================================="
echo ""

# Function to check if a service is running
check_service() {
    local url=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

# Check if vLLM is running
echo "Checking vLLM server..."
if ! curl -s http://localhost:5005/health > /dev/null 2>&1; then
    echo "⚠️  vLLM server not detected on port 5005"
    echo ""
    echo "Please start vLLM in a separate terminal:"
    echo "  conda activate vllm_oss"
    echo "  python -m vllm.entrypoints.openai.api_server --port=5005 --model openai/gpt-oss-20b"
    echo ""
    exit 1
fi
echo "✓ vLLM server is running"
echo ""

# Start Gradio App
echo "Starting Gradio application..."

# Install dependencies if needed (quietly)
echo "Ensuring dependencies are installed..."
pip install -r requirements.txt > /dev/null 2>&1
pip install -r backend/requirements.txt > /dev/null 2>&1

# Run the app
# Use nohup to keep it running if the script exits, but we usually wait
conda run -n analytics_vidhya python gradio_app.py > app.log 2>&1 &
APP_PID=$!

echo "Waiting for application to be ready..."
# Gradio usually starts on 7860
if check_service "http://localhost:7860"; then
    echo "✓ Application started (PID: $APP_PID)"
else
    echo "❌ Application failed to start"
    echo "Check app.log for errors"
    kill $APP_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ Application started successfully!"
echo ""
echo "📍 URL: http://localhost:7860"
echo ""
echo "📋 Logs: tail -f app.log"
echo ""
echo "🛑 To stop the application, press Ctrl+C or run: ./stop.sh"
echo ""

# Save PID to file for stop script
echo "$APP_PID" > .app.pid

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping application..."
    kill $APP_PID 2>/dev/null || true
    rm -f .app.pid
    echo "✓ Application stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for user interrupt
wait
