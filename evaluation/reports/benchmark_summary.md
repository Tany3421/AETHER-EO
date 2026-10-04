# AETHER-EO Performance Benchmark Report
**Execution Mode:** Air-Gapped / Offline Local Execution  
**Dataset:** Sentinel-2 L2A Multi-Temporal Archive (114 Tiles, 4 Epochs: 2023-2026)

---

### 1. Semantic Retrieval Performance
- **Recall@5:** 100.0%
- **Recall@10:** 100.0%
- **Precision@5:** 92.0%
- **Mean Reciprocal Rank (MRR):** 1.000
- **Mean Query Latency:** 0.73 ms

---

### 2. Temporal Change & False-Alarm Suppression
- **Precision:** 95.0%
- **Recall:** 95.0%
- **F1-Score:** 95.0%
- **False Alarm Rate:** 5.0% (Suppressed 10 seasonal phenology false alarms)

---

### 3. Archive & Ingestion Benchmarks
- **Total Indexed Tiles:** 114
- **Incremental Ingestion Latency:** 32.09 ms / tile (Zero index rebuilding)
- **Vector Index Footprint:** 228.1 KB
