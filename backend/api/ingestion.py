import time
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

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
        "file_path": str(TILES_DIR / f"{tile_id}.png")
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
