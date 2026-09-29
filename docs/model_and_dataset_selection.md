# AETHER-EO: Model & Dataset Selection Matrix
**Project:** AI-Enabled Earth Observation Retrieval & Temporal Intelligence  
**Problem Statement:** SIH26227  
**Document Status:** Approved Architecture & Model Decision Sheet  
**Date:** September 2026

---

## 1. Executive Summary & Recommended Stack

To satisfy SIH26227 with an air-gapped, fully offline, highly defensible architecture that out-benchmarks simplistic public implementations (which rely solely on generic OpenCLIP + FAISS), we decouple the system into two specialized engines backed by Sentinel-2 L2A:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AETHER-EO ENGINE SELECTION                      │
├────────────────────────────┬───────────────────────────────────────────┤
│ Module                     │ Selected Technology / Model               │
├────────────────────────────┼───────────────────────────────────────────┤
│ Semantic Retrieval (Text)  │ RemoteCLIP (ViT-B/32 or ResNet-50)        │
│ Baseline Benchmark         │ OpenCLIP (ViT-B/32 on LAION-2B)           │
│ Change Detection Engine    │ Dual-Branch Siamese Feature Difference    │
│                            │ + Lightweight Temporal Classifier         │
│ False-Alarm Suppression    │ Sentinel-2 SCL Mask + NDVI/NDWI           │
│                            │ + Seasonal Calendar Filter + Persistence  │
│ Vector Search              │ FAISS IndexFlatIP (Cosine Similarity)     │
│ Primary Data Source        │ Sentinel-2 L2A (10m B2, B3, B4, B8 + SCL) │
│ Offline Deployment         │ Local TorchScript / ONNX + Staged Weights │
└────────────────────────────┴───────────────────────────────────────────┘
```

---

## 2. Foundation Model Comparison (Vision-Language / Semantic Retrieval)

| Evaluation Criteria | **RemoteCLIP** *(Recommended)* | **OpenCLIP (ViT-B/32)** *(Baseline)* | **Clay Foundation Model** | **Prithvi-100M (NASA/IBM)** | **SatCLIP** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Model Type** | Vision-Language (RS Aligned) | Vision-Language (General Web) | Self-Supervised MAE (Vision Only) | Temporal MAE (Vision Only) | Geo-Location CLIP |
| **Natural Language Search** | **Native** (Text Encoder + RS Image Encoder) | **Native** (Text Encoder + Generic Image Encoder) | ❌ *No* (Requires separate text projection head) | ❌ *No* (Dense segmentation / downstream only) | ❌ *No* (Coordinates to Image only) |
| **Image-to-Image Search** | ✅ Excellent (Domain-specific features) | ⚠️ Moderate (Overfits color/texture, not overhead geometry) | ✅ Excellent (Multispectral representations) | ✅ High (Multispectral features) | ⚠️ Location-biased |
| **Input Bands** | RGB (Derived from Sentinel-2 B4, B3, B2) | RGB | Multi-band (10+ bands: B2, B3, B4, B8, SWIR) | 6 HLS Bands (B2-B7) | RGB / Multispectral |
| **Offline / Air-Gapped Feasibility** | **100% Local** (~600MB weights, zero cloud calls) | **100% Local** (~600MB weights) | ⚠️ Complex (Large package dependencies, ~1.5GB) | ⚠️ Moderate (~400MB, requires custom rasterio wrapper) | Moderate |
| **Hardware (Inference)** | **CPU:** ~85 ms/tile<br>**GPU:** ~12 ms/tile (2GB VRAM) | **CPU:** ~75 ms/tile<br>**GPU:** ~10 ms/tile (2GB VRAM) | **CPU:** >450 ms/tile<br>**GPU:** ~65 ms/tile (6GB+ VRAM) | **CPU:** >350 ms/tile<br>**GPU:** ~50 ms/tile (4GB+ VRAM) | CPU: ~100 ms/tile |
| **License** | Open Academic / MIT compatible | MIT | Apache 2.0 | Apache 2.0 | MIT |
| **Why Competitors Fail Here** | Most competitors use generic OpenCLIP. RemoteCLIP understands overhead domain queries like *"river meander"*, *"quarry"*, *"bridge"*, *"sprawling industrial sheds"*. | OpenCLIP confuses nadir landforms, fails on scale, and mistakes seasonal dry vegetation for urban terrain. | Clay cannot do text queries without training an expensive cross-modal adapter, which is out of scope for air-gapped hackathons. | Prithvi is a segmentation foundation model for HLS, not a cross-modal natural language search engine. | SatCLIP maps lat/lon to image features, not natural language concepts. |

---

## 3. Change Detection Model Comparison

| Evaluation Criteria | **Siamese Difference + Temporal Head** *(Recommended)* | **ChangeFormer / BIT** | **Naive Pixel / NDVI Differencing** |
| :--- | :--- | :--- | :--- |
| **Architecture** | Dual-backbone weight-shared feature extractor with bi-temporal difference vector $\Delta = |f(T_1) - f(T_2)|$ and multi-class classifier | Bitemporal Transformer with tokenized difference attention and spatial mask decoder | Direct spectral index subtraction $\Delta \text{NDVI} = \text{NDVI}_{T_2} - \text{NDVI}_{T_1}$ |
| **Classes Supported** | 1. Construction<br>2. Land Clearance<br>3. Water Extent (Flood/Shrink)<br>4. Road / Infrastructure | Dense pixel mask for change vs no-change | Binary change threshold only |
| **Inference Footprint** | Extremely lightweight (~45 MB), runs under 30 ms on CPU | Heavy (~220 MB), requires GPU for responsive UI (>300 ms on CPU) | Instantaneous (<5 ms on CPU) |
| **False-Alarm Resistance** | **High** (Features are invariant to slight illumination and radiometric shifts) | **High** (Spatial context aware) | **Extremely Low** (Flags every seasonal shift, shadow, and haze as a change) |
| **Earliest Change Detection** | Evaluates temporal confidence trajectories: $[c(T_1, T_2), c(T_2, T_3), c(T_3, T_4)]$ with persistence rule | Can be chained sequentially across epochs | No semantic persistence |

---

## 4. Earth Observation Sensor & Dataset Selection

| Sensor / Product | Spatial Resolution | Revisit Time | Spectral Capabilities | Role in AETHER-EO | Availability & License |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sentinel-2 L2A (MSI)** *(Primary)* | **10m** (Visible + NIR: B2, B3, B4, B8)<br>20m (Red Edge + SWIR) | 5 days (constellation) | 12 bands + **SCL (Scene Classification Layer)** | **Core Engine Input**: Optical search, RGB tiles, NDVI/NDWI validation, and SCL cloud masking | Free & Open (Copernicus Open Access / AWS Open Data / CDSE) |
| **Sentinel-1 GRD (SAR)** *(Secondary / Optional)* | 10m (VV, VH polarization) | 6-12 days | C-Band Synthetic Aperture Radar | **Cloud Penetration & Structural Verification**: Robust against cloud cover and weather anomalies | Free & Open |
| **Landsat 8/9 OLI-2** | 30m multispectral (15m panchromatic) | 8-16 days | 11 spectral bands | Long historical baseline (10+ years), but 30m resolution is too coarse for detecting small new construction sites | Free & Open (USGS) |

### Why Sentinel-2 L2A is the Winning Choice for SIH26227:
1. **10-meter Ground Sample Distance (GSD):** Resolves individual buildings, highway segments, canal excavations, and riverbank structures cleanly.
2. **Built-in Quality Layer (SCL):** Sentinel-2 Level-2A includes an automated scene classification mask with dedicated classes for *Cloud High Probability*, *Cloud Medium Probability*, *Cloud Shadow*, *Cirrus*, *Water*, and *Snow/Ice*. This provides a scientifically rigorous false-alarm layer out of the box.
3. **Multi-temporal Availability:** 5-day global revisit enables dense historical sequences (e.g., 2023, 2024, 2025, 2026) over any Area of Interest (AOI) in India.

---

## 5. False-Alarm Suppression Pipeline (Key Differentiator)

Competitors get disqualified or penalized because standard image subtraction treats seasonal grass drying, sun angle changes, and thin clouds as "new construction". AETHER-EO enforces a 5-stage filter:

```
                  ┌─────────────────────────────────────────┐
                  │          Candidate Pair (T1, T2)        │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
  Stage 1: Pixel Validity Mask         │ ➔ Discard pixels with Cloud / Cloud-Shadow / Missing data
  [SCL Band Filter]                    │    (Requires >85% clear observation or auto-fallback to alternate date)
                                       │
                                       ▼
  Stage 2: Co-Registration Check       │ ➔ Phase cross-correlation check
  [Spatial Alignment]                  │    Detects sub-pixel shift; re-aligns before comparison
                                       │
                                       ▼
  Stage 3: Phenological / Seasonal     │ ➔ Compare Same-Season first (e.g., Post-Monsoon 2024 vs Post-Monsoon 2025)
  [Calendar & NDVI Invariance]         │    If NDVI decreases without built-up spectral signature (NDBI),
                                       │    flag as "Seasonal Vegetation Phenology", NOT "Clearance"
                                       │
                                       ▼
  Stage 4: Structural Feature Check    │ ➔ Deep feature difference in Siamese space
  [Deep Semantic Invariance]           │    Filters illumination, sun azimuth, and radiometric differences
                                       │
                                       ▼
  Stage 5: Multi-Epoch Persistence     │ ➔ "Earliest Supported Change" algorithm:
  [Temporal Persistence Rule]          │    Change at T_k is only confirmed if confidence persists at T_{k+1}
                                       │    Single-epoch blips are classified as "Transient Anomaly"
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       VERIFIED CHANGE INTELLIGENCE      │
                  └─────────────────────────────────────────┘
