# AETHER-EO: Provenance & Audit Trail Specification
**Problem Statement: SIH26227 | Preserving Traceability and Chain of Custody**

---

## 1. Overview
The SIH26227 specification mandates that every retrieval, change candidate, and analyst decision must maintain strict, verifiable provenance. An analyst or external auditor must be able to inspect an alert and reconstruct:
- Which raw scene and satellite sensor generated the tile.
- The exact bounding box (WGS84 lat/lon and native CRS coordinates).
- Acquisition timestamps of both $T_1$ and $T_2$ observations.
- Which preprocessing filters were applied (cloud mask, radiometric normalization, co-registration).
- The exact model name, checkpoint version, and hash used for inference.
- The human analyst's decision (Confirmed / Rejected / Flagged for Ground Truth), analyst identity, timestamp, and review remarks.

---

## 2. JSON-LD / Provenance Data Schema

Each detected change candidate stores an immutable provenance record adhering to the following structure:

```json
{
  "change_id": "CHG-2026-IND-004921",
  "created_at": "2026-09-29T14:30:00Z",
  "tile_metadata": {
    "tile_id": "T_000182",
    "spatial_extent": {
      "crs": "EPSG:4326",
      "bbox": [85.275, 23.315, 85.285, 23.325],
      "center": [23.320, 85.280]
    },
    "ground_sample_distance_m": 10.0
  },
  "temporal_observations": {
    "t1": {
      "scene_id": "S2A_MSIL2A_20241015T051011_R105",
      "sensor": "Sentinel-2A MSI",
      "acquisition_date": "2024-10-15T05:10:11Z",
      "source_provider": "Copernicus Open Access / Local COG Cache",
      "cloud_cover_percent": 1.2,
      "scl_valid_pixel_ratio": 0.985
    },
    "t2": {
      "scene_id": "S2B_MSIL2A_20251010T050929_R105",
      "sensor": "Sentinel-2B MSI",
      "acquisition_date": "2025-10-10T05:09:29Z",
      "source_provider": "Copernicus Open Access / Local COG Cache",
      "cloud_cover_percent": 2.8,
      "scl_valid_pixel_ratio": 0.971
    }
  },
  "processing_pipeline": {
    "pipeline_version": "v1.2.0-airgap",
    "preprocessing_steps": [
      "CRS validation & georeferenced tiling (256x256)",
      "SCL band cloud/shadow thresholding (>85% clear)",
      "Sub-pixel phase correlation co-registration",
      "Histogram matching radiometric normalization"
    ],
    "quality_metrics": {
      "cloud_quality_score": 0.96,
      "registration_quality_score": 0.94,
      "seasonal_similarity_score": 0.92,
      "composite_quality_score": 0.94
    }
  },
  "model_provenance": {
    "semantic_model": {
      "name": "RemoteCLIP-ViT-B/32",
      "checkpoint_hash": "sha256:7f8a9d123e456b7c...",
      "vector_dimension": 512,
      "distance_metric": "InnerProduct_Cosine"
    },
    "change_model": {
      "name": "Siamese-Temporal-ChangeNet",
      "checkpoint_hash": "sha256:3a4b5c6d7e8f...",
      "inferred_change_type": "New Construction",
      "raw_confidence": 0.91,
      "adjusted_confidence": 0.88,
      "earliest_supported_epoch": "2025-10-10"
    }
  },
  "analyst_audit_trail": {
    "status": "CONFIRMED",
    "analyst_id": "ANALYST_DELL_01",
    "reviewed_at": "2026-09-29T14:35:12Z",
    "verification_method": "High-resolution optical cross-check with 4-epoch sequence",
    "comments": "Confirmed new foundation and road access bordering water basin. Suppressed adjacent agricultural clearing as seasonal phenology.",
    "export_hash": "sha256:e1a2b3c4d5e6f7..."
  }
}
```

---

## 3. Storage and Export
1. **Local SQLite / PostGIS Audit Store:** All records are written atomically on analyst action.
2. **Standardized Export:** Analysts can export verified detections with 1 click into:
   - `GeoJSON` (for QGIS, ArcGIS, or GeoServer integration).
   - `CSV / Excel` summary reports for leadership briefings.
   - Self-contained `PDF Evidence Dossier` containing before/after imagery, spectral indices, and chain-of-custody signatures.
