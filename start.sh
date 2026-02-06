#!/bin/bash

# AI Code Generator - Improved Quick Start Script
# Starts backend and frontend with proper health checks

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

# Start backend
echo "Starting backend server..."
cd backend
conda run -n analytics_vidhya uvicorn main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
if check_service "http://localhost:8000"; then
    echo "✓ Backend server started (PID: $BACKEND_PID)"
else
    echo "❌ Backend server failed to start"
    echo "Check backend.log for errors"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo ""

# Start frontend
echo "Starting frontend server..."
cd frontend
# Using serve dist instead of npm run dev to avoid file watcher limits (ENOSPC)
npx -y serve dist -l 5173 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
sleep 3

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📍 URLs:"
echo "   Backend API:  http://localhost:8000"
echo "   Frontend UI:  http://localhost:5173"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop all services, press Ctrl+C or run: ./stop.sh"
echo ""

# Save PIDs to file for stop script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    rm -f .backend.pid .frontend.pid
    echo "✓ All services stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for user interrupt
wait
