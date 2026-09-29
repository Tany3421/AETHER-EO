"""
AETHER-EO Quality Assessment & False Alarm Preprocessing Service
Handles:
- Sentinel-2 SCL (Scene Classification Layer) cloud/shadow mask validation
- Spectral index calculations (NDVI, NDWI, NDBI)
- Co-registration cross-correlation check
- Composite quality score computation
"""

import numpy as np
from typing import Dict, Any, Tuple

# Sentinel-2 SCL (Scene Classification) Classes
# 0: NO_DATA, 1: SATURATED_OR_DEFECTIVE, 2: DARK_AREA_PIXELS
# 3: CLOUD_SHADOWS, 4: VEGETATION, 5: NOT_VEGETATED
# 6: WATER, 7: UNCLASSIFIED, 8: CLOUD_MEDIUM_PROBABILITY
# 9: CLOUD_HIGH_PROBABILITY, 10: THIN_CIRRUS, 11: SNOW
INVALID_SCL_CLASSES = {0, 1, 3, 8, 9, 10, 11}

def compute_scl_quality(scl_mask: np.ndarray) -> Dict[str, float]:
    """
    Evaluates SCL pixel distribution.
    Returns valid clear pixel ratio and cloud/shadow fractions.
    """
    if scl_mask is None or scl_mask.size == 0:
        return {"valid_ratio": 1.0, "cloud_ratio": 0.0, "shadow_ratio": 0.0, "quality_score": 0.95}

    total_pixels = scl_mask.size
    cloud_pixels = np.isin(scl_mask, [8, 9, 10]).sum()
    shadow_pixels = (scl_mask == 3).sum()
    invalid_pixels = np.isin(scl_mask, list(INVALID_SCL_CLASSES)).sum()

    valid_ratio = float((total_pixels - invalid_pixels) / total_pixels)
    cloud_ratio = float(cloud_pixels / total_pixels)
    shadow_ratio = float(shadow_pixels / total_pixels)
    
    # Penalize higher cloud and shadow presence
    quality_score = max(0.0, min(1.0, valid_ratio * (1.0 - cloud_ratio * 0.5 - shadow_ratio * 0.5)))

    return {
        "valid_ratio": round(valid_ratio, 4),
        "cloud_ratio": round(cloud_ratio, 4),
        "shadow_ratio": round(shadow_ratio, 4),
        "quality_score": round(quality_score, 4)
    }

def compute_spectral_indices(b4_red: np.ndarray, b8_nir: np.ndarray, b3_green: np.ndarray = None, b11_swir: np.ndarray = None) -> Dict[str, float]:
    """
    Computes mean surface reflectance indices:
    - NDVI = (NIR - Red) / (NIR + Red)
    - NDWI = (Green - NIR) / (Green + NIR)
    - NDBI = (SWIR - NIR) / (SWIR + NIR)
    """
    red = b4_red.astype(np.float32)
    nir = b8_nir.astype(np.float32)
    denom_ndvi = nir + red + 1e-6
    ndvi = (nir - red) / denom_ndvi

    ndwi_val = 0.0
    if b3_green is not None:
        green = b3_green.astype(np.float32)
        denom_ndwi = green + nir + 1e-6
        ndwi_val = float(np.nanmean((green - nir) / denom_ndwi))

    ndbi_val = 0.0
    if b11_swir is not None:
        swir = b11_swir.astype(np.float32)
        denom_ndbi = swir + nir + 1e-6
        ndbi_val = float(np.nanmean((swir - nir) / denom_ndbi))

    return {
        "mean_ndvi": round(float(np.nanmean(ndvi)), 4),
        "mean_ndwi": round(ndwi_val, 4),
        "mean_ndbi": round(ndbi_val, 4)
    }

def check_coregistration(img_t1: np.ndarray, img_t2: np.ndarray) -> Dict[str, float]:
    """
    Computes normalized cross-correlation peak to verify spatial alignment between T1 and T2.
    """
    if img_t1.shape != img_t2.shape:
        return {"registration_score": 0.5, "aligned": False}

    # Use grayscale luminance
    g1 = np.mean(img_t1, axis=-1) if img_t1.ndim == 3 else img_t1
    g2 = np.mean(img_t2, axis=-1) if img_t2.ndim == 3 else img_t2

    g1_norm = (g1 - np.mean(g1)) / (np.std(g1) + 1e-6)
    g2_norm = (g2 - np.mean(g2)) / (np.std(g2) + 1e-6)

    corr = float(np.mean(g1_norm * g2_norm))
    reg_score = max(0.0, min(1.0, (corr + 1.0) / 2.0))

    return {
        "registration_score": round(reg_score, 4),
        "aligned": reg_score > 0.65
    }

def calculate_composite_quality(
    cloud_quality: float,
    registration_quality: float,
    radiometric_quality: float = 0.92,
    sensor_compatibility: float = 0.95
) -> Dict[str, float]:
    """
    Combines individual quality metrics into a single defensible quality assessment.
    """
    weights = [0.35, 0.25, 0.20, 0.20]
    scores = [cloud_quality, registration_quality, radiometric_quality, sensor_compatibility]
    overall = sum(w * s for w, s in zip(weights, scores))

    return {
        "cloud_quality": round(cloud_quality, 4),
        "registration_quality": round(registration_quality, 4),
        "radiometric_quality": round(radiometric_quality, 4),
        "sensor_compatibility": round(sensor_compatibility, 4),
        "overall_quality": round(overall, 4)
    }
