"""
AETHER-EO Temporal Intelligence & Change Detection Service
Handles:
- Bi-temporal feature differencing & change mask computation
- Multi-class change classification (Construction, Clearance, Water, Road)
- False-alarm suppression (Phenological NDVI check, SCL cloud suppression)
- Earliest Supported Change algorithm with multi-epoch persistence verification
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image

from backend.config import (
    CHANGE_CONFIDENCE_THRESHOLD, PERSISTENCE_THRESHOLD, CHANGE_CATEGORIES
)
from backend.services.quality import (
    compute_scl_quality, compute_spectral_indices, check_coregistration, calculate_composite_quality
)

class TemporalChangeEngine:
    def __init__(self):
        pass

    def analyze_temporal_pair(
        self,
        tile_t1_meta: Dict[str, Any],
        tile_t2_meta: Dict[str, Any],
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        scl_t1: Optional[np.ndarray] = None,
        scl_t2: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Compares two temporal observations T1 and T2 over the same location.
        Runs false-alarm suppression and outputs verified change intelligence.
        """
        # 1. Quality & Preprocessing Checks
        scl_qual_t1 = compute_scl_quality(scl_t1)
        scl_qual_t2 = compute_scl_quality(scl_t2)
        min_cloud_qual = min(scl_qual_t1["quality_score"], scl_qual_t2["quality_score"])

        reg_check = check_coregistration(img_t1, img_t2)

        composite_qual = calculate_composite_quality(
            cloud_quality=min_cloud_qual,
            registration_quality=reg_check["registration_score"]
        )

        # 2. Pixel & Spectral Differencing
        diff = np.abs(img_t2.astype(np.float32) - img_t1.astype(np.float32))
        mean_pixel_diff = float(np.mean(diff) / 255.0)

        # Spectral index analysis (assuming RGB or multiband)
        # Red: channel 0, Green: channel 1, Blue: channel 2
        r1, g1, b1 = img_t1[..., 0], img_t1[..., 1], img_t1[..., 2]
        r2, g2, b2 = img_t2[..., 0], img_t2[..., 1], img_t2[..., 2]

        # Proxy NIR approximation from optical brightness for spectral checks
        nir1 = np.clip(g1.astype(np.float32) * 1.2 + 20, 0, 255)
        nir2 = np.clip(g2.astype(np.float32) * 1.2 + 20, 0, 255)

        spec_t1 = compute_spectral_indices(b4_red=r1, b8_nir=nir1, b3_green=g1)
        spec_t2 = compute_spectral_indices(b4_red=r2, b8_nir=nir2, b3_green=g2)

        delta_ndvi = spec_t2["mean_ndvi"] - spec_t1["mean_ndvi"]
        brightness_increase = float(np.mean(img_t2) - np.mean(img_t1)) / 255.0

        # Structural edge/gradient difference (detects geometric construction/roads)
        grad_t1 = np.abs(np.diff(img_t1, axis=0)).mean() + np.abs(np.diff(img_t1, axis=1)).mean()
        grad_t2 = np.abs(np.diff(img_t2, axis=0)).mean() + np.abs(np.diff(img_t2, axis=1)).mean()
        delta_texture = float((grad_t2 - grad_t1) / 255.0)

        # 3. False Alarm Suppression Logic
        is_false_alarm = False
        suppression_reason = None

        # SCL Cloud / Shadow violation
        if scl_qual_t1["valid_ratio"] < 0.75 or scl_qual_t2["valid_ratio"] < 0.75:
            is_false_alarm = True
            suppression_reason = "Excluded by SCL Quality Filter (excessive cloud / shadow obscuration)"

        # Seasonal Phenology (Vegetation drying without structural change)
        elif delta_ndvi < -0.15 and delta_texture < 0.02 and not (brightness_increase > 0.35):
            is_false_alarm = True
            suppression_reason = "Suppressed: Seasonal Phenology (grass drying / harvest cycle, no structural built-up)"

        # Poor Co-Registration Shift
        elif not reg_check["aligned"]:
            is_false_alarm = True
            suppression_reason = "Flagged: Poor co-registration alignment / sub-pixel sensor artifact"

        # 4. Change Classification & Confidence
        if is_false_alarm:
            change_type = "Seasonal Phenology (False Alarm)"
            raw_confidence = max(0.1, mean_pixel_diff * 0.4)
            verified_confidence = round(raw_confidence * 0.3, 4)
            change_detected = False
        else:
            # Determine specific change category
            if delta_texture > 0.04 and brightness_increase > 0.08:
                change_type = "Construction"
                raw_confidence = min(0.98, 0.65 + delta_texture * 4.0 + brightness_increase * 0.5)
            elif delta_ndvi < -0.20 and brightness_increase > 0.05:
                change_type = "Land Clearance"
                raw_confidence = min(0.95, 0.60 + abs(delta_ndvi) * 0.8)
            elif abs(spec_t2["mean_ndwi"] - spec_t1["mean_ndwi"]) > 0.15:
                change_type = "Water Extent"
                raw_confidence = min(0.96, 0.65 + abs(spec_t2["mean_ndwi"] - spec_t1["mean_ndwi"]) * 1.2)
            elif delta_texture > 0.03:
                change_type = "Road Development"
                raw_confidence = min(0.94, 0.60 + delta_texture * 3.5)
            else:
                change_type = "Minor Surface Variation"
                raw_confidence = min(0.50, mean_pixel_diff)

            # Adjust confidence with composite quality
            verified_confidence = round(raw_confidence * composite_qual["overall_quality"], 4)
            change_detected = verified_confidence >= CHANGE_CONFIDENCE_THRESHOLD

        return {
            "change_detected": change_detected,
            "change_type": change_type,
            "raw_confidence": round(float(raw_confidence), 4),
            "adjusted_confidence": float(verified_confidence),
            "is_false_alarm": is_false_alarm,
            "suppression_reason": suppression_reason,
            "quality_assessment": composite_qual,
            "delta_metrics": {
                "mean_pixel_diff": round(mean_pixel_diff, 4),
                "delta_ndvi": round(float(delta_ndvi), 4),
                "delta_texture": round(delta_texture, 4),
                "brightness_shift": round(brightness_increase, 4)
            },
            "dates": {
                "t1_date": tile_t1_meta.get("date"),
                "t2_date": tile_t2_meta.get("date")
            }
        }

    def detect_earliest_supported_change(
        self,
        timeline_tiles: List[Dict[str, Any]],
        timeline_images: List[np.ndarray]
    ) -> Dict[str, Any]:
        """
        Analyzes a chronological sequence of observations T1, T2, ..., TN.
        Finds the earliest epoch where a change manifests AND persists in subsequent epochs.
        """
        if len(timeline_tiles) < 2:
            return {
                "earliest_supported_date": None,
                "earliest_epoch_index": -1,
                "trajectory": [],
                "persistent": False,
                "summary": "Insufficient temporal observations"
            }

        trajectory = []
        n = len(timeline_tiles)

        # Baseline T0 comparison against all subsequent Tk
        base_meta = timeline_tiles[0]
        base_img = timeline_images[0]

        for k in range(1, n):
            target_meta = timeline_tiles[k]
            target_img = timeline_images[k]

            analysis = self.analyze_temporal_pair(
                tile_t1_meta=base_meta,
                tile_t2_meta=target_meta,
                img_t1=base_img,
                img_t2=target_img
            )

            trajectory.append({
                "epoch_index": k,
                "date": target_meta.get("date"),
                "scene_id": target_meta.get("scene_id"),
                "confidence": analysis["adjusted_confidence"],
                "change_type": analysis["change_type"],
                "is_false_alarm": analysis["is_false_alarm"]
            })

        # Earliest Supported Change with Persistence Rule
        earliest_epoch = -1
        earliest_date = None
        is_persistent = False

        for i, point in enumerate(trajectory):
            if point["confidence"] >= CHANGE_CONFIDENCE_THRESHOLD and not point["is_false_alarm"]:
                # Check persistence in remaining observations
                subsequent = trajectory[i+1:]
                if not subsequent:  # Last epoch in sequence
                    earliest_epoch = point["epoch_index"]
                    earliest_date = point["date"]
                    is_persistent = True
                    break
                else:
                    mean_subsequent = np.mean([p["confidence"] for p in subsequent])
                    if mean_subsequent >= PERSISTENCE_THRESHOLD:
                        earliest_epoch = point["epoch_index"]
                        earliest_date = point["date"]
                        is_persistent = True
                        break

        return {
            "earliest_supported_date": earliest_date,
            "earliest_epoch_index": earliest_epoch,
            "persistent": is_persistent,
            "trajectory": trajectory,
            "summary": f"Earliest supported change established at {earliest_date}" if earliest_date else "No persistent change detected across epochs"
        }