```

---

## 6. Offline / Air-Gapped Strategy & Storage Budget

The hackathon guidelines mandate that the entire stack can operate with zero internet connectivity once deployed.

### Local Storage & Dependency Footprint

| Component | Asset / Package | Size on Disk | Offline Readiness |
| :--- | :--- | :--- | :--- |
| **Vector DB** | FAISS Index (`IndexFlatIP` / `IndexIVFFlat`) | ~25 MB for 50,000 tiles | Standalone C++/Python wheel, zero network |
| **Retrieval Model** | RemoteCLIP ViT-B/32 Weights | ~600 MB (`remoteclip_vit_b32.pt`) | Stored in `./models/retrieval/` |
| **Change Model** | Siamese Classifier Weights | ~45 MB (`change_siamese.pt`) | Stored in `./models/change/` |
| **Tile Cache / Data** | Sentinel-2 COG Patches (500-2,000 demo tiles) | ~500 MB - 2 GB | Local GeoTIFF archive in `./data/processed/` |
| **Metadata & Audit** | SQLite / PostGIS Local Database | ~15 MB | Local database file / local Docker container |
| **Frontend UI** | Static React build or local Vite dev server | ~30 MB | Pre-bundled `node_modules` + local browser |
| **Total Footprint** | **Complete Portable Solution** | **< 3.5 GB** | Easily fits on an offline USB / local laptop |

---

## 7. Concrete Next Steps & Implementation Order

1. **Environment Setup:** Python 3.10+ with `torch`, `torchvision`, `open_clip_torch`, `faiss-cpu`, `rasterio`, `shapely`, `geopandas`, `fastapi`, `uvicorn`.
2. **Ingestion & Tiler (`scripts/ingest.py`):** Convert multi-temporal Sentinel-2 COGs into indexed 256x256 tiles with geo-coordinates, CRS, and SCL metadata.
3. **FAISS Index Builder (`scripts/build_index.py`):** Compute RemoteCLIP embeddings for all tiles, save FAISS index and metadata lookup table.
4. **Retrieval API (`backend/api/search.py`):** Implement natural language text search and image-to-image similarity search.
5. **Change & False Alarm Service (`backend/services/change_detection.py`):** Implement bi-temporal feature differencing, seasonal NDVI suppression, and earliest supported change tracking.
6. **Provenance & Analyst Audit (`backend/services/provenance.py`):** Full end-to-end logging of scene ID, model checkpoint, CRS, confidence, and human confirm/reject decisions.
7. **Analyst UI (`frontend/`):** Interactive map and multi-temporal timeline slider with inspection and evidence export.
