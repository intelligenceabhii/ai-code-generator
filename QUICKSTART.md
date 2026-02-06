# 🚀 Quick Reference - AI Code Generator

## Start the Application

```bash
# Make sure vLLM is running first on port 5005
./start.sh
```

**Access Points:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Stop the Application

```bash
./stop.sh
```

## Test the Application

1. **Open Frontend**: Navigate to http://localhost:5173
2. **Enter Prompt**: Type a coding request, e.g., "write a function to calculate fibonacci numbers"
3. **Generate**: Click "Generate Code" or press `Cmd/Ctrl + Enter`
4. **Watch**: See real-time status updates as the agent works
5. **Use**: Copy or download the generated code

## Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Code Generator web application"

# Add your remote repository
git remote add origin <your-github-repo-url>

# Push to GitHub
git push -u origin main
```

## Project Structure

```
code-generator/
├── backend/          # FastAPI server + LangGraph agent
├── frontend/         # React UI with Monaco editor
├── start.sh          # Quick start script
├── stop.sh           # Stop all services
└── README.md         # Full documentation
```

## Troubleshooting

**Backend won't start:**
- Ensure `analytics_vidhya` conda environment is activated
- Run: `conda run -n analytics_vidhya pip install -r backend/requirements.txt`

**Frontend errors:**
- Run: `cd frontend && npm install`

**vLLM not running:**
- Start in separate terminal: `conda activate vllm_oss && python -m vllm.entrypoints.openai.api_server --port=5005 --model openai/gpt-oss-20b`

## Key Features

✨ **Self-Correcting**: Agent validates and fixes code automatically
⚡ **Real-time**: Live status updates via SSE streaming  
🎨 **Premium UI**: Modern dark mode with glassmorphism
📝 **Monaco Editor**: VS Code-like code editing
🔄 **Smart Retry**: Up to 3 attempts with error feedback
