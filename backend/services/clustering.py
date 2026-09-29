"""
AETHER-EO Discovery & Clustering Service
Handles:
- Similar site discovery (K-nearest semantic neighbors)
- Dimensionality reduction & visual clustering (K-Means / PCA)
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from backend.services.retrieval import VectorArchiveIndex

class DiscoveryEngine:
    def __init__(self, index: VectorArchiveIndex):
        self.index = index

    def find_similar_sites(self, tile_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Finds locations visually and semantically similar to the specified tile.
        """
        target_idx = None
        for i, meta in enumerate(self.index.metadata):
            if meta.get("tile_id") == tile_id:
                target_idx = i
                break

        if target_idx is None or self.index.vectors.size == 0:
            return []

        target_vec = self.index.vectors[target_idx]
        # Query index
        results = self.index.search(target_vec, top_k=top_k + 1)
        # Exclude self
        filtered = [r for r in results if r.get("tile_id") != tile_id][:top_k]
        return filtered

    def compute_archive_clusters(self, n_clusters: int = 4) -> Dict[str, Any]:
        """
        Performs clustering over archive embeddings to discover macro-patterns
        (e.g., riverine networks, urban build-up, agricultural regions).
        """
        if self.index.vectors.size < n_clusters or len(self.index.metadata) < n_clusters:
            return {"clusters": [], "cluster_labels": []}

        vectors = self.index.vectors
        # 2D projection for visualization
        pca = PCA(n_components=2, random_state=42)
        coords_2d = pca.fit_transform(vectors)

        # Cluster
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        labels = kmeans.fit_predict(vectors)

        cluster_summary = []
        for c in range(n_clusters):
            member_indices = np.where(labels == c)[0]
            member_tiles = [self.index.metadata[i]["tile_id"] for i in member_indices[:5]]
            cluster_summary.append({
                "cluster_id": int(c),
                "size": int(len(member_indices)),
                "representative_tiles": member_tiles
            })

        projected_points = []
        for i, meta in enumerate(self.index.metadata):
            projected_points.append({
                "tile_id": meta.get("tile_id"),
                "x": round(float(coords_2d[i, 0]), 3),
                "y": round(float(coords_2d[i, 1]), 3),
                "cluster": int(labels[i]),
                "date": meta.get("date"),
                "latitude": meta.get("latitude"),
                "longitude": meta.get("longitude")
            })

        return {
            "cluster_summary": cluster_summary,
            "projected_points": projected_points
        }
