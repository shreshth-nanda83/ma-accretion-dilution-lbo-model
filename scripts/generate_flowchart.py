"""
High-Resolution Flowchart Generator for Cross-Border M&A & LBO Model
====================================================================
Generates assets/flowchart.png illustrating the complete institutional pipeline:
  1. Kaggle Data Ingestion & SQL Target Screener
  2. Flagship ₹4,200 Cr Deal Calibration & Synergies
  3. Purchase Price Allocation (Goodwill & DTL)
  4. 5 Capital Structures & LBO Cash Sweep (3.08x Covenant & 18.7% IRR)
  5. Wall Street Excel Model & Streamlit Interactive Deal Room
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(WORKSPACE_DIR, "assets")
FLOWCHART_PNG_PATH = os.path.join(ASSETS_DIR, "flowchart.png")


def create_flowchart(output_path: str = FLOWCHART_PNG_PATH):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(18, 11), dpi=300)
    fig.patch.set_facecolor("#0A0E17")
    ax.set_facecolor("#0A0E17")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Header Title Banner
    title_box = patches.FancyBboxPatch(
        (4, 88), 92, 9,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#111C33",
        edgecolor="#38BDF8",
        linewidth=2,
    )
    ax.add_patch(title_box)

    ax.text(
        50, 93.8,
        "CROSS-BORDER M&A ACCRETION/DILUTION & LBO SYNERGY MODEL",
        fontsize=16, fontweight="bold", color="#F8FAFC",
        ha="center", va="center"
    )
    ax.text(
        50, 90.0,
        "End-to-End Institutional Architecture | Kaggle NYSE Fundamentals (dgawlik/nyse) → ₹4,200 Cr Deal Engine",
        fontsize=10.5, color="#94A3B8",
        ha="center", va="center"
    )

    # Stages Layout
    stages = [
        {
            "num": "01",
            "title": "KAGGLE DATA INGESTION",
            "sub": "Raw Financial Statements",
            "x": 4, "y": 50, "w": 20.5, "h": 32,
            "border": "#38BDF8",
            "items": [
                ("Dataset", "Kaggle dgawlik/nyse"),
                ("Coverage", "448 S&P 500 / NYSE Firms"),
                ("Attributes", "79 Financial Statement Cols"),
                ("Normalization", "Snake_case / Missing values"),
                ("Storage", "SQLite: kaggle_ma_universe.db"),
                ("Metrics", "EBITDA, Net Debt, OCF, FCF"),
            ]
        },
        {
            "num": "02",
            "title": "SQL TARGET SCREENER",
            "sub": "Multi-CTE Window Functions",
            "x": 28, "y": 50, "w": 20.5, "h": 32,
            "border": "#00E676",
            "items": [
                ("Query Script", "sql/target_screener.sql"),
                ("Window Func", "ROW_NUMBER() per Ticker"),
                ("EBITDA Margin", "> 15.0% (Core Profitability)"),
                ("SG&A Ratio", "> 15.0% (Cost Synergy Runway)"),
                ("FCF Conversion", "> 40.0% (Debt Service)"),
                ("Net Debt/EBITDA", "< 2.50x (Prudent Leverage)"),
                ("Output", "Top 25 Institutional Targets"),
            ]
        },
        {
            "num": "03",
            "title": "₹4,200 CR M&A ENGINE",
            "sub": "PPA & 5-Yr Pro-Forma IS",
            "x": 51.5, "y": 50, "w": 20.5, "h": 32,
            "border": "#F59E0B",
            "items": [
                ("Enterprise Value", "₹4,200 Cr (12.0x EBITDA)"),
                ("Target EBITDA", "₹350 Cr LTM (₹1,750 Cr Rev)"),
                ("5-Yr Synergies", "₹380 Cr (40, 75, 85, 90, 90)"),
                ("Sources & Uses", "Balanced at ₹4,200 Cr"),
                ("Goodwill / DTL", "₹2,351 Cr / ₹151 Cr (25.17%)"),
                ("Y2 Pro-Forma EPS", "₹45.00 → ₹47.88 (+6.4%)"),
            ]
        },
        {
            "num": "04",
            "title": "CAPITAL STRUCTURE & LBO",
            "sub": "5 Structures & Cash Sweep",
            "x": 75.5, "y": 50, "w": 20.5, "h": 32,
            "border": "#A855F7",
            "items": [
                ("5 Structures", "Stock, 70/30, 50/50, Hybrid, LBO"),
                ("Optimal Structure", "Structure #4: Optimal Hybrid"),
                ("Debt Breakdown", "Senior ₹850 Cr, Mezz ₹350 Cr"),
                ("Net Debt / EBITDA", "3.08x (< 3.20x Covenant)"),
                ("5-Yr Project IRR", "14.2% Base → 18.7% Hybrid"),
                ("75% Cash Sweep", "Senior Debt: ₹850 Cr → <₹20 Cr"),
            ]
        },
    ]

    for stg in stages:
        box = patches.FancyBboxPatch(
            (stg["x"], stg["y"]), stg["w"], stg["h"],
            boxstyle="round,pad=0.7,rounding_size=1.2",
            facecolor="#111A2E",
            edgecolor=stg["border"],
            linewidth=2,
        )
        ax.add_patch(box)

        # Stage Number Badge
        badge = patches.FancyBboxPatch(
            (stg["x"] + 1, stg["y"] + stg["h"] - 4.5), 3.5, 3.2,
            boxstyle="round,pad=0.3,rounding_size=0.6",
            facecolor=stg["border"],
            edgecolor=stg["border"],
        )
        ax.add_patch(badge)
        ax.text(
            stg["x"] + 2.75, stg["y"] + stg["h"] - 2.9,
            stg["num"],
            fontsize=10, fontweight="bold", color="#0A0E17",
            ha="center", va="center"
        )

        ax.text(
            stg["x"] + 5.5, stg["y"] + stg["h"] - 2.3,
            stg["title"],
            fontsize=10.5, fontweight="bold", color="#F8FAFC",
            ha="left", va="center"
        )
        ax.text(
            stg["x"] + 5.5, stg["y"] + stg["h"] - 4.2,
            stg["sub"],
            fontsize=8.5, color="#94A3B8",
            ha="left", va="center"
        )

        # Divider line
        ax.plot(
            [stg["x"] + 1, stg["x"] + stg["w"] - 1],
            [stg["y"] + stg["h"] - 5.8, stg["y"] + stg["h"] - 5.8],
            color="white", alpha=0.15, linewidth=0.8
        )

        # Content items
        curr_y = stg["y"] + stg["h"] - 8.5
        for lbl, val in stg["items"]:
            ax.text(
                stg["x"] + 1.2, curr_y,
                f"• {lbl}:",
                fontsize=8.2, fontweight="bold", color="#38BDF8" if "Optimal" in val or "+6.4%" in val or "3.08x" in val else "#CBD5E1",
                ha="left", va="center"
            )
            ax.text(
                stg["x"] + 1.2, curr_y - 1.8,
                f"   {val}",
                fontsize=8.0, color="#00E676" if "+6.4%" in val or "18.7%" in val or "3.08x" in val else "#94A3B8",
                ha="left", va="center"
            )
            curr_y -= 3.7

    # Connectors between stages 1 -> 2 -> 3 -> 4
    for arrow_x in [25.5, 49.0, 73.0]:
        ax.annotate(
            "",
            xy=(arrow_x + 2.3, 66),
            xytext=(arrow_x - 0.8, 66),
            arrowprops=dict(
                arrowstyle="fancy,head_width=2.5,head_length=3.5",
                facecolor="#38BDF8",
                edgecolor="#38BDF8",
                linewidth=0.8
            )
        )

    # Deliverables Stage 05 (Bottom Row)
    deliv_box = patches.FancyBboxPatch(
        (4, 7), 92, 36,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#111C33",
        edgecolor="#EC4899",
        linewidth=2,
    )
    ax.add_patch(deliv_box)

    # Stage 05 Header
    deliv_badge = patches.FancyBboxPatch(
        (5.5, 38.5), 3.5, 3.2,
        boxstyle="round,pad=0.3,rounding_size=0.6",
        facecolor="#EC4899",
        edgecolor="#EC4899",
    )
    ax.add_patch(deliv_badge)
    ax.text(
        7.25, 40.1,
        "05",
        fontsize=10, fontweight="bold", color="#0A0E17",
        ha="center", va="center"
    )
    ax.text(
        10.2, 40.8,
        "INSTITUTIONAL DELIVERABLES & INTERFACES",
        fontsize=11.5, fontweight="bold", color="#F8FAFC",
        ha="left", va="center"
    )
    ax.text(
        10.2, 38.7,
        "Interactive Executive Presentation & Wall Street Financial Workbooks",
        fontsize=9, color="#94A3B8",
        ha="left", va="center"
    )

    # Downward connectors to deliverables
    ax.annotate(
        "",
        xy=(27, 44),
        xytext=(27, 49),
        arrowprops=dict(arrowstyle="fancy,head_width=2,head_length=3", facecolor="#EC4899", edgecolor="#EC4899")
    )
    ax.annotate(
        "",
        xy=(73, 44),
        xytext=(73, 49),
        arrowprops=dict(arrowstyle="fancy,head_width=2,head_length=3", facecolor="#EC4899", edgecolor="#EC4899")
    )

    # Left Deliverable Card: Excel Model
    ex_card = patches.FancyBboxPatch(
        (7, 10.5), 41.5, 25.5,
        boxstyle="round,pad=0.6,rounding_size=1.0",
        facecolor="#152238",
        edgecolor="#217346",
        linewidth=1.8,
    )
    ax.add_patch(ex_card)

    ax.text(9.5, 33.2, "[EXCEL] Wall Street Workbook Generator (models/*.xlsx)", fontsize=10.5, fontweight="bold", color="#34D399")
    ax.text(9.5, 31.2, "Built via openpyxl with 6 Investment Banking Tabs:", fontsize=8.5, color="#94A3B8")

    excel_tabs = [
        "1. Kaggle_M&A_Target_Screener (Top 25 Screened Candidates)",
        "2. Sources_Uses_&_Goodwill_PPA (PPA, DTL ₹151 Cr, Goodwill ₹2,351 Cr)",
        "3. 5Yr_ProForma_IS_&_Synergies (₹380 Cr Phased Synergies Realization)",
        "4. EPS_Accretion_Dilution_Bridge (₹45.00 → ₹47.88, +6.4% Accretion)",
        "5. 5_Debt_Structures_&_Cash_Sweep (Covenant Check 3.08x < 3.2x)",
        "6. Sensitivity_Matrices (2D Data Tables: Multiple vs Synergies & LBO IRR)",
    ]
    curr_tab_y = 28.5
    for t in excel_tabs:
        ax.text(9.8, curr_tab_y, f"• {t}", fontsize=8.2, color="#E2E8F0")
        curr_tab_y -= 2.7

    # Right Deliverable Card: Streamlit Deal Room
    st_card = patches.FancyBboxPatch(
        (51.5, 10.5), 41.5, 25.5,
        boxstyle="round,pad=0.6,rounding_size=1.0",
        facecolor="#152238",
        edgecolor="#FF4B4B",
        linewidth=1.8,
    )
    ax.add_patch(st_card)

    ax.text(54.0, 33.2, "[STREAMLIT] Interactive Deal Room (app.py)", fontsize=10.5, fontweight="bold", color="#F87171")
    ax.text(54.0, 31.2, "Real-Time Scenario Simulator & Visual Analytics:", fontsize=8.5, color="#94A3B8")

    st_features = [
        "Tab 1: Kaggle Target Screener & Acquirer-Target Universe Matcher",
        "Tab 2: Accretion/Dilution Engine with 5 Top KPI Metric Cards",
        "Interactive Plotly Waterfall Chart (Year 2 EPS Accretion Bridge)",
        "Tab 3: Capital Structure Simulator & Credit Covenant Test (3.08x)",
        "Interactive 5-Year Debt Paydown Deleveraging Chart (75% Sweep)",
        "Direct One-Click Wall Street Excel (.xlsx) Export & Scenario Sliders",
    ]
    curr_feat_y = 28.5
    for f in st_features:
        ax.text(54.3, curr_feat_y, f"• {f}", fontsize=8.2, color="#E2E8F0")
        curr_feat_y -= 2.7

    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close()
    print(f"[Flowchart] Successfully created high-resolution flowchart at: {output_path}")
    return output_path


if __name__ == "__main__":
    create_flowchart()
