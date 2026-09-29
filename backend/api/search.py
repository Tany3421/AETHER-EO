from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.services.retrieval import SemanticEmbeddingEngine, VectorArchiveIndex

router = APIRouter(prefix="/search", tags=["Semantic Retrieval"])

# Global singletons
_embedding_engine = SemanticEmbeddingEngine()
_vector_index = VectorArchiveIndex()

class TextSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    sensor: Optional[str] = "All"
    max_cloud: Optional[float] = 100.0
    min_date: Optional[str] = None
    max_date: Optional[str] = None

class ImageSearchRequest(BaseModel):
    tile_id: str
    top_k: int = 5

@router.post("/text")
def search_by_text(req: TextSearchRequest):
    """
    Translates a natural language query into remote sensing embedding space
    and executes top-k similarity search across indexed satellite tiles.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty")

    query_vec = _embedding_engine.encode_text(req.query)
    filters = {
        "sensor": req.sensor,
        "max_cloud": req.max_cloud,
        "min_date": req.min_date,
        "max_date": req.max_date
    }
    results = _vector_index.search(query_vec, top_k=req.top_k, filters=filters)
    return {
        "query": req.query,
        "total_indexed_tiles": _vector_index.get_count(),
        "returned_results": len(results),
        "results": results
    }

@router.post("/image")
def search_by_image(req: ImageSearchRequest):
    """
    Retrieves tiles visually and semantically similar to an existing tile.
    """
    # Find tile vector
    target_meta = next((m for m in _vector_index.metadata if m.get("tile_id") == req.tile_id), None)
    if not target_meta:
        raise HTTPException(status_code=404, detail=f"Tile '{req.tile_id}' not found in index")

    target_idx = [i for i, m in enumerate(_vector_index.metadata) if m.get("tile_id") == req.tile_id][0]
    target_vec = _vector_index.vectors[target_idx]

    raw_results = _vector_index.search(target_vec, top_k=req.top_k + 1)
    results = [r for r in raw_results if r.get("tile_id") != req.tile_id][:req.top_k]

    return {
        "target_tile_id": req.tile_id,
        "results": results
    }

def get_archive_index() -> VectorArchiveIndex:
    return _vector_index

def get_embedding_engine() -> SemanticEmbeddingEngine:
    return _embedding_engine
