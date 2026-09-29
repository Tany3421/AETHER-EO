import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import TILES_DIR
from backend.api import search, changes, analyst, ingestion

app = FastAPI(
    title="AETHER-EO: AI-Enabled Earth Observation Retrieval & Temporal Intelligence",
    description="Smart India Hackathon SIH26227 - Fully Offline Sovereign Prototype",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(search.router)
app.include_router(changes.router)
app.include_router(analyst.router)
app.include_router(ingestion.router)

# Mount Satellite Tile Storage
TILES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/tiles", StaticFiles(directory=str(TILES_DIR)), name="tiles")

# Mount Static UI
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def get_workbench():
    """Serves the interactive Analyst Workbench UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "AETHER-EO Backend Online", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  AETHER-EO PROTOTYPE SERVER STARTING")
    print("  URL: http://127.0.0.1:8000")
    print("  Docs: http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
