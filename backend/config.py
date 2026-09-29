import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
TILES_DIR = DATA_DIR / "tiles"
METADATA_DIR = DATA_DIR / "metadata"

INDEX_DIR = BASE_DIR / "index"
FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
METADATA_LOOKUP_PATH = INDEX_DIR / "metadata_lookup.json"

MODELS_DIR = BASE_DIR / "models"
RETRIEVAL_MODELS_DIR = MODELS_DIR / "embeddings"
CHANGE_MODELS_DIR = MODELS_DIR / "change"

DATABASE_DIR = BASE_DIR / "database"
DB_PATH = DATABASE_DIR / "aether_provenance.db"

EVAL_DIR = BASE_DIR / "evaluation"
REPORTS_DIR = EVAL_DIR / "reports"

# Model & Engine Parameters
EMBEDDING_DIM = 512
SIMILARITY_THRESHOLD = 0.65
CHANGE_CONFIDENCE_THRESHOLD = 0.70
PERSISTENCE_THRESHOLD = 0.60
SCL_CLEAR_PIXEL_THRESHOLD = 0.80

# Predefined Sentinel-2 Change Categories
CHANGE_CATEGORIES = [
    "Construction",
    "Land Clearance",
    "Water Extent",
    "Road Development",
    "Seasonal Phenology (False Alarm)"
]
