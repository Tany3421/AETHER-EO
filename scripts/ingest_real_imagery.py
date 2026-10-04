"""
AETHER-EO: Real Imagery Ingestion Utility
Allows ingesting real-world satellite GeoTIFFs, PNGs, or JPGs into the AETHER-EO archive.
Computes real-pixel 512-D RemoteCLIP embeddings, registers coordinates,
and immediately appends to the vector index.

Usage:
  Single image:
    python scripts/ingest_real_imagery.py --image "path/to/satellite.png" --name "Site Name" --lat 18.52 --lon 73.85 --date 2026-06-15

  Batch folder:
    python scripts/ingest_real_imagery.py --folder "data/raw/"
"""

import os
import sys
import time
import argparse
import numpy as np
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import TILES_DIR, INDEX_DIR
from backend.services.retrieval import SemanticEmbeddingEngine, VectorArchiveIndex

def ingest_single_image(
    image_path: Path,
    location_name: str,
    date: str,
    lat: float,
    lon: float,
    theme: str = "real_satellite",
    sensor: str = "Sentinel-2A MSI",
    description: str = "Real-world Earth Observation optical scene"
):
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"[!] File not found: {image_path}")
        return False

    index = VectorArchiveIndex()
    engine = SemanticEmbeddingEngine()

    start_time = time.time()
    try:
        pil_img = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"[!] Error opening image {image_path}: {e}")
        return False

    # Resize chip to 256x256
    if pil_img.size != (256, 256):
        pil_img = pil_img.resize((256, 256), Image.Resampling.LANCZOS)

    tile_id = f"T_{index.get_count() + 1:06d}"
    dest_path = TILES_DIR / f"{tile_id}.png"
    pil_img.save(dest_path, "PNG")

    # Compute real image embedding on actual pixel values
    img_arr = np.array(pil_img)
    vec = engine.encode_image(img_arr)

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
        "latitude": round(lat, 5),
        "longitude": round(lon, 5),
        "cloud_percentage": 0.5,
        "resolution": 10.0,
        "crs": "EPSG:4326",
        "theme": theme,
        "description": description,
        "file_path": str(dest_path),
        "is_real_upload": True
    }

    index.add_batch(new_vectors=vec.reshape(1, -1), new_metadata=[meta])
    elapsed_ms = (time.time() - start_time) * 1000.0

    print(f"[OK] Ingested: {image_path.name}")
    print(f"     Tile ID:      {tile_id}")
    print(f"     Location:     {location_name} ({lat}, {lon})")
    print(f"     Date:         {date}")
    print(f"     Elapsed Time: {elapsed_ms:.2f} ms")
    print(f"     Archive Size: {index.get_count()} tiles")
    return True

def ingest_folder(folder_path: Path):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"[!] Directory not found: {folder}")
        return

    extensions = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
    files = [f for f in folder.iterdir() if f.suffix.lower() in extensions]

    if not files:
        print(f"[!] No valid image files (.png, .jpg, .tif) found in {folder}")
        return

    print(f"[*] Found {len(files)} image(s) in {folder}. Ingesting...")
    for idx, f in enumerate(files):
        site_name = f.stem.replace("_", " ").title()
        ingest_single_image(
            image_path=f,
            location_name=f"Site: {site_name}",
            date="2026-06-15",
            lat=18.5204 + idx * 0.005,
            lon=73.8567 + idx * 0.005,
            theme="real_world_satellite",
            description=f"Real image chip {f.name}"
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AETHER-EO Real Imagery Ingestion")
    parser.add_argument("--image", type=str, help="Path to single image file")
    parser.add_argument("--folder", type=str, help="Path to folder of images")
    parser.add_argument("--name", type=str, default="Real EO Site", help="Location name")
    parser.add_argument("--date", type=str, default="2026-06-15", help="Acquisition date (YYYY-MM-DD)")
    parser.add_argument("--lat", type=float, default=18.5204, help="Latitude")
    parser.add_argument("--lon", type=float, default=73.8567, help="Longitude")
    parser.add_argument("--theme", type=str, default="river_construction", help="Semantic theme")
    parser.add_argument("--sensor", type=str, default="Sentinel-2A MSI", help="Sensor name")

    args = parser.parse_args()

    if args.image:
        ingest_single_image(
            image_path=Path(args.image),
            location_name=args.name,
            date=args.date,
            lat=args.lat,
            lon=args.lon,
            theme=args.theme,
            sensor=args.sensor
        )
    elif args.folder:
        ingest_folder(Path(args.folder))
    else:
        print("Please provide --image <file> or --folder <dir>. Example:")
        print("  python scripts/ingest_real_imagery.py --image sample.png --name \"Ganga Riverfront\" --lat 25.31 --lon 83.00")
