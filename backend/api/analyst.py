import csv
import io
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.services.provenance import ProvenanceManager
from backend.services.clustering import DiscoveryEngine
from backend.api.search import get_archive_index

router = APIRouter(prefix="/analyst", tags=["Analyst Review & Provenance Audit"])

_provenance_manager = ProvenanceManager()

class AnalystDecisionRequest(BaseModel):
    change_id: str
    decision: str  # "CONFIRMED" or "REJECTED"
    analyst: Optional[str] = "Lead Analyst"
    comments: Optional[str] = ""

@router.post("/decision")
def submit_decision(req: AnalystDecisionRequest):
    """
    Records an analyst's decision on a change detection alert with full audit trail.
    """
    if req.decision.upper() not in ["CONFIRMED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be 'CONFIRMED' or 'REJECTED'")

    res = _provenance_manager.record_analyst_decision(
        change_id=req.change_id,
        decision=req.decision.upper(),
        analyst=req.analyst,
        comments=req.comments
    )
    return {
        "status": "success",
        "message": f"Change {req.change_id} marked as {req.decision.upper()}",
        "audit_record": res
    }

@router.get("/provenance/{change_id}")
def get_provenance(change_id: str):
    """Returns end-to-end chain-of-custody and processing history for an alert."""
    record = _provenance_manager.get_provenance(change_id)
    if not record:
        raise HTTPException(status_code=404, detail="Provenance record not found")
    return record

@router.get("/similar/{tile_id}")
def get_similar_sites(tile_id: str, top_k: int = 4):
    """Finds semantically and visually similar locations across the archive."""
    index = get_archive_index()
    engine = DiscoveryEngine(index)
    results = engine.find_similar_sites(tile_id=tile_id, top_k=top_k)
    return {
        "source_tile_id": tile_id,
        "similar_sites": results
    }

@router.get("/clusters")
def get_archive_clusters(n_clusters: int = 4):
    """Returns PCA 2D coordinates and macro-clusters across the indexed archive."""
    index = get_archive_index()
    engine = DiscoveryEngine(index)
    return engine.compute_archive_clusters(n_clusters=n_clusters)

@router.get("/export/geojson")
def export_geojson():
    """Exports all verified change intelligence as standard GeoJSON."""
    return _provenance_manager.export_geojson()

@router.get("/export/csv")
def export_csv():
    """Exports all verified alerts and decisions as a downloadable CSV."""
    geojson = _provenance_manager.export_geojson()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "change_id", "tile_id", "latitude", "longitude", "change_type",
        "confidence", "earliest_supported_date", "analyst_decision", "analyst", "comments"
    ])

    for f in geojson.get("features", []):
        props = f["properties"]
        geom = f["geometry"]["coordinates"]
        writer.writerow([
            props.get("change_id"),
            props.get("tile_id"),
            geom[1],
            geom[0],
            props.get("change_type"),
            props.get("confidence"),
            props.get("earliest_supported_date"),
            props.get("analyst_decision"),
            props.get("analyst"),
            props.get("comments")
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=aether_change_intelligence.csv"}
    )
