"""
AETHER-EO Data Ingestion & Tile Generation Script
Generates multi-temporal Sentinel-2 L2A tile simulations across 4 epochs (2023-2026)
with realistic spectral features, SCL masks, and geographic coordinates.
"""

import os
import sys
import json
import numpy as np
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw
from backend.config import TILES_DIR, INDEX_DIR, METADATA_DIR, EMBEDDING_DIM
from backend.services.retrieval import SemanticEmbeddingEngine, VectorArchiveIndex

TILES_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

# Key Demonstration Locations in India
LOCATIONS = [
    {
        "name": "Mula-Mutha Riverbank (Pune)",
        "base_lat": 18.5204,
        "base_lon": 73.8567,
        "theme": "river_construction",
        "story": "Riverbank with new industrial shed and concrete pier emerging in 2025 (Earliest Supported Change)"
    },
    {
        "name": "Godavari Basin Development (Nashik)",
        "base_lat": 19.9975,
        "base_lon": 73.7898,
        "theme": "river_road",
        "story": "Bridge and arterial road construction crossing river basin"
    },
    {
        "name": "Marathwada Agricultural Plain",
        "base_lat": 19.1383,
        "base_lon": 77.3210,
        "theme": "seasonal_phenology",
        "story": "Seasonal crop cycle (Green in Monsoon, Dry in Summer). Naive systems flag FALSE ALARM; AETHER-EO suppresses"
    },
    {
        "name": "Khadakwasla Reservoir Basin",
        "base_lat": 18.4412,
        "base_lon": 73.7622,
        "theme": "water_extent",
        "story": "Water body expansion and embankment reinforcement"
    },
    {
        "name": "Chakan Industrial Corridor",
        "base_lat": 18.7612,
        "base_lon": 73.8543,
        "theme": "industrial_complex",
        "story": "Rapid expansion of large vehicle logistics sheds and clearing"
    },
    {
        "name": "Bhimashankar Forest Boundary",
        "base_lat": 19.0722,
        "base_lon": 73.5350,
        "theme": "land_clearance",
        "story": "Illegal forest clearance and excavation along highway"
    }
]

EPOCHS = [
    {"year": "2023", "date": "2023-05-15", "season": "Pre-Monsoon (Dry)"},
    {"year": "2024", "date": "2024-05-18", "season": "Pre-Monsoon (Dry)"},
    {"year": "2025", "date": "2025-05-14", "season": "Pre-Monsoon (Dry)"},
    {"year": "2026", "date": "2026-05-12", "season": "Pre-Monsoon (Dry)"}
]

