from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import sys
import os
import uvicorn
from workflow import build_workflow, AgentState

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ResearchRequest(BaseModel):
    topic: str

class CrunchRequest(BaseModel):
    dummy: str = "" # No input needed really

# Logic to run agent in background
def run_agent(mode: str, topic: str = None, extra_data: dict = None):
    logger.info(f"Starting Agent Job: Mode={mode}, Topic={topic}")
    app_workflow = build_workflow()
    
    inputs = {
        "mode": mode,
        "topic": topic,
        "url": None,
        "html_content": None,
        "article_data": None,
        "research_context": None,
        "blog_content": None,
        "final_content": None,
        "output_files": [],
        "error": None,
    }
    
    if extra_data:
        inputs.update(extra_data) # Inject login credentials

    
    result = app_workflow.invoke(inputs)
    logger.info(f"Job Finished. Result: {result.get('output_files')}")
    # In a real app, we'd save result to DB or memory. 
    # For MVP, we just log.
    return result

from fastapi.concurrency import run_in_threadpool

# ... imports ...

# Endpoints
@app.post("/api/research")
async def start_research(req: ResearchRequest):
    # Synchronous run for MVP simplicity to return result to UI
    # We use run_in_threadpool to ensure sync_playwright runs in a thread without an event loop
    logger.info(f"Received research request: {req.topic}")
    result = await run_in_threadpool(run_agent, "research", req.topic)
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
        
    return {
        "status": "success",
        "files": result.get("output_files"),
        "content": result.get("final_content")
    }

@app.post("/api/youtube")
async def start_youtube(req: ResearchRequest):
    logger.info(f"Received YouTube request: {req.topic}")
    # Using 'research' request model since it just needs 'topic'
    result = await run_in_threadpool(run_agent, "youtube", req.topic)
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
        
    return {
        "status": "success",
        "content": result.get("final_content", "Video played.")
    }

@app.post("/api/auto-crunch")
async def start_crunch():
    logger.info("Received TechCrunch Auto request")
    result = await run_in_threadpool(run_agent, "techcrunch")
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
        
    return {
        "status": "success",
        "files": result.get("output_files"),
        "content": result.get("final_content")
    }

class LoginRequest(BaseModel):
    url: str
    username: str
    password: str

@app.post("/api/login-demo")
async def start_login_demo(req: LoginRequest):
    logger.info(f"Received Sauce Login request for {req.username} on {req.url}")
    # Pass dict as 'topic' argument? No, run_agent is string based. 
    # Better to update run_agent to accept kwargs or just pack into topic string or change signature.
    # To keep MVP simple, let's pass a JSON string or similar, OR update workflow state to take these.
    # Better: Update run_agent to accept specific args or a data dict.
    
    # Let's modify run_agent slightly in next step or use kwargs.
    # Here we will pass `req` data.
    
    result = await run_in_threadpool(run_agent, "sauce", None, req.dict()) 
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
        
    return {
        "status": "success",
        "content": result.get("final_content")
    }

# Serve UI
# Create static directory if not exists (handled by file tools later)
app.mount("/", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
