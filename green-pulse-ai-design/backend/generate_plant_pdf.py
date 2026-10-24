"""
GreenPulse AI - Plant Knowledge Base PDF Generator
Generates a comprehensive, enterprise-grade PDF manual encompassing all plant
specifications, dashboard KPIs, machine fleet digital twins, forecasting algorithms,
anomalies, ECM recommendations, carbon accounting, and regulatory compliance.
Saves to backend/knowledge_documents/uploaded_pdfs and public/ for download.
"""
import os
import sys
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds professional running header and footer with total page count."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0F172A"))

        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 792 - 36, "GREENPULSE AI — INDUSTRIAL INTELLIGENCE PLATFORM")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(612 - 54, 792 - 36, "PLANT #4 COMPREHENSIVE OPERATIONAL REFERENCE")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 792 - 42, 612 - 54, 792 - 42)

        # Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — GREENPULSE MANUFACTURING CORP.")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def create_plant_manual(output_paths):
    for out_path in output_paths:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

    primary_path = output_paths[0]
    doc = SimpleDocTemplate(
        primary_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom Typographic Hierarchy
    c_navy = colors.HexColor("#0F172A")
    c_emerald = colors.HexColor("#059669")
    c_slate = colors.HexColor("#334155")
    c_light_bg = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_navy,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=c_emerald,
        spaceAfter=18,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_navy,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_emerald,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_slate,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=3,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=c_slate,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=c_navy,
    )

    story = []

    # =========================================================================
    # DOCUMENT COVER HEADER
    # =========================================================================
    story.append(Paragraph("GREENPULSE MANUFACTURING PLANT #4", title_style))
    story.append(Paragraph("Comprehensive Plant Master Reference & Operational Manual", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_emerald, spaceAfter=14))

    meta_table_data = [
        [
            Paragraph("<b>Facility Code:</b> FAC-IND-PUN-004", body_style),
            Paragraph("<b>Contracted Demand:</b> 2,500.0 kW", body_style),
        ],
        [
            Paragraph("<b>Location:</b> Chakan MIDC Phase II, Pune", body_style),
            Paragraph("<b>Utility Account:</b> MSEDCL-HT-9482103", body_style),
        ],
        [
            Paragraph("<b>Operating Mode:</b> 3 Shifts / 24x7 Continuous", body_style),
            Paragraph("<b>Substation Feeder:</b> 33 kV Express Feeder #3", body_style),
        ],
        [
            Paragraph(f"<b>Effective Date:</b> October 2026", body_style),
            Paragraph("<b>Compliance:</b> ISO 50001 / BEE PAT VI / IEEE 519", body_style),
        ],
    ]
    t_meta = Table(meta_table_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 1: FACILITY OVERVIEW & INFRASTRUCTURE
    # =========================================================================
    story.append(Paragraph("1. Facility Profile & Electrical Infrastructure", h1_style))
    story.append(Paragraph(
        "GreenPulse Plant #4 is an advanced precision engineering and heavy component manufacturing facility. "
        "The plant operates on a 24x7 three-shift basis with a total connected load of approximately 3,450 kW and a "
        "utility-sanctioned Contract Demand of <b>2,500.0 kW</b> supplied via a dedicated 33 kV substation transformer.",
        body_style
    ))
    story.append(Paragraph("<b>Electrical Parameters & Power Ingress:</b>", h2_style))
    story.append(Paragraph("• <b>Primary Ingress:</b> 33 kV stepped down to 415V, 3-phase, 50 Hz via dual 2,000 kVA ONAN transformers.", bullet_style))
    story.append(Paragraph("• <b>Contract Demand (CD):</b> 2,500.0 kW (Billing demand is maximum of actual kVA or 85% of CD).", bullet_style))
    story.append(Paragraph("• <b>Tariff Structure:</b> MSEDCL HT-1 Industrial with Time-of-Day (ToD) tariff. Base tariff: ₹7.20/kWh.", bullet_style))
    story.append(Paragraph("• <b>Peak Hours (18:00–22:00 IST):</b> 1.44x multiplier (effective ₹10.37/kWh). Peak demand charges are strictly tracked.", bullet_style))
    story.append(Paragraph("• <b>Off-Peak Night Hours (22:00–06:00 IST):</b> 0.85x incentive multiplier (effective ₹6.12/kWh).", bullet_style))
    story.append(Paragraph("• <b>Power Factor Rebate / Penalty:</b> Target PF > 0.98. Rebate up to 7% for PF ≥ 0.995; penalty of 2% for every 0.01 drop below 0.90.", bullet_style))
    story.append(Paragraph("• <b>Backup Generation:</b> 2 x 1,250 kVA Caterpillar Diesel Generators with automatic transfer switch (ATS).", bullet_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: EXECUTIVE DASHBOARD KPIS & OPERATIONAL BENCHMARKS
    # =========================================================================
    story.append(Paragraph("2. Executive Dashboard KPIs & Live Telemetry Metrics", h1_style))
    story.append(Paragraph(
        "The GreenPulse AI executive dashboard synthesizes real-time Modbus SCADA telemetry every 15 seconds. "
        "The baseline operational benchmarks monitored on the dashboard are structured as follows:",
        body_style
    ))

    kpi_table_data = [
        [Paragraph("Dashboard Metric", table_header_style), Paragraph("Nominal Value / Range", table_header_style), Paragraph("Threshold / Alert Rule", table_header_style), Paragraph("Operational Impact", table_header_style)],
        [Paragraph("Active Facility Demand", table_cell_bold), Paragraph("1,420 – 1,650 kW", table_cell_style), Paragraph("Warning > 2,200 kW<br/>Critical > 2,375 kW", table_cell_style), Paragraph("Prevents DISCOM 150% penalty on demand exceedance", table_cell_style)],
        [Paragraph("Daily Energy Draw", table_cell_bold), Paragraph("18,500 – 22,000 kWh", table_cell_style), Paragraph("Baseline variance > ±10%", table_cell_style), Paragraph("Tracks production specific energy consumption", table_cell_style)],
        [Paragraph("System Power Factor", table_cell_bold), Paragraph("0.96 – 0.99 lagging", table_cell_style), Paragraph("Alert if PF &lt; 0.95<br/>Critical if PF &lt; 0.90", table_cell_style), Paragraph("Secures utility rebate; prevents reactive surcharge", table_cell_style)],
        [Paragraph("Voltage THD (IEEE 519)", table_cell_bold), Paragraph("2.1% – 3.8%", table_cell_style), Paragraph("Limit ≤ 5.0% THD_V", table_cell_style), Paragraph("Protects electronic drives, motors, and transformer life", table_cell_style)],
        [Paragraph("Current TDD (IEEE 519)", table_cell_bold), Paragraph("4.5% – 6.2%", table_cell_style), Paragraph("Limit ≤ 8.0% TDD", table_cell_style), Paragraph("Minimizes neutral conductor heating and line loss", table_cell_style)],
        [Paragraph("Fleet Health Index", table_cell_bold), Paragraph("88.4% Average", table_cell_style), Paragraph("Critical if asset &lt; 75%", table_cell_style), Paragraph("Identifies bearing and thermal degradation early", table_cell_style)],
        [Paragraph("Carbon Intensity", table_cell_bold), Paragraph("0.82 kg CO₂e / kWh", table_cell_style), Paragraph("National CEA Benchmark", table_cell_style), Paragraph("Mandatory BRSR & ESG Scope 2 disclosure", table_cell_style)],
    ]
    t_kpi = Table(kpi_table_data, colWidths=[110, 110, 124, 160])
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_navy),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 3: COMPLETE MACHINE FLEET REGISTRY & DIGITAL TWIN
    # =========================================================================
    story.append(Paragraph("3. Machine Fleet Registry & Digital Twin Specifications", h1_style))
    story.append(Paragraph(
        "The digital twin tracks 9 primary industrial assets across 6 physical factory zones. "
        "Each machine is monitored via IoT edge gateways measuring power (kW), voltage, current, vibration (mm/s RMS), "
        "and bearing temperature (°C).",
        body_style
    ))

    fleet_table_data = [
        [
            Paragraph("Asset Code", table_header_style),
            Paragraph("Machine Description & Model", table_header_style),
            Paragraph("Zone / Bay", table_header_style),
            Paragraph("Rated / Peak kW", table_header_style),
            Paragraph("Health / Status", table_header_style),
        ],
        [
            Paragraph("CNC-01", table_cell_bold),
            Paragraph("5-Axis Milling Center<br/><i>DMG Mori DMU 65 monoBLOCK</i>", table_cell_style),
            Paragraph("Precision Bay 1", table_cell_style),
            Paragraph("22.0 kW / 35 kW", table_cell_style),
            Paragraph("96% / Running", table_cell_style),
        ],
        [
            Paragraph("CNC-02", table_cell_bold),
            Paragraph("Heavy-Duty 4-Axis Lathe<br/><i>Doosan Puma 2600SY II</i>", table_cell_style),
            Paragraph("Precision Bay 2", table_cell_style),
            Paragraph("18.0 kW / 26 kW", table_cell_style),
            Paragraph("94% / Running", table_cell_style),
        ],
        [
            Paragraph("COMP-01", table_cell_bold),
            Paragraph("Screw Air Compressor #1 (Lead)<br/><i>Atlas Copco GA 75 VSD+</i>", table_cell_style),
            Paragraph("Utilities Block A", table_cell_style),
            Paragraph("58.0 kW / 412 kW*", table_cell_style),
            Paragraph("71% / Warning", table_cell_style),
        ],
        [
            Paragraph("COMP-02", table_cell_bold),
            Paragraph("Variable Speed Compressor #2<br/><i>Ingersoll Rand R55i VSD</i>", table_cell_style),
            Paragraph("Utilities Block A", table_cell_style),
            Paragraph("58.0 kW / 75 kW", table_cell_style),
            Paragraph("92% / Running", table_cell_style),
        ],
        [
            Paragraph("FURN-01", table_cell_bold),
            Paragraph("Continuous Annealing Furnace<br/><i>Seco/Warwick Vector 2.0</i>", table_cell_style),
            Paragraph("Thermal Bay", table_cell_style),
            Paragraph("95.0 kW / 650 kW*", table_cell_style),
            Paragraph("84% / Running", table_cell_style),
        ],
        [
            Paragraph("HVAC-01", table_cell_bold),
            Paragraph("Central Chiller & Air Handler<br/><i>Daikin Pathfinder AWV 15</i>", table_cell_style),
            Paragraph("Chiller Plant", table_cell_style),
            Paragraph("15.0 kW / 180 kW*", table_cell_style),
            Paragraph("88% / Running", table_cell_style),
        ],
        [
            Paragraph("PAINT-01", table_cell_bold),
            Paragraph("Automated Spray Booth & Plenum<br/><i>Eisenmann E-Shuttle 200</i>", table_cell_style),
            Paragraph("Finishing Bay B", table_cell_style),
            Paragraph("32.0 kW / 45 kW", table_cell_style),
            Paragraph("90% / Idle", table_cell_style),
        ],
        [
            Paragraph("PUMP-01", table_cell_bold),
            Paragraph("Coolant Recirculation Pump<br/><i>Grundfos CR 64-3 Industrial</i>", table_cell_style),
            Paragraph("Utilities Block B", table_cell_style),
            Paragraph("12.0 kW / 18 kW", table_cell_style),
            Paragraph("95% / Running", table_cell_style),
        ],
        [
            Paragraph("ASSY-01", table_cell_bold),
            Paragraph("Robotic Assembly Cell<br/><i>ABB IRB 6700 Cell</i>", table_cell_style),
            Paragraph("Assembly Hall", table_cell_style),
            Paragraph("90.0 kW / 115 kW", table_cell_style),
            Paragraph("98% / Running", table_cell_style),
        ],
    ]
    t_fleet = Table(fleet_table_data, colWidths=[65, 175, 100, 84, 80])
    t_fleet.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_navy),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_fleet)
    story.append(Paragraph("<font size='7'>* Note: Peak instantaneous loads include inductive startup cycles and thermal heating bank elements during full multi-stage operation.</font>", body_style))
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 4: PREDICTIVE AI & MACHINE LEARNING ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("4. Industrial AI & Machine Learning Architecture", h1_style))
    story.append(Paragraph(
        "GreenPulse AI employs an integrated suite of scikit-learn and XGBoost models running via the in-memory "
        "<b>ModelRegistry</b> singleton. Models operate with zero per-request disk reloading to ensure sub-100ms inference times.",
        body_style
    ))
    story.append(Paragraph("<b>4.1. 24-Hour Multi-Horizon Energy Load Forecasting (XGBoost):</b>", h2_style))
    story.append(Paragraph(
        "• <b>Algorithm:</b> Multi-stage gradient-boosted decision trees (XGBoost Regressor) trained on multi-season historical plant SCADA data.<br/>"
        "• <b>Features:</b> Rolling lag power, outdoor ambient temperature, shift schedule phase, production tonnage forecast, and calendar seasonality.<br/>"
        "• <b>Explainability:</b> TreeExplainer SHAP (SHapley Additive exPlanations) generates real-time feature attribution bar graphs.<br/>"
        "• <b>Accuracy & Metrics:</b> Mean Absolute Percentage Error (MAPE) = 3.82%, Root Mean Squared Error (RMSE) = 48.6 kW, Confidence = 94.2%.",
        body_style
    ))
    story.append(Paragraph("<b>4.2. Unsupervised Anomaly Detection (Isolation Forest):</b>", h2_style))
    story.append(Paragraph(
        "• <b>Algorithm:</b> High-dimensional Isolation Forest with an empirical contamination factor of 0.03.<br/>"
        "• <b>Telemetry Inputs:</b> Active power (kW), reactive power (kVAR), 3-phase current imbalance, bearing temperature (°C), and vibration RMS (mm/s).<br/>"
        "• <b>Incident Attribution:</b> Root causes automatically mapped to ISO 10816 vibration zones, motor phase unbalance, or thermal insulation breakdown.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 5: PRESCRIPTIVE RECOMMENDATIONS & ECM ROI MATRIX
    # =========================================================================
    story.append(Paragraph("5. Prescriptive Energy Conservation Measures (ECMs)", h1_style))
    story.append(Paragraph(
        "The Prescriptive Recommendation Engine ranks facility energy projects using Multi-Criteria Decision Analysis (MCDA). "
        "The current prioritized portfolio of active Energy Conservation Measures includes:",
        body_style
    ))

    ecm_table_data = [
        [
            Paragraph("ECM Title", table_header_style),
            Paragraph("Target Asset", table_header_style),
            Paragraph("Annual Savings", table_header_style),
            Paragraph("Cost / Payback", table_header_style),
            Paragraph("Carbon Offset", table_header_style),
        ],
        [
            Paragraph("VFD Retrofit & Pressure Setpoint Optimization (7.5 to 6.8 bar)", table_cell_bold),
            Paragraph("COMP-01<br/>Utilities", table_cell_style),
            Paragraph("48,000 kWh/yr<br/><b>₹3,45,600/yr</b>", table_cell_style),
            Paragraph("₹2,35,000<br/>8.2 months", table_cell_style),
            Paragraph("39.4 MT CO₂e/yr", table_cell_style),
        ],
        [
            Paragraph("Flue Gas Waste Heat Recovery (WHR) System Installation", table_cell_bold),
            Paragraph("FURN-01<br/>Thermal Bay", table_cell_style),
            Paragraph("72,000 kWh/yr<br/><b>₹5,18,400/yr</b>", table_cell_style),
            Paragraph("₹6,25,000<br/>14.5 months", table_cell_style),
            Paragraph("59.0 MT CO₂e/yr", table_cell_style),
        ],
        [
            Paragraph("Chilled Water Supply Temperature Reset (+1.5 °C Reset)", table_cell_bold),
            Paragraph("HVAC-01<br/>Chiller Plant", table_cell_style),
            Paragraph("18,500 kWh/yr<br/><b>₹1,33,200/yr</b>", table_cell_style),
            Paragraph("₹15,000<br/>1.4 months", table_cell_style),
            Paragraph("15.2 MT CO₂e/yr", table_cell_style),
        ],
        [
            Paragraph("Automated Capacitor Bank Stage Tuning (PF 0.96 to 0.995)", table_cell_bold),
            Paragraph("Main Substation<br/>Plant-Wide", table_cell_style),
            Paragraph("Rebate Capture<br/><b>₹1,80,000/yr</b>", table_cell_style),
            Paragraph("₹45,000<br/>3.0 months", table_cell_style),
            Paragraph("12.0 MT CO₂e/yr", table_cell_style),
        ],
        [
            Paragraph("Compressed Air Ultrasonic Acoustic Leakage Remediation (22 Leaks)", table_cell_bold),
            Paragraph("Utilities Ring<br/>Blocks A & B", table_cell_style),
            Paragraph("31,200 kWh/yr<br/><b>₹2,24,640/yr</b>", table_cell_style),
            Paragraph("₹38,000<br/>2.0 months", table_cell_style),
            Paragraph("25.6 MT CO₂e/yr", table_cell_style),
        ],
    ]
    t_ecm = Table(ecm_table_data, colWidths=[150, 85, 95, 84, 90])
    t_ecm.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_navy),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ecm)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: WHAT-IF SIMULATOR PARAMETRIC MODELING
    # =========================================================================
    story.append(Paragraph("6. What-If Parametric Simulation & Scenario Modeling", h1_style))
    story.append(Paragraph(
        "The What-If Simulator module empowers plant leadership to model counterfactual operational and economic scenarios "
        "before implementing physical setpoint modifications. The core parameters supported include:",
        body_style
    ))
    story.append(Paragraph("• <b>Production Throughput Scaling:</b> Simulates facility energy draw when production load varies from 50% to 150% of nominal 320 tons/day capacity.", bullet_style))
    story.append(Paragraph("• <b>Tariff Optimization & Peak Shift:</b> Calculates cost variance when thermal annealing or machining shifts are transferred from peak (18:00–22:00) to off-peak night windows.", bullet_style))
    story.append(Paragraph("• <b>Renewable Energy Integration:</b> Models the net import load curves and peak shaving impacts of an on-site 850 kWp solar PV array.", bullet_style))
    story.append(Paragraph("• <b>Equipment Duty Cycle Adjustments:</b> Simulates the effects of staggering lead/lag compressors (COMP-01 and COMP-02) to prevent simultaneous startup spikes.", bullet_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 7: CARBON ACCOUNTING, ESG & NET-ZERO ROADMAP
    # =========================================================================
    story.append(Paragraph("7. GHG Protocol Carbon Accounting & ESG Reporting", h1_style))
    story.append(Paragraph(
        "GreenPulse AI implements automated greenhouse gas emissions accounting aligned with the GHG Protocol Corporate Standard "
        "and India's SEBI Business Responsibility and Sustainability Reporting (BRSR) framework.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Scope 1 (Direct Emissions):</b> 12.4 Metric Tons (MT) CO₂e / month. Derived from natural gas consumption in the annealing furnace "
        "(FURN-01) and intermittent testing of diesel generators.<br/>"
        "• <b>Scope 2 (Indirect Emissions):</b> 48.6 Metric Tons (MT) CO₂e / month. Calculated using the Central Electricity Authority (CEA) "
        "grid emission factor of <b>0.82 kg CO₂e / kWh</b> applied to utility electricity consumption.<br/>"
        "• <b>Total Plant Carbon Footprint:</b> ~61.0 MT CO₂e / month (Annualized ~732 MT CO₂e).<br/>"
        "• <b>Specific Energy Consumption (SEC):</b> 68.5 kWh / Metric Ton of finished industrial output.<br/>"
        "• <b>Net-Zero 2030 Roadmap:</b> Target of 42% carbon intensity reduction by 2030 through rooftop solar PV expansion (850 kWp), "
        "compressed air electrification, and waste heat recovery.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 8: STANDARD OPERATING PROCEDURES & COMPLIANCE
    # =========================================================================
    story.append(Paragraph("8. Standard Operating Procedures (SOPs) & Regulatory Compliance", h1_style))
    story.append(Paragraph(
        "Operational procedures are indexed in the RAG vector store for instant retrieval by the AI Copilot. "
        "Key protocols and standards governing Plant #4 include:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>GP-SOP-ENG-04 (Peak Demand Curtailment):</b><br/>"
        "  - <i>Stage 1 (90% / 2,250 kW):</i> Automated warning notification to Shift Supervisor. Halt auxiliary testing.<br/>"
        "  - <i>Stage 2 (95% / 2,375 kW):</i> Throttle secondary trim air compressor (COMP-02) and shed comfort air conditioning.<br/>"
        "  - <i>Stage 3 (98% / 2,450 kW):</i> Interlock heating elements on furnace FURN-01 to eliminate immediate penalty risk.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>GP-SOP-ENG-07 (Power Factor & Harmonics):</b><br/>"
        "  - Daily inspection of APFC microprocessor relay display.<br/>"
        "  - Verification that THD_V remains &lt; 5.0% and capacitor bank contactor operating temperatures remain &lt; 55 °C.<br/>"
        "  - Immediate replacement of detuned reactor steps if current harmonics exceed 8% TDD.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>ISO 10816-3 (Vibration Severity Guidelines):</b><br/>"
        "  - Zone A (&lt; 1.4 mm/s RMS): Newly commissioned state.<br/>"
        "  - Zone B (1.4 – 2.8 mm/s RMS): Nominal unrestricted long-term operation.<br/>"
        "  - Zone C (2.8 – 4.5 mm/s RMS): Unsatisfactory operation; plan bearing grease / realignment.<br/>"
        "  - Zone D (&gt; 4.5 mm/s RMS): Critical vibration; initiate controlled machinery shutdown.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>ISO 50001:2018 (Energy Management Systems):</b><br/>"
        "  - Energy baseline (EnB) regression models updated quarterly against production tonnage.<br/>"
        "  - Significant Energy Uses (SEUs): Compressed air supply (28.4%), Furnace thermal heat (38.2%), Precision machining (18.6%).",
        bullet_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 9: SCADA ARCHITECTURE & RBAC SECURITY
    # =========================================================================
    story.append(Paragraph("9. SCADA Telemetry Architecture & Enterprise RBAC Governance", h1_style))
    story.append(Paragraph(
        "• <b>SCADA Gateway:</b> Moxa industrial edge controller streaming Modbus TCP (Port 502) and OPC UA (Port 4840) telemetry.<br/>"
        "• <b>Sync Cycle:</b> 15-second polling interval with zero-data-loss local circular buffer caching.<br/>"
        "• <b>Role-Based Access Control (RBAC):</b><br/>"
        "  - <i>Plant Head:</i> Full executive oversight, setpoint authorizations, financial and compliance sign-offs.<br/>"
        "  - <i>Energy Manager:</i> Complete energy explorer access, tariff modeling, ECM approvals, and carbon disclosures.<br/>"
        "  - <i>Maintenance Manager:</i> Equipment diagnostics, vibration spectrum analysis, work orders, and health indices.<br/>"
        "  - <i>Operator:</i> Restricted bay-level telemetry (assigned machines only); plant-wide financial metrics masked.",
        body_style
    ))
    story.append(Spacer(1, 14))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated master PDF at: {primary_path}")

    # Copy to secondary paths
    for extra_path in output_paths[1:]:
        with open(primary_path, "rb") as f_src:
            content = f_src.read()
        with open(extra_path, "wb") as f_dst:
            f_dst.write(content)
        print(f"Copied master PDF to: {extra_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_pdf_1 = os.path.join(base_dir, "knowledge_documents", "uploaded_pdfs", "GreenPulse_Plant_4_Master_Operational_Manual.pdf")
    target_pdf_2 = os.path.join(os.path.dirname(base_dir), "public", "GreenPulse_Plant_4_Master_Operational_Manual.pdf")
    
    create_plant_manual([target_pdf_1, target_pdf_2])
