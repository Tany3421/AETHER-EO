# AETHER-EO: System Architecture & Engineering Blueprint
**AI-Enabled Earth Observation Retrieval & Temporal Intelligence**  
*Problem Statement: SIH26227 | Smart India Hackathon*

---

## 1. System Overview

AETHER-EO is a high-assurance, air-gapped Earth Observation intelligence platform designed to replace coordinate-and-date satellite searches with semantic intent and temporal discovery.

Analysts query high-level phenomena (e.g., *"Find newly constructed structures near riverbanks"* or upload an exemplar tile). The system indexes multi-temporal satellite imagery, filters environmental false alarms, calculates temporal confidence trajectories, isolates the earliest supported change observation, and tracks audit provenance.

```
                           ┌────────────────────────────┐
                           │      Sentinel-2 L2A        │
                           │  (B2, B3, B4, B8, SCL COG) │
                           └─────────────┬──────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │    INGESTION & TILING      │
                           │  - CRS & Geotransform      │
                           │  - 256x256 Patch Slicing   │
                           │  - SCL Quality Masking     │
                           └─────────────┬──────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
   ┌───────────────────────────┐                   ┌───────────────────────────┐
   │     SEMANTIC ENGINE       │                   │      TEMPORAL ENGINE      │
   │  - RemoteCLIP RS Embedder │                   │  - Bi-Temporal Align (T1) │
   │  - Shared 512-d Space     │                   │  - Siamese Differencing   │
   │  - FAISS IndexFlatIP      │                   │  - Change Mask Decoder    │
   └─────────────┬─────────────┘                   └─────────────┬─────────────┘
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │   FALSE-ALARM SUPPRESSION  │
                           │  - SCL Cloud/Shadow Filter │
                           │  - Phenological Invariance │
                           │  - Temporal Persistence    │
                           └─────────────┬──────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │    ANALYST WORKBENCH &     │
                           │     PROVENANCE AUDIT       │
                           │  - Interactive Map & Time  │
                           │  - Earliest Change Date    │
                           │  - Confirm / Reject Audit  │
                           │  - GeoJSON / PDF Export    │
                           └────────────────────────────┘
```

---

## 2. Directory Layout & Module Responsibilities

```text
d:\Nakshatra\SIH26227\
├── backend/
│   ├── main.py                     # FastAPI application entrypoint
│   ├── config.py                   # System configuration & directory paths
│   ├── api/
│   │   ├── search.py               # Text-to-image and image-to-image endpoints
│   │   ├── changes.py              # Temporal change analysis & earliest change API
│   │   ├── ingestion.py            # COG ingestion & incremental update endpoints
│   │   └── analyst.py              # Review feedback, confirm/reject audit logging
│   └── services/
│       ├── retrieval.py            # FAISS indexing & RemoteCLIP inference wrapper
│       ├── change_detection.py     # Siamese difference & temporal persistence rule
│       ├── quality.py              # SCL masking, NDVI validation, registration check
│       ├── clustering.py           # HDBSCAN / KMeans discovery for similar sites
│       └── provenance.py           # Immutable audit trails (SQLite/JSON-LD)
├── frontend/                       # Interactive Analyst UI (React / MapLibre / Vite)
├── data/
│   ├── raw/                        # Original multi-temporal GeoTIFF / COG scenes
│   ├── processed/                  # Standardized normalized scenes
│   ├── tiles/                      # 256x256 GeoTIFF chips with georeferencing
│   └── metadata/                   # Scene and tile JSON metadata schemas
├── index/
│   ├── faiss.index                 # Vector index for instant L2/Cosine retrieval
│   └── metadata_lookup.json        # Tile ID to geo-bounding box & timestamp mapping
├── models/
│   ├── embeddings/                 # RemoteCLIP / OpenCLIP weights
│   └── change/                     # Siamese change classifier weights
├── evaluation/
│   ├── retrieval/                  # Held-out test queries, Recall@K, MRR scripts
│   ├── change/                     # Held-out change pairs, F1, IoU, Precision/Recall
│   └── reports/                    # Benchmark measurement outputs (latency, memory)
├── scripts/
│   ├── ingest.py                   # Batch scene processor & tile extractor
│   ├── build_index.py              # Feature extraction & FAISS index generator
│   ├── incremental_update.py       # Live incremental ingestion without re-indexing
│   └── evaluate.py                 # Full metric benchmark suite
└── docs/
    ├── architecture.md             # This document
    ├── model_and_dataset_selection.md # Detailed model decision sheet
    └── provenance.md               # Audit schema and chain-of-custody specification
```

---

## 3. False Alarm Suppression Details

To prove superiority over standard difference baselines:
1. **SCL Mask Filtering:** Rejects pixels tagged in classes 3 (Cloud Shadow), 8 (Cloud Medium Prob), 9 (Cloud High Prob), 10 (Thin Cirrus), 11 (Snow/Ice).
2. **Phenological Seasonality:**
   $$\Delta \text{NDVI} = \frac{\text{B8} - \text{B4}}{\text{B8} + \text{B4}}\Big|_{T_2} - \frac{\text{B8} - \text{B4}}{\text{B8} + \text{B4}}\Big|_{T_1}$$
   If spectral shift is predominantly vegetative without increase in Normalized Difference Built-up Index (NDBI), change confidence is demoted from "Construction" to "Vegetation Phenology".
3. **Earliest Supported Change & Persistence Rule:**
   For temporal observations $T_1, T_2, \dots, T_N$, a change candidate at epoch $k$ is considered the **Earliest Supported Change** if:
   $$c(T_k) \ge \tau \quad \text{AND} \quad \frac{1}{N - k} \sum_{j=k+1}^N c(T_j) \ge \tau_{\text{persist}}$$
   This suppresses transient anomalies (such as temporary parked vehicles, seasonal water puddles, or cloud edge artifacts).

---

## 4. Air-Gapped & Offline Execution Guarantee

- Model weights are staged locally in `./models/`.
- Pre-built FAISS index binary runs in-process via C++ shared library without external socket connections.
- Map tiles are rendered from local raster/vector GeoJSON or local MBTiles server.
- All Python dependencies are bundleable into an offline wheelhouse or local Docker container.
