"""
AETHER-EO One-Click Prototype Launcher
Launches the local FastAPI backend server and automatically opens the
Analyst Workbench in your default web browser.
"""

import os
import sys
import time
import webbrowser
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def launch():
    import uvicorn
    from backend.config import TILES_DIR, INDEX_DIR

    print("=" * 65)
    print("           AETHER-EO: EARTH OBSERVATION INTELLIGENCE")
    print("           Smart India Hackathon Prototype (SIH26227)")
    print("=" * 65)
    print(f"[*] Project Root:   {PROJECT_ROOT}")
    print(f"[*] Status:         AIR-GAPPED & FULLY OFFLINE READY")
    print(f"[*] Server URL:     http://127.0.0.1:8000")
    print(f"[*] API Swagger:    http://127.0.0.1:8000/docs")
    print("=" * 65)

    # Open browser after a brief delay
    def open_browser():
        time.sleep(1.2)
        print("[*] Opening Analyst Workbench in web browser...")
        webbrowser.open("http://127.0.0.1:8000")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Start FastAPI server
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    launch()
