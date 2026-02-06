# ============================================================
# FastAPI Server for AI Code Generator
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio
from datetime import datetime

from coder import coder_agent, Code
from langchain_core.messages import HumanMessage

# ============================================================
# FastAPI App Configuration
# ============================================================

app = FastAPI(
    title="AI Code Generator API",
    description="Self-correcting code generation using LangGraph",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Request/Response Models
# ============================================================

class CodeGenerationRequest(BaseModel):
    prompt: str
    max_attempts: Optional[int] = 3
    verbose: Optional[bool] = True

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    message: str

# ============================================================
# API Endpoints
# ============================================================

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        message="AI Code Generator API is running"
    )

@app.get("/api/health", response_model=HealthResponse)
async def api_health():
    """API health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        message="API is operational"
    )

@app.post("/api/generate")
async def generate_code(request: CodeGenerationRequest):
    """
    Stream code generation events using Server-Sent Events (SSE)
    
    Event types:
    - status: Agent status updates (GENERATING, CHECKING, etc.)
    - message: Human-readable messages
    - code: Generated code solution
    - error: Error messages
    - complete: Generation completed
    """
    
    async def event_stream():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'data': 'INITIALIZING'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Track events
            event_count = 0
            last_code_solution = None
            
            # Stream agent execution
            events = coder_agent.stream(
                {
                    "messages": [HumanMessage(content=request.prompt)],
                    "attempts": 0,
                    "error_flag": "unknown",
                },
                stream_mode="values",
            )
            
            for event in events:
                event_count += 1
                
                # Extract current state
                error_flag = event.get("error_flag", "unknown")
                attempts = event.get("attempts", 0)
                code_solution = event.get("code_solution")
                
                # Determine status
                if error_flag == "unknown":
                    status = "GENERATING"
                elif error_flag == "yes":
                    status = f"RETRYING (Attempt {attempts}/3)"
                elif error_flag == "no":
                    status = "CHECKING"
                else:
                    status = "PROCESSING"
                
                # Send status update
                yield f"data: {json.dumps({'type': 'status', 'data': status, 'attempts': attempts})}\n\n"
                await asyncio.sleep(0.1)
                
                # If we have a code solution, send it
                if code_solution and code_solution != last_code_solution:
                    last_code_solution = code_solution
                    code_data = {
                        "prefix": code_solution.prefix,
                        "imports": code_solution.imports,
                        "code": code_solution.code,
                    }
                    yield f"data: {json.dumps({'type': 'code', 'data': code_data})}\n\n"
                    await asyncio.sleep(0.1)
                
                # Send messages if verbose
                if request.verbose and "messages" in event and len(event["messages"]) > 0:
                    last_message = event["messages"][-1]
                    message_content = getattr(last_message, "content", str(last_message))
                    if message_content and len(str(message_content)) < 500:  # Avoid huge messages
                        yield f"data: {json.dumps({'type': 'message', 'data': str(message_content)[:500]})}\n\n"
                        await asyncio.sleep(0.1)
            
            # Send final completion
            if last_code_solution:
                final_data = {
                    "prefix": last_code_solution.prefix,
                    "imports": last_code_solution.imports,
                    "code": last_code_solution.code,
                    "total_attempts": attempts,
                    "success": error_flag == "no",
                }
                yield f"data: {json.dumps({'type': 'complete', 'data': final_data})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'data': 'No code solution generated'})}\n\n"
                
        except Exception as e:
            error_message = f"Error during code generation: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'data': error_message})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering for nginx
        }
    )

@app.post("/api/validate")
async def validate_code(code: str):
    """
    Validate Python code syntax and imports
    """
    try:
        # Try to compile the code
        compile(code, '<string>', 'exec')
        
        # Try to execute imports
        imports_only = "\n".join([line for line in code.split("\n") if line.strip().startswith("import") or line.strip().startswith("from")])
        if imports_only:
            exec(imports_only)
        
        return {
            "valid": True,
            "message": "Code validation successful"
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error": "SyntaxError",
            "message": str(e),
            "line": e.lineno
        }
    except Exception as e:
        return {
            "valid": False,
            "error": type(e).__name__,
            "message": str(e)
        }

# ============================================================
# Run Server
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
