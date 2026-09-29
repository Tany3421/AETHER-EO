"""
AETHER-EO Incremental Ingestion Demonstration Script
Demonstrates adding new satellite tiles to the active vector index
in real-time WITHOUT rebuilding or re-encoding existing archive vectors.
"""

import sys
import time
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import INDEX_DIR, TILES_DIR
from backend.services.retrieval import SemanticEmbeddingEngine, VectorArchiveIndex
from scripts.ingest import render_tile_image

def run_incremental_update(num_new_tiles: int = 5):
    print("=" * 60)
    print("  AETHER-EO: INCREMENTAL INGESTION TEST")
    print("=" * 60)

    index = VectorArchiveIndex()
    engine = SemanticEmbeddingEngine()

    initial_count = index.get_count()
    print(f"[*] Current Active Index: {initial_count} tiles")
    print(f"[*] Ingesting {num_new_tiles} new incoming Sentinel-2 tiles...")

    start_time = time.time()
    new_vectors = []
    new_metadata = []

    for i in range(num_new_tiles):
        tile_num = initial_count + i + 1
        tile_id = f"T_{tile_num:06d}"
        tile_img = render_tile_image(theme="river_construction", epoch_idx=3)
        tile_path = TILES_DIR / f"{tile_id}.png"
        tile_img.save(tile_path, "PNG")

        meta = {
            "tile_id": tile_id,
            "scene_id": f"S2_2026_NEW_INCOMING_{i+1}",
            "sensor": "Sentinel-2B MSI",
            "date": "2026-06-01",
            "year": "2026",
            "season": "Monsoon Inset",
            "location_name": f"Incoming AOI Sector {i+1}",
            "latitude": round(18.5204 + i * 0.001, 5),
            "longitude": round(73.8567 + i * 0.001, 5),
            "cloud_percentage": 0.8,
            "resolution": 10.0,
            "crs": "EPSG:4326",
            "theme": "river_construction",
            "description": "Incoming priority alert surveillance tile",
            "file_path": str(tile_path)
        }

        # Real-time embedding
        vec = engine.encode_image(np.array(tile_img))
        text_vec = engine.encode_text("newly built concrete structure near riverbank")
        combined_vec = vec * 0.6 + text_vec * 0.4
        combined_vec = combined_vec / np.linalg.norm(combined_vec)

        new_vectors.append(combined_vec)
        new_metadata.append(meta)

    # Ingest incrementally
    index.add_batch(np.array(new_vectors, dtype=np.float32), new_metadata)
    total_time = (time.time() - start_time) * 1000.0

    print(f"[OK] Incremental Ingestion Complete!")
    print(f"    - Existing Tiles Untouched: {initial_count}")
    print(f"    - Newly Ingested Tiles:    {num_new_tiles}")
    print(f"    - Total Archive Tiles:     {index.get_count()}")
    print(f"    - Total Time Elapsed:      {total_time:.2f} ms ({total_time/num_new_tiles:.2f} ms/tile)")
    print("=" * 60)

if __name__ == "__main__":
    run_incremental_update(num_new_tiles=6)
