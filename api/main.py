"""FastAPI backend application for RevScan AI (Spec 8.0, Spec 12 - Member 5)."""
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any

from src.core.config import settings
from src.core.orchestrator import orchestrator
from src.core.state import state_manager
from src.knowledge.knowledge_pack import knowledge_generator
from src.core.models import (
    StartScanRequest,
    StartScanResponse,
    StopScanResponse,
    ScanStatusResponse,
    ScreensResponse,
    ScreenSummary,
    ScreenModel,
    KnowledgePackModel
)

app = FastAPI(
    title="RevScan AI API",
    description="Autonomous Android App Explorer API",
    version="1.0.0"
)

# Enable CORS for dashboard and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve screenshots directory if it exists
os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=settings.SCREENSHOT_DIR), name="screenshots")


@app.get("/")
def read_root():
    return {
        "app": "RevScan AI",
        "version": "1.0.0",
        "status": "ready"
    }


@app.post("/scan/start", response_model=StartScanResponse)
def start_scan(request: StartScanRequest):
    """Start autonomous scan for the target Android app package."""
    knowledge_generator.set_app_info(
        name=request.package_name.split(".")[-1].capitalize(),
        package=request.package_name
    )
    started = orchestrator.start_scan(request.package_name)
    if not started and state_manager.status == "running":
        return StartScanResponse(status="already_running", package_name=request.package_name)
    return StartScanResponse(status="started", package_name=request.package_name)


@app.post("/scan/stop", response_model=StopScanResponse)
def stop_scan():
    """Stop the running autonomous scan."""
    orchestrator.stop_scan()
    return StopScanResponse(status="stopped")


@app.get("/scan/status", response_model=ScanStatusResponse)
def get_scan_status():
    """Get the current scan execution status and counters."""
    return state_manager.get_status_response()


@app.get("/screens", response_model=ScreensResponse)
def get_screens():
    """Get the list of discovered screens."""
    screens_list = list(knowledge_generator.screens_map.values())
    summaries = [
        ScreenSummary(id=s.id, name=s.name, purpose=s.purpose)
        for s in screens_list
    ]
    return ScreensResponse(screens=summaries)


@app.get("/screens/{screen_id}", response_model=ScreenModel)
def get_screen(screen_id: str):
    """Get full details of a specific screen by ID."""
    if screen_id not in knowledge_generator.screens_map:
        raise HTTPException(status_code=404, detail=f"Screen '{screen_id}' not found")
    return knowledge_generator.screens_map[screen_id]


@app.get("/knowledge-pack", response_model=KnowledgePackModel)
def get_knowledge_pack():
    """Retrieve the generated App Knowledge Pack."""
    pack = knowledge_generator.generate_pack()
    return pack


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
