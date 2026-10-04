import io
import time
import numpy as np
from pathlib import Path
from PIL import Image
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from backend.config import INDEX_DIR, TILES_DIR
from backend.api.search import get_archive_index, get_embedding_engine

router = APIRouter(prefix="/ingest", tags=["Data Ingestion & Incremental Indexing"])

class IncrementalIngestRequest(BaseModel):
    scene_id: str
    sensor: str = "Sentinel-2 L2A"
    date: str
    latitude: float
    longitude: float
    category: str = "Construction"
    cloud_percentage: float = 2.5

@router.get("/stats")
def get_archive_stats():
    """Returns indexing throughput, storage footprint, and tile counts."""
    index = get_archive_index()
    index_file = INDEX_DIR / "vectors.npy"
    size_mb = round(index_file.stat().st_size / (1024 * 1024), 2) if index_file.exists() else 0.0

    return {
        "indexed_tiles_count": index.get_count(),
        "embedding_dimensions": 512,
        "vector_index_size_mb": size_mb,
        "status": "Online (Air-Gapped Ready)"
    }

@router.post("/incremental")
def incremental_ingest(req: IncrementalIngestRequest):
    """
    Demonstrates true incremental ingestion:
    Adds new tile vector to the index in real-time WITHOUT re-indexing existing tiles.
    """
    start_time = time.time()
    index = get_archive_index()
    engine = get_embedding_engine()

    tile_id = f"T_{index.get_count() + 1:06d}"
    tile_file = TILES_DIR / f"{tile_id}.png"

    # Save realistic optical chip
    try:
        from scripts.ingest import render_tile_image
        chip_img = render_tile_image(theme="river_construction", epoch_idx=3)
        chip_img.save(tile_file, "PNG")
    except Exception:
        # Fallback if render fails
        img = Image.new("RGB", (256, 256), color=(140, 160, 110))
        img.save(tile_file, "PNG")
    
    # Generate embedding based on category semantic representation
    vec = engine.encode_text(f"{req.category} near water / riverbank")
    
    meta = {
        "tile_id": tile_id,
        "scene_id": req.scene_id,
        "sensor": req.sensor,
        "date": req.date,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "cloud_percentage": req.cloud_percentage,
        "resolution": 10,
        "crs": "EPSG:4326",
        "category": req.category,
        "file_path": str(tile_file)
    }

    index.add_batch(new_vectors=vec.reshape(1, -1), new_metadata=[meta])
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "success",
        "tile_id": tile_id,
        "elapsed_ms": elapsed_ms,
        "total_tiles_now": index.get_count(),
        "message": f"Successfully ingested {tile_id} in {elapsed_ms}ms without rebuilding index"
    }

@router.post("/upload")
async def upload_real_image(
    file: UploadFile = File(...),
    location_name: str = Form("Custom Earth Observation Site"),
    latitude: float = Form(18.5204),
    longitude: float = Form(73.8567),
    date: str = Form("2026-06-15"),
    sensor: str = Form("Sentinel-2A MSI"),
    theme: str = Form("Real-World Satellite Ingestion"),
    description: str = Form("User-uploaded optical Earth Observation imagery")
):
    """
    Ingests and indexes a REAL satellite/aerial/drone image into AETHER-EO.
    Computes real feature embeddings, saves chip to tile archive,
    and updates vector index in real time.
    """
    start_time = time.time()
    index = get_archive_index()
    engine = get_embedding_engine()

    # Read uploaded image bytes
    contents = await file.read()
    try:
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    # Target 256x256 chip size
    if pil_img.size != (256, 256):
        pil_img = pil_img.resize((256, 256), Image.Resampling.LANCZOS)

    tile_id = f"T_{index.get_count() + 1:06d}"
    tile_filename = f"{tile_id}.png"
    tile_path = TILES_DIR / tile_filename
    pil_img.save(tile_path, "PNG")

    # Compute real vision-language feature embedding on actual image pixels
    img_arr = np.array(pil_img)
    vec = engine.encode_image(img_arr)

    # Blend semantic description vector for enhanced multimodal matching
    if description or theme:
        text_vec = engine.encode_text(f"{theme} {description} {location_name}")
        vec = vec * 0.7 + text_vec * 0.3
        vec = vec / np.linalg.norm(vec)

    meta = {
        "tile_id": tile_id,
        "scene_id": f"REAL_S2_{date.replace('-', '')}_{tile_id}",
        "sensor": sensor,
        "date": date,
        "year": date.split("-")[0] if "-" in date else "2026",
        "season": "Custom Ingestion",
        "location_name": location_name,
        "latitude": round(latitude, 5),
        "longitude": round(longitude, 5),
        "cloud_percentage": 0.5,
        "resolution": 10.0,
        "crs": "EPSG:4326",
        "theme": theme,
        "description": description,
        "file_path": str(tile_path),
        "is_real_upload": True
    }

    index.add_batch(new_vectors=vec.reshape(1, -1), new_metadata=[meta])
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "success",
        "tile_id": tile_id,
        "location_name": location_name,
        "date": date,
        "latitude": latitude,
        "longitude": longitude,
        "elapsed_ms": elapsed_ms,
        "total_tiles_now": index.get_count(),
        "tile_url": f"/tiles/{tile_filename}",
        "message": f"Real satellite image successfully indexed as {tile_id} in {elapsed_ms}ms!"
    }