def render_tile_image(theme: str, epoch_idx: int) -> Image.Image:
    """
    Renders realistic satellite-like optical imagery (256x256) based on location theme and year.
    """
    img = Image.new("RGB", (256, 256), color=(140, 160, 110))
    draw = ImageDraw.Draw(img)

    if theme == "river_construction":
        # Base terrain: green-brown riverbank
        for y in range(256):
            c = int(100 + 20 * np.sin(y / 15.0))
            draw.line([(0, y), (255, y)], fill=(c, c + 30, c - 20))

        # Meandering river across the left/middle
        points = [(40, 0), (70, 60), (100, 130), (85, 200), (110, 256)]
        for w in range(35, 0, -1):
            draw.line(points, fill=(35, 75, 140), width=w)

        # 2023: Pure natural bank
        # 2024: Minor trail
        if epoch_idx >= 1:
            draw.line([(120, 90), (180, 110)], fill=(160, 150, 130), width=4)

        # 2025: Construction foundation appears (EARLIEST SUPPORTED)
        if epoch_idx >= 2:
            draw.rectangle([130, 95, 195, 155], fill=(210, 195, 165), outline=(180, 80, 40), width=2)
            draw.rectangle([140, 105, 160, 125], fill=(180, 180, 185))

        # 2026: Fully completed concrete industrial structure + paved pier
        if epoch_idx >= 3:
            draw.rectangle([130, 95, 210, 165], fill=(230, 235, 240), outline=(80, 80, 90), width=3)
            # Pier extending to river
            draw.line([(130, 130), (95, 135)], fill=(190, 190, 200), width=6)
            # Roof textures
            for rx in range(135, 205, 10):
                draw.line([(rx, 96), (rx, 164)], fill=(160, 170, 180), width=1)

    elif theme == "river_road":
        # River flowing horizontally
        for y in range(256):
            draw.line([(0, y), (255, y)], fill=(120, 145, 95))
        draw.line([(0, 128), (256, 128)], fill=(30, 80, 150), width=40)

        # Bridge construction
        if epoch_idx >= 2:
            # 2025: Piers
            draw.rectangle([115, 100, 140, 156], fill=(190, 190, 180))
        if epoch_idx >= 3:
            # 2026: Completed bridge road
            draw.line([(128, 0), (128, 256)], fill=(70, 70, 75), width=12)
            draw.line([(128, 0), (128, 256)], fill=(240, 240, 240), width=2)

    elif theme == "seasonal_phenology":
        # Alternates dry (pre-monsoon) vs lush
        if epoch_idx % 2 == 0:
            # Dry bare soil
            base_col = (195, 170, 130)
        else:
            # Lush crop green
            base_col = (85, 160, 65)
        img = Image.new("RGB", (256, 256), color=base_col)
        draw = ImageDraw.Draw(img)
        # Agricultural field grids
        for x in range(0, 256, 40):
            draw.line([(x, 0), (x, 256)], fill=(140, 130, 100), width=2)
        for y in range(0, 256, 50):
            draw.line([(0, y), (256, y)], fill=(140, 130, 100), width=2)

    elif theme == "water_extent":
        # Water basin expanding
        img = Image.new("RGB", (256, 256), color=(130, 140, 110))
        draw = ImageDraw.Draw(img)
        radius = 40 + epoch_idx * 25
        draw.ellipse([128 - radius, 128 - radius, 128 + radius, 128 + radius], fill=(30, 85, 165))

    elif theme == "industrial_complex":
        img = Image.new("RGB", (256, 256), color=(140, 145, 130))
        draw = ImageDraw.Draw(img)
        if epoch_idx >= 1:
            draw.rectangle([30, 30, 110, 110], fill=(210, 215, 220), outline=(50, 50, 60), width=2)
        if epoch_idx >= 2:
            draw.rectangle([130, 40, 230, 140], fill=(225, 230, 235), outline=(50, 50, 60), width=2)
        if epoch_idx >= 3:
            draw.rectangle([40, 150, 220, 230], fill=(70, 75, 80)) # asphalt parking

    elif theme == "land_clearance":
        # Forest being cleared
        img = Image.new("RGB", (256, 256), color=(45, 115, 45))
        draw = ImageDraw.Draw(img)
        if epoch_idx >= 1:
            draw.polygon([(80, 80), (180, 90), (160, 180), (70, 150)], fill=(175, 140, 100))
        if epoch_idx >= 2:
            draw.polygon([(60, 60), (210, 70), (190, 210), (50, 170)], fill=(200, 160, 110))

    # Add realistic optical noise
    arr = np.array(img, dtype=np.int16)
    noise = np.random.randint(-8, 9, arr.shape, dtype=np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def main():
    print("[Ingest] Generating multi-temporal Sentinel-2 L2A tile archive...")
    
    engine = SemanticEmbeddingEngine()
    index = VectorArchiveIndex()

    all_metadata = []
    all_vectors = []
    tile_count = 0

    for loc in LOCATIONS:
        for ep_idx, ep in enumerate(EPOCHS):
            tile_count += 1
            tile_id = f"T_{tile_count:06d}"
            scene_id = f"S2_{ep['year']}_{loc['theme']}"
            
            # Sub-tile offsets for grid coverage
            for sub_i in range(3):
                sub_tile_id = f"T_{tile_count:04d}_{sub_i+1}"
                lat = loc["base_lat"] + (sub_i * 0.002)
                lon = loc["base_lon"] + (sub_i * 0.002)

                tile_img = render_tile_image(loc["theme"], ep_idx)
                tile_filename = f"{sub_tile_id}.png"
                tile_path = TILES_DIR / tile_filename
                tile_img.save(tile_path, "PNG")

                cloud_pct = 1.2 if loc["theme"] != "cloud_obscured" else 42.0
                
                meta = {
                    "tile_id": sub_tile_id,
                    "scene_id": f"{scene_id}_tile{sub_i}",
                    "sensor": "Sentinel-2A MSI",
                    "date": ep["date"],
                    "year": ep["year"],
                    "season": ep["season"],
                    "location_name": loc["name"],
                    "latitude": round(lat, 5),
                    "longitude": round(lon, 5),
                    "cloud_percentage": cloud_pct,
                    "resolution": 10.0,
                    "crs": "EPSG:4326",
                    "theme": loc["theme"],
                    "description": loc["story"],
                    "file_path": str(tile_path)
                }

                # Compute embedding
                vec = engine.encode_image(np.array(tile_img))
                # Add location thematic semantic anchor to simulate RS pretraining
                thematic_text = f"{loc['theme']} {loc['story']}"
                text_vec = engine.encode_text(thematic_text)
                combined_vec = vec * 0.6 + text_vec * 0.4
                combined_vec = combined_vec / np.linalg.norm(combined_vec)

                all_vectors.append(combined_vec)
                all_metadata.append(meta)

    # Save to Index
    vectors_arr = np.array(all_vectors, dtype=np.float32)
    index.add_batch(vectors_arr, all_metadata)

    print(f"[Ingest] Successfully ingested {len(all_metadata)} multi-temporal Sentinel-2 tiles!")
    print(f"[Ingest] Vectors saved to: {INDEX_DIR / 'vectors.npy'}")
    print(f"[Ingest] Metadata saved to: {INDEX_DIR / 'metadata_lookup.json'}")

if __name__ == "__main__":
    main()
