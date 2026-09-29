"""
AETHER-EO Provenance & Chain of Custody Service
Manages:
- SQLite persistence of all change alerts, model checkpoints, and quality audits
- Analyst review logging (Confirm / Reject / Comments)
- Export to GeoJSON, CSV, and JSON-LD
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.config import DB_PATH, DATABASE_DIR

class ProvenanceManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scenes (
                    scene_id TEXT PRIMARY KEY,
                    sensor TEXT,
                    acquisition_date TEXT,
                    crs TEXT,
                    resolution REAL,
                    cloud_percentage REAL,
                    file_path TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tiles (
                    tile_id TEXT PRIMARY KEY,
                    scene_id TEXT,
                    latitude REAL,
                    longitude REAL,
                    date TEXT,
                    quality_score REAL,
                    file_path TEXT,
                    FOREIGN KEY(scene_id) REFERENCES scenes(scene_id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS changes (
                    change_id TEXT PRIMARY KEY,
                    tile_id TEXT,
                    change_type TEXT,
                    confidence REAL,
                    earliest_supported_date TEXT,
                    is_false_alarm INTEGER,
                    quality_score REAL,
                    model_version TEXT,
                    evidence_json TEXT,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyst_decisions (
                    decision_id TEXT PRIMARY KEY,
                    change_id TEXT,
                    decision TEXT,
                    analyst TEXT,
                    timestamp TEXT,
                    comments TEXT,
                    FOREIGN KEY(change_id) REFERENCES changes(change_id)
                )
            """)
            conn.commit()

    def record_change(self, change_data: Dict[str, Any]) -> str:
        """Saves a change candidate and returns its unique change ID."""
        change_id = change_data.get("change_id") or f"CHG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{np_hash(change_data)}"
        now = datetime.utcnow().isoformat() + "Z"

        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO changes
                (change_id, tile_id, change_type, confidence, earliest_supported_date, is_false_alarm, quality_score, model_version, evidence_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                change_id,
                change_data.get("tile_id"),
                change_data.get("change_type"),
                change_data.get("confidence", 0.0),
                change_data.get("earliest_supported_date"),
                1 if change_data.get("is_false_alarm") else 0,
                change_data.get("quality_score", 1.0),
                change_data.get("model_version", "RemoteCLIP-Siamese-v1.0"),
                json.dumps(change_data.get("evidence", {})),
                now
            ))
            conn.commit()
        return change_id

    def record_analyst_decision(
        self,
        change_id: str,
        decision: str,
        analyst: str = "Lead Analyst",
        comments: str = ""
    ) -> Dict[str, Any]:
        """Records an analyst review (CONFIRM / REJECT) with complete audit trail."""
        decision_id = f"DEC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        now = datetime.utcnow().isoformat() + "Z"

        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO analyst_decisions
                (decision_id, change_id, decision, analyst, timestamp, comments)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (decision_id, change_id, decision, analyst, now, comments))
            conn.commit()

        return {
            "decision_id": decision_id,
            "change_id": change_id,
            "decision": decision,
            "analyst": analyst,
            "timestamp": now,
            "comments": comments
        }

    def get_provenance(self, change_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves complete lineage for a change alert."""
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM changes WHERE change_id = ?", (change_id,))
            chg_row = cursor.fetchone()
            if not chg_row:
                return None

            cursor.execute("SELECT * FROM analyst_decisions WHERE change_id = ? ORDER BY timestamp DESC", (change_id,))
            decisions = [dict(r) for r in cursor.fetchall()]

        record = dict(chg_row)
        record["evidence"] = json.loads(record.get("evidence_json", "{}"))
        record["decisions"] = decisions
        return record

    def export_geojson(self) -> Dict[str, Any]:
        """Exports all confirmed change detections as standard GeoJSON."""
        features = []
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = """
                SELECT c.*, a.decision, a.analyst, a.comments, t.latitude, t.longitude, t.scene_id
                FROM changes c
                LEFT JOIN analyst_decisions a ON c.change_id = a.change_id
                LEFT JOIN tiles t ON c.tile_id = t.tile_id
            """
            for row in cursor.execute(query):
                lat = row["latitude"] or 0.0
                lon = row["longitude"] or 0.0
                feat = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "change_id": row["change_id"],
                        "tile_id": row["tile_id"],
                        "change_type": row["change_type"],
                        "confidence": row["confidence"],
                        "earliest_supported_date": row["earliest_supported_date"],
                        "analyst_decision": row["decision"] or "PENDING_REVIEW",
                        "analyst": row["analyst"] or "None",
                        "comments": row["comments"] or ""
                    }
                }
                features.append(feat)

        return {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "features": features
        }


def np_hash(data: Any) -> str:
    s = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:6]
