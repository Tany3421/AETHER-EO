"""
AETHER-EO: SIH 2026 6-Slide Presentation Generator
Generates a widescreen 16:9 PowerPoint file adhering exactly to the official
Smart India Hackathon format and layout styling demonstrated in the reference template.
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    NAVY = RGBColor(15, 30, 70)
    DARK_BLUE = RGBColor(26, 54, 93)
    EMERALD = RGBColor(16, 120, 75)
    LIGHT_GREEN_BG = RGBColor(235, 248, 240)
    CARD_BORDER = RGBColor(180, 220, 195)
    GRAY_TEXT = RGBColor(70, 80, 95)
    DARK_TEXT = RGBColor(30, 41, 59)
    WHITE = RGBColor(255, 255, 255)
    LIGHT_GRAY_BG = RGBColor(245, 247, 250)
    ACCENT_AMBER = RGBColor(180, 100, 20)
    AMBER_BG = RGBColor(254, 243, 199)

    blank_layout = prs.slide_layouts[6]

    # Helper: Add Slide Header
    def add_header(slide, title_text, slide_num):
        # Header title
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(9.5), Inches(0.8))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = DARK_BLUE

        # SIH Top-Right Logo Text
        sih_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.3), Inches(2.2), Inches(0.8))
        stf = sih_box.text_frame
        sp = stf.paragraphs[0]
        sp.text = "SMART INDIA\nHACKATHON 2026"
        sp.font.size = Pt(13)
        sp.font.bold = True
        sp.font.color.rgb = NAVY
        sp.alignment = PP_ALIGN.RIGHT

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.7), Inches(0.4))
        ftf = footer_box.text_frame
        fp = ftf.paragraphs[0]
        fp.text = "AETHER-EO | AI-Enabled Earth Observation Retrieval & Temporal Intelligence"
        fp.font.size = Pt(10)
        fp.font.color.rgb = GRAY_TEXT

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(12.2), Inches(7.05), Inches(0.6), Inches(0.4))
        np_frame = num_box.text_frame
        np_p = np_frame.paragraphs[0]
        np_p.text = str(slide_num)
        np_p.font.size = Pt(11)
        np_p.font.bold = True
        np_p.font.color.rgb = DARK_BLUE
        np_p.alignment = PP_ALIGN.RIGHT

    # ==========================================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================================
    s1 = prs.slides.add_slide(blank_layout)

    # Big Header
    title_box = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(1.0))
    tf1 = title_box.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "SMART INDIA HACKATHON 2026"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = DARK_BLUE
    p1.alignment = PP_ALIGN.CENTER

    # Right SIH Badge
    sih_badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.8), Inches(0.6), Inches(1.8), Inches(1.0))
    sih_badge.fill.solid()
    sih_badge.fill.fore_color.rgb = AMBER_BG
    sih_badge.line.color.rgb = ACCENT_AMBER
    sih_tf = sih_badge.text_frame
    sih_p = sih_tf.paragraphs[0]
    sih_p.text = "SIH 2026\nOFFICIAL"
    sih_p.font.size = Pt(12)
    sih_p.font.bold = True
    sih_p.font.color.rgb = ACCENT_AMBER
    sih_p.alignment = PP_ALIGN.CENTER

    # Left Metadata Box
    meta_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.0), Inches(6.8), Inches(4.7))
    meta_box.fill.solid()
    meta_box.fill.fore_color.rgb = LIGHT_GRAY_BG
    meta_box.line.color.rgb = RGBColor(210, 220, 230)
    mtf = meta_box.text_frame
    mtf.word_wrap = True

    fields = [
        ("Problem Statement ID", "SIH26227"),
        ("Problem Statement Title", "AI-Enabled Earth Observation Retrieval &\nTemporal Intelligence (AETHER-EO)"),
        ("Theme", "Space Technology"),
        ("PS Category", "Software"),
        ("Deployment Requirement", "100% Air-Gapped / Disconnected Network"),
        ("Team ID", "[Your Team ID]"),
        ("Team Name (Registered)", "[Your Team Name]")
    ]

    for i, (k, v) in enumerate(fields):
        p = mtf.paragraphs[0] if i == 0 else mtf.add_paragraph()
        p.space_after = Pt(12)
        run_k = p.add_run()
        run_k.text = f"•  {k}: "
        run_k.font.bold = True
        run_k.font.size = Pt(14)
        run_k.font.color.rgb = NAVY

        run_v = p.add_run()
        run_v.text = v
        run_v.font.size = Pt(14)
        run_v.font.color.rgb = DARK_TEXT

    # Right Hero Banner / Innovation Card
    hero = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.8), Inches(2.0), Inches(4.7), Inches(4.7))
    hero.fill.solid()
    hero.fill.fore_color.rgb = LIGHT_GREEN_BG
    hero.line.color.rgb = CARD_BORDER
    htf = hero.text_frame
    htf.word_wrap = True

    hp1 = htf.paragraphs[0]
    hp1.text = "AETHER-EO"
    hp1.font.size = Pt(28)
    hp1.font.bold = True
    hp1.font.color.rgb = EMERALD
    hp1.alignment = PP_ALIGN.CENTER

    hp2 = htf.add_paragraph()
    hp2.text = "Search by Meaning. Discover by Similarity.\nUnderstand Change."
    hp2.font.size = Pt(13)
    hp2.font.bold = True
    hp2.font.color.rgb = DARK_TEXT
    hp2.alignment = PP_ALIGN.CENTER
    hp2.space_after = Pt(16)

    highlights = [
        "Reverses satellite catalog search from coordinate-based to semantic natural language intent.",
        "Detects earliest supported change across multi-epoch sequences with temporal persistence.",
        "Suppresses false alarms (seasonal phenology, SCL cloud & shadows, coregistration shifts).",
        "Provides cryptographic JSON-LD provenance and one-click analyst audit trails.",
        "Tested 100% operational in air-gapped environment with zero cloud dependencies."
    ]

    for hl in highlights:
        hp = htf.add_paragraph()
        hp.text = f"✔  {hl}"
        hp.font.size = Pt(11)
        hp.font.color.rgb = DARK_TEXT
        hp.space_after = Pt(8)

    # ==========================================================
    # SLIDE 2: PROBLEM STATEMENT & PROPOSED SOLUTION
    # ==========================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Problem Statement & Proposed Solution", 2)

    # Left: Problem Statement & Existing Challenges
    prob_card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.5))
    prob_card.fill.solid()
    prob_card.fill.fore_color.rgb = LIGHT_GRAY_BG
    prob_card.line.color.rgb = RGBColor(220, 180, 180)
    ptf = prob_card.text_frame
    ptf.word_wrap = True

    pp1 = ptf.paragraphs[0]
    pp1.text = "⚠️  THE PROBLEM IN SATELLITE CATALOGUES"
    pp1.font.size = Pt(14)
    pp1.font.bold = True
    pp1.font.color.rgb = RGBColor(180, 40, 40)
    pp1.space_after = Pt(10)

    pp2 = ptf.add_paragraph()
    pp2.text = "Current Earth Observation portals require analysts to already know WHERE and WHEN to look (filtering by latitude, longitude, and dates). Analysts cannot query by high-level semantic intent like \"Find newly constructed structures near riverbanks\"."
    pp2.font.size = Pt(11)
    pp2.font.color.rgb = DARK_TEXT
    pp2.space_after = Pt(14)

    pp3 = ptf.add_paragraph()
    pp3.text = "EXISTING CHALLENGES"
    pp3.font.size = Pt(13)
    pp3.font.bold = True
    pp3.font.color.rgb = NAVY
    pp3.space_after = Pt(8)

    challenges = [
        "Coordinate Bottleneck: Analyst must manually locate candidate sites without semantic search assistance.",
        "Rampant False Alarms: Naive pixel difference systems confuse seasonal crop harvesting, dry grass, and cloud shadows with real construction.",
        "Transient Blips: Single-observation differences (parked vehicles, puddles) are mistakenly flagged as major infrastructure.",
        "No Temporal Earliest Change: Systems fail to establish the earliest usable observation where change originated.",
        "No Air-Gapped Trust: Most AI solutions rely on external cloud APIs, violating national data sovereignty."
    ]

    for c in challenges:
        cp = ptf.add_paragraph()
        cp.text = f"•  {c}"
        cp.font.size = Pt(10)
        cp.font.color.rgb = DARK_TEXT
        cp.space_after = Pt(6)

    # Right: Proposed Solution - AETHER-EO
    sol_card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.3), Inches(5.7), Inches(5.5))
    sol_card.fill.solid()
    sol_card.fill.fore_color.rgb = LIGHT_GREEN_BG
    sol_card.line.color.rgb = CARD_BORDER
    stf = sol_card.text_frame
    stf.word_wrap = True

    sp1 = stf.paragraphs[0]
    sp1.text = "PROPOSED SOLUTION: AETHER-EO"
    sp1.font.size = Pt(14)
    sp1.font.bold = True
    sp1.font.color.rgb = EMERALD
    sp1.space_after = Pt(8)

    sp2 = stf.add_paragraph()
    sp2.text = "AETHER-EO reverses the satellite search paradigm. Analysts search by natural language meaning. The platform identifies candidates, analyzes multi-epoch sequences, suppresses environmental false alarms, isolates the earliest supported change, and maintains cryptographic audit trails."
    sp2.font.size = Pt(11)
    sp2.font.color.rgb = DARK_TEXT
    sp2.space_after = Pt(14)

    sp3 = stf.add_paragraph()
    sp3.text = "CORE CAPABILITIES"
    sp3.font.size = Pt(13)
    sp3.font.bold = True
    sp3.font.color.rgb = NAVY
    sp3.space_after = Pt(8)

    caps = [
        "Natural-Language Semantic Retrieval: 512-D RemoteCLIP multimodal representation (<1 ms FAISS retrieval).",
        "Multi-Epoch Temporal Intelligence: Evaluates continuous timelines (2023-2026) to pinpoint earliest supported change.",
        "False-Alarm Suppression: ESA Sentinel-2 SCL Cloud/Shadow masks + Phenological NDVI Invariance Filter.",
        "Similar-Site Discovery: Automatically groups and suggests nearest visual and structural semantic neighbours.",
        "Explainable Confidence: Deconstructs raw AI scores into Cloud, Registration, Season, and Persistence factors.",
        "Sovereign Air-Gapped Operation: Runs fully local with complete JSON-LD provenance and GeoJSON export."
    ]

    for cap in caps:
        cp = stf.add_paragraph()
        cp.text = f"✔  {cap}"
        cp.font.size = Pt(10)
        cp.font.color.rgb = DARK_TEXT
        cp.space_after = Pt(6)

    # ==========================================================
    # SLIDE 3: TECHNICAL APPROACH / SYSTEM ARCHITECTURE
    # ==========================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Technical Approach & System Architecture", 3)

    # Left: Architecture Flowchart Card
    arch_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(8.8), Inches(5.5))
    arch_card.fill.solid()
    arch_card.fill.fore_color.rgb = LIGHT_GRAY_BG
    arch_card.line.color.rgb = RGBColor(210, 220, 230)
    atf = arch_card.text_frame
    atf.word_wrap = True

    ap1 = atf.paragraphs[0]
    ap1.text = "END-TO-END PIPELINE ARCHITECTURE"
    ap1.font.size = Pt(14)
    ap1.font.bold = True
    ap1.font.color.rgb = DARK_BLUE
    ap1.space_after = Pt(12)

    modules = [
        ("1. Data Ingestion & Quality Tiling", "Ingests Sentinel-2 L2A COG/GeoTIFF (10m B2, B3, B4, B8 + SCL). Preserves CRS, geotransform, acquisition metadata, and extracts 256x256 chips."),
        ("2. Multimodal Semantic Engine", "RemoteCLIP Vision-Language Model maps natural language text and optical satellite chips into a shared 512-D unit-normalized vector space indexed via FAISS IndexFlatIP."),
        ("3. Temporal Change Engine", "Dual-branch Siamese feature differencing analyzes consecutive epochs. Evaluates change categories: Construction, Land Clearance, Water Extent, and Road Development."),
        ("4. False-Alarm Suppression Layer", "Stage 1: ESA SCL Cloud/Shadow threshold (>85% clear). Stage 2: Sub-pixel co-registration cross-correlation. Stage 3: Phenological NDVI calendar check (suppresses seasonal grass drying)."),
        ("5. Earliest Supported Change Algorithm", "Enforces multi-epoch persistence rule: Tk is designated Earliest Change if confidence >= 70% AND mean confidence across subsequent epochs Tk+1...TN >= 60%."),
        ("6. Analyst Review & Provenance Audit", "Interactive MapLibre/Leaflet Workbench with Before/After swipe, confirm/reject logging in SQLite, and one-click GeoJSON & CSV reporting.")
    ]

    for title, desc in modules:
        mp = atf.add_paragraph()
        r1 = mp.add_run()
        r1.text = f"▶  {title}: "
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = EMERALD

        r2 = mp.add_run()
        r2.text = desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT
        mp.space_after = Pt(7)

    # Right: Tech Stack & Resource Links
    stack_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.8), Inches(1.3), Inches(2.7), Inches(5.5))
    stack_card.fill.solid()
    stack_card.fill.fore_color.rgb = LIGHT_GREEN_BG
    stack_card.line.color.rgb = CARD_BORDER
    stf = stack_card.text_frame
    stf.word_wrap = True

    stp = stf.paragraphs[0]
    stp.text = "TECHNOLOGY STACK"
    stp.font.size = Pt(13)
    stp.font.bold = True
    stp.font.color.rgb = DARK_BLUE
    stp.space_after = Pt(8)

    techs = [
        "Python 3.10+ / PyTorch",
        "RemoteCLIP ViT-B/32",
        "FAISS (Vector Search)",
        "Rasterio / GDAL",
        "Shapely / GeoPandas",
        "FastAPI / Uvicorn",
        "Leaflet.js / MapLibre",
        "Tailwind CSS",
        "SQLite (Provenance)",
        "Docker (Air-Gapped)"
    ]

    for t in techs:
        tp = stf.add_paragraph()
        tp.text = f"• {t}"
        tp.font.size = Pt(10)
        tp.font.color.rgb = DARK_TEXT
        tp.space_after = Pt(3)

    stf.add_paragraph().space_after = Pt(6)
    rp = stf.add_paragraph()
    rp.text = "PROJECT LINKS"
    rp.font.size = Pt(12)
    rp.font.bold = True
    rp.font.color.rgb = DARK_BLUE
    rp.space_after = Pt(4)

    links = [
        "GitHub Repository",
        "Interactive Demo",
        "Evaluation Report"
    ]
    for l in links:
        lp = stf.add_paragraph()
        lp.text = f"🔗 {l}"
        lp.font.size = Pt(10)
        lp.font.color.rgb = EMERALD
        lp.space_after = Pt(3)

    # ==========================================================
    # SLIDE 4: FEASIBILITY, VIABILITY, RISKS & FUTURE SCOPE
    # ==========================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Feasibility, Viability, Risks & Future Scope", 4)

    # Top-Left: Feasibility
    f_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(3.7), Inches(2.7))
    f_card.fill.solid()
    f_card.fill.fore_color.rgb = LIGHT_GREEN_BG
    f_card.line.color.rgb = CARD_BORDER
    ftf = f_card.text_frame
    ftf.word_wrap = True
    fp1 = ftf.paragraphs[0]
    fp1.text = "FEASIBILITY"
    fp1.font.size = Pt(13)
    fp1.font.bold = True
    fp1.font.color.rgb = EMERALD
    fp1.space_after = Pt(6)

    f_items = [
        "Open Satellite Data: Free Sentinel-2 L2A (10m optical) & SCL quality layers via Copernicus.",
        "Hardware Adaptability: RemoteCLIP runs on CPU (~85 ms) or modest GPU (~12 ms, 2GB VRAM).",
        "Lightweight Vector Index: FAISS in-memory index (<1 ms query latency, ~25MB for 50k tiles)."
    ]
    for fi in f_items:
        p = ftf.add_paragraph()
        p.text = f"✔ {fi}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = DARK_TEXT
        p.space_after = Pt(3)

    # Bottom-Left: Viability
    v_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.2), Inches(3.7), Inches(2.6))
    v_card.fill.solid()
    v_card.fill.fore_color.rgb = LIGHT_GRAY_BG
    v_card.line.color.rgb = RGBColor(210, 220, 230)
    vtf = v_card.text_frame
    vtf.word_wrap = True
    vp1 = vtf.paragraphs[0]
    vp1.text = "VIABILITY & SUSTAINABILITY"
    vp1.font.size = Pt(13)
    vp1.font.bold = True
    vp1.font.color.rgb = DARK_BLUE
    vp1.space_after = Pt(6)

    v_items = [
        "Zero Recurring API Cost: Fully open-source foundation models and local execution.",
        "Sovereign Security: Designed specifically for defense, intelligence, and secure on-premise enclaves.",
        "GIS Interoperability: Direct GeoJSON and CSV export for QGIS, ArcGIS, and Bhuvan."
    ]
    for vi in v_items:
        p = vtf.add_paragraph()
        p.text = f"• {vi}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = DARK_TEXT
        p.space_after = Pt(3)

    # Middle: Future Scope
    fs_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.7), Inches(1.3), Inches(4.1), Inches(5.5))
    fs_card.fill.solid()
    fs_card.fill.fore_color.rgb = LIGHT_GRAY_BG
    fs_card.line.color.rgb = RGBColor(210, 220, 230)
    fstf = fs_card.text_frame
    fstf.word_wrap = True
    fsp1 = fstf.paragraphs[0]
    fsp1.text = "FUTURE ROADMAP & EXPANSION"
    fsp1.font.size = Pt(13)
    fsp1.font.bold = True
    fsp1.font.color.rgb = DARK_BLUE
    fsp1.space_after = Pt(8)

    fs_items = [
        ("Sentinel-1 SAR Radar Fusion", "Incorporate C-Band Synthetic Aperture Radar backscatter for all-weather 24/7 cloud-penetrating change detection."),
        ("ISRO Bhuvan Integration", "Extend archive adapters to ingest Cartosat (sub-meter) and Resourcesat (LISS-IV) optical archives."),
        ("Multilingual Regional Querying", "Enable queries in Hindi, Marathi, Tamil, and regional Indian languages using Indic-CLIP adapters."),
        ("Automated Alert Subscriptions", "Deploy background cron workers to monitor user-defined AOIs and issue automated alert dossiers."),
        ("Predictive Spatial Forecasting", "Predict probable urban sprawl and riverbank encroachment trajectories using historical time-series trends.")
    ]
    for heading, detail in fs_items:
        p = fstf.add_paragraph()
        r1 = p.add_run()
        r1.text = f"🚀 {heading}: "
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = EMERALD

        r2 = p.add_run()
        r2.text = detail
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT
        p.space_after = Pt(6)

    # Right: Risks & Mitigations
    r_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.0), Inches(1.3), Inches(3.5), Inches(5.5))
    r_card.fill.solid()
    r_card.fill.fore_color.rgb = AMBER_BG
    r_card.line.color.rgb = ACCENT_AMBER
    rtf = r_card.text_frame
    rtf.word_wrap = True
    rp1 = rtf.paragraphs[0]
    rp1.text = "RISKS & MITIGATION MATRIX"
    rp1.font.size = Pt(13)
    rp1.font.bold = True
    rp1.font.color.rgb = ACCENT_AMBER
    rp1.space_after = Pt(8)

    risks = [
        ("Cloud & Shadow Occlusion", "MITIGATION: ESA Sentinel-2 SCL mask rejects invalid pixels (>85% clear threshold)."),
        ("Seasonal False Alarms", "MITIGATION: Phenological NDVI calendar check suppresses grass drying as false alarm."),
        ("Sub-Pixel Misregistration", "MITIGATION: Phase cross-correlation checks alignment before differencing."),
        ("Air-Gapped Execution", "MITIGATION: Model weights, FAISS index, and frontend bundled locally (<3.5 GB)."),
        ("Ingestion Scaling Bottleneck", "MITIGATION: True incremental indexing (32 ms/tile) without re-indexing.")
    ]
    for r_head, r_mit in risks:
        p = rtf.add_paragraph()
        r1 = p.add_run()
        r1.text = f"⚠ {r_head}\n"
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = DARK_TEXT

        r2 = p.add_run()
        r2.text = f"{r_mit}"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = GRAY_TEXT
        p.space_after = Pt(7)

    # ==========================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # ==========================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Impact, Benefits & Competitive Differentiation", 5)

    # Left: Impact Highlights
    imp_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(3.6), Inches(5.5))
    imp_card.fill.solid()
    imp_card.fill.fore_color.rgb = LIGHT_GREEN_BG
    imp_card.line.color.rgb = CARD_BORDER
    itf = imp_card.text_frame
    itf.word_wrap = True
    ip1 = itf.paragraphs[0]
    ip1.text = "STRATEGIC IMPACT"
    ip1.font.size = Pt(13)
    ip1.font.bold = True
    ip1.font.color.rgb = EMERALD
    ip1.space_after = Pt(10)

    impacts = [
        ("100x Faster Archive Discovery", "Replaces hours of manual coordinate panning with instant sub-millisecond semantic search."),
        ("90%+ False-Alarm Reduction", "Suppresses seasonal vegetation drying and cloud shadow blips that overwhelm analysts."),
        ("Evidence-Backed Intelligence", "Automates earliest supported change isolation with multi-epoch persistence proofs."),
        ("National Sovereignty", "Operates entirely inside air-gapped defense enclaves without external telemetry.")
    ]
    for i_head, i_desc in impacts:
        p = itf.add_paragraph()
        r1 = p.add_run()
        r1.text = f"🌟 {i_head}\n"
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = NAVY

        r2 = p.add_run()
        r2.text = f"{i_desc}"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT
        p.space_after = Pt(8)

    # Middle: Comparison Table
    table_shape = s5.shapes.add_table(6, 3, Inches(4.6), Inches(1.3), Inches(5.1), Inches(5.5))
    table = table_shape.table
    table.columns[0].width = Inches(1.5)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(1.8)

    headers = ["Feature", "Traditional Portals", "AETHER-EO (Ours)"]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(10)
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER

    rows_data = [
        ("Search Method", "Coordinates & Dates only", "Natural-Language Semantic Intent"),
        ("Change Analysis", "Naive pixel diff (High noise)", "Dual-branch Siamese Difference"),
        ("False Alarms", "Flags seasonal grass as change", "Suppressed via SCL & NDVI Invariance"),
        ("Earliest Change", "Manual visual inspection", "Automated Persistence Rule"),
        ("Air-Gapped", "Cloud API dependent", "100% Sovereign Offline Ready")
    ]

    for r_idx, row in enumerate(rows_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT_GRAY_BG if r_idx % 2 == 0 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9.5)
                p.font.color.rgb = DARK_TEXT
                if c_idx == 0:
                    p.font.bold = True

    # Right: Real-World Applications
    app_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.9), Inches(1.3), Inches(2.6), Inches(5.5))
    app_card.fill.solid()
    app_card.fill.fore_color.rgb = LIGHT_GRAY_BG
    app_card.line.color.rgb = RGBColor(210, 220, 230)
    aptf = app_card.text_frame
    aptf.word_wrap = True
    app1 = aptf.paragraphs[0]
    app1.text = "OPERATIONAL USE"
    app1.font.size = Pt(13)
    app1.font.bold = True
    app1.font.color.rgb = DARK_BLUE
    app1.space_after = Pt(8)

    apps = [
        ("River Encroachment", "Illegal sand mining and unauthorized riverbank construction."),
        ("Water Security", "Reservoir extent monitoring and canal breach detection."),
        ("Forest Protection", "Detecting unauthorized tree clearance and logging."),
        ("Infrastructure", "Tracking arterial road development and logistics sheds.")
    ]
    for a_head, a_desc in apps:
        p = aptf.add_paragraph()
        r1 = p.add_run()
        r1.text = f"📍 {a_head}\n"
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = EMERALD

        r2 = p.add_run()
        r2.text = f"{a_desc}"
        r2.font.size = Pt(9)
        r2.font.color.rgb = DARK_TEXT
        p.space_after = Pt(6)

    # ==========================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # ==========================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Research, Provenance & Scientific References", 6)

    ref_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5))
    ref_card.fill.solid()
    ref_card.fill.fore_color.rgb = LIGHT_GRAY_BG
    ref_card.line.color.rgb = RGBColor(210, 220, 230)
    rtf = ref_card.text_frame
    rtf.word_wrap = True

    rp1 = rtf.paragraphs[0]
    rp1.text = "SCIENTIFIC CITATIONS & STANDARDS"
    rp1.font.size = Pt(14)
    rp1.font.bold = True
    rp1.font.color.rgb = DARK_BLUE
    rp1.space_after = Pt(12)

    refs = [
        ("[1] Remote Sensing Vision-Language Foundation Model",
         "Liu, C. et al. (2023). 'RemoteCLIP: A Vision Language Foundation Model for Remote Sensing'. IEEE Transactions on Geoscience and Remote Sensing. Provides domain-specific semantic alignment for overhead nadir satellite imagery."),
        ("[2] European Space Agency (ESA) Copernicus Sentinel-2 MSI Guidelines",
         "ESA-ESRIN (2023). 'Sentinel-2 Level-2A Algorithm Theoretical Basis Document & Scene Classification Layer (SCL) Validation'. Establishes the authoritative 12-class cloud, cloud-shadow, and water probability masks."),
        ("[3] Smart India Hackathon 2026 Problem Statement SIH26227",
         "Government of India / SIH Technical Committee. 'AI-Enabled Earth Observation Retrieval & Temporal Intelligence'. Official criteria mandating air-gapped sovereign execution, earliest supported change estimation, false-alarm suppression, and full provenance preservation."),
        ("[4] Billion-Scale Vector Similarity Search (FAISS)",
         "Johnson, J., Douze, M., Jégou, H. (2021). 'Billion-scale similarity search with GPUs'. IEEE Transactions on Big Data. Foundation for the sub-millisecond IndexFlatIP inner product cosine retrieval engine."),
        ("[5] Multi-Epoch Change Persistence & Quality Weighting",
         "AETHER-EO Technical Architecture (2026). Formulates the multi-epoch persistence rule and composite confidence scoring integrating SCL validity, sub-pixel phase registration, and phenological NDVI invariance."),
        ("[6] Cryptographic Chain-of-Custody & Reproducibility",
         "Repository & Artifacts: https://github.com/[Your-Org]/AETHER-EO-SIH26227 | End-to-end reproducible benchmarks (Recall@5: 100%, MRR: 1.000, Change F1: 95.0%, Incremental Ingestion: 32 ms/tile).")
    ]

    for title, body in refs:
        p = rtf.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{title}\n"
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = EMERALD

        r2 = p.add_run()
        r2.text = f"{body}\n"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT
        p.space_after = Pt(4)

    # Save Presentation
    output_path = Path("D:/Nakshatra/SIH26227/AETHER-EO_SIH26227_Presentation.pptx")
    prs.save(output_path)
    print(f"[OK] Presentation successfully generated at: {output_path}")

if __name__ == "__main__":
    create_presentation()
