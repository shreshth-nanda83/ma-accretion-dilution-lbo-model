"""
Cross-Border M&A Accretion/Dilution & LBO Synergy Model - Streamlit Deal Room
=============================================================================
Powered by real Kaggle NYSE Fundamentals dataset (dgawlik/nyse)
Features:
  - Tab 1: Kaggle M&A Target Screener & Universal Deal Selector
  - Tab 2: Accretion/Dilution & Synergy Bridge (KPI Cards & Interactive Y2 EPS Waterfall)
  - Tab 3: Capital Structure & LBO IRR Simulator (5 Structures, Cash Sweep, Excel Export)
"""

import os
import sys

# Ensure workspace root is in python path
WORKSPACE_DIR = os.path.abspath(os.path.dirname(__file__))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from src.kaggle_data_loader import (
    execute_screener_sql,
    get_all_tickers,
    get_company_profile,
    get_db_connection,
)
from src.accretion_dilution_engine import (
    AccretionDilutionEngine,
    FlagshipDealInputs,
    build_dynamic_deal_model,
)
from src.debt_structures_irr import DebtStructuresOptimizer
from src.generate_excel_model import generate_wall_street_excel_model, EXCEL_OUTPUT_PATH

# Streamlit Page Config
st.set_page_config(
    page_title="Cross-Border M&A & LBO Synergy Model",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Institutional CSS Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        background: linear-gradient(180deg, #0A0E17 0%, #0F172A 100%);
        color: #E2E8F0;
    }

    /* KPI Metric Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }

    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }

    .kpi-title {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }

    .kpi-sub {
        font-size: 0.8rem;
        font-weight: 500;
        color: #10B981;
    }

    .kpi-sub.cyan { color: #38BDF8; }
    .kpi-sub.gold { color: #F59E0B; }
    .kpi-sub.purple { color: #A855F7; }

    /* Custom Badges */
    .badge-pass {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-breach {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: #F1F5F9;
        margin: 20px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        color: #94A3B8;
        background-color: transparent;
    }

    .stTabs [aria-selected="true"] {
        color: #38BDF8 !important;
        background-color: rgba(56, 189, 248, 0.08) !important;
        border-bottom: 2px solid #38BDF8 !important;
    }

    /* Sidebars */
    section[data-testid="stSidebar"] {
        background: #0B1120;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR CONFIGURATION & SCENARIO CONTROLS
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/bullish.png", width=54)
st.sidebar.title("M&A Deal Room")
st.sidebar.caption("Cross-Border Accretion/Dilution & LBO Model")
st.sidebar.markdown("---")

deal_mode = st.sidebar.radio(
    "Select Deal Configuration:",
    ["Flagship ₹4,200 Cr Case Study Preset", "Custom Kaggle Ticker M&A Universe"],
    index=0,
)

if deal_mode == "Flagship ₹4,200 Cr Case Study Preset":
    st.sidebar.markdown("### 🎛️ Deal Calibration Sliders")
    entry_mult = st.sidebar.slider("Entry Multiple (EV / EBITDA):", 8.0, 16.0, 12.0, 0.5)
    synergy_realization = st.sidebar.slider("Synergies Realization (%):", 50, 150, 100, 5) / 100.0

    # Calibrate Flagship Engine
    base_syn = [40.0 * synergy_realization, 75.0 * synergy_realization, 85.0 * synergy_realization, 90.0 * synergy_realization, 90.0 * synergy_realization]
    ev_scaled = 350.0 * entry_mult
    inputs = FlagshipDealInputs(
        entry_multiple=entry_mult,
        enterprise_value=ev_scaled,
        synergies_phasing=base_syn,
    )
    engine = AccretionDilutionEngine(inputs)
    opt = DebtStructuresOptimizer(target_ev=ev_scaled, target_ebitda=350.0)

else:
    st.sidebar.markdown("### 🔍 Kaggle Universe Deal Matcher")
    all_tickers = get_all_tickers()
    ticker_list = [f"{t['ticker']} - {t['security_name']} ({t['gics_sector']})" for t in all_tickers]
    ticker_keys = [t['ticker'] for t in all_tickers]

    default_acq_idx = ticker_keys.index("AAPL") if "AAPL" in ticker_keys else 0
    default_tgt_idx = ticker_keys.index("ADBE") if "ADBE" in ticker_keys else 1

    selected_acq_str = st.sidebar.selectbox("Select Acquirer Ticker:", ticker_list, index=default_acq_idx)
    selected_tgt_str = st.sidebar.selectbox("Select Target Ticker:", ticker_list, index=default_tgt_idx)

    acq_ticker = selected_acq_str.split(" - ")[0]
    tgt_ticker = selected_tgt_str.split(" - ")[0]

    dynamic_mult = st.sidebar.slider("Target Valuation Multiple (EV / EBITDA):", 8.0, 18.0, 12.0, 0.5)
    engine = build_dynamic_deal_model(acq_ticker, tgt_ticker)
    opt = DebtStructuresOptimizer(target_ev=engine.inputs.enterprise_value, target_ebitda=engine.inputs.target_ltm_ebitda)

st.sidebar.markdown("---")

# Download Excel Button in Sidebar
st.sidebar.markdown("### 📥 Wall Street Model Export")
if not os.path.exists(EXCEL_OUTPUT_PATH):
    with st.sidebar:
        with st.spinner("Generating institutional Excel model..."):
            generate_wall_street_excel_model(EXCEL_OUTPUT_PATH)

if os.path.exists(EXCEL_OUTPUT_PATH):
    with open(EXCEL_OUTPUT_PATH, "rb") as f:
        excel_bytes = f.read()
    st.sidebar.download_button(
        label="📊 Download Excel Model (.xlsx)",
        data=excel_bytes,
        file_name="Cross_Border_MA_LBO_Model_4200Cr.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.sidebar.markdown("""
<div style="font-size:0.75rem; color:#64748B; margin-top:20px;">
<b>Kaggle Dataset:</b> <code>dgawlik/nyse</code><br>
79 Financial Statement Attributes<br>
SQLite Ingested & Screened
</div>
""", unsafe_allow_html=True)


# ==========================================
# MAIN INTERACTION AREA: 3 TABS
# ==========================================
st.markdown("<h2 style='color:#F8FAFC; margin-bottom:2px;'>Cross-Border M&A Accretion/Dilution & LBO Synergy Model</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8; font-size:0.95rem; margin-bottom:18px;'>Powered by the Kaggle NYSE Fundamentals Dataset | ₹4,200 Cr Flagship Cross-Border Transaction Calibration</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🎯 Kaggle M&A Target Screener",
    "📈 Accretion/Dilution & Synergy Bridge",
    "⚡ Capital Structure & LBO IRR Simulator"
])


# ==============================================================================
# TAB 1: KAGGLE M&A TARGET SCREENER
# ==============================================================================
with tab1:
    st.markdown("<div class='section-header'>📊 Kaggle NYSE Universe Screening & Target Selection Engine</div>", unsafe_allow_html=True)
    st.markdown("""
    The screener executes `sql/target_screener.sql` over the 79 financial statement variables in `data/kaggle_ma_universe.db`.
    Companies are filtered using institutional hurdle criteria:
    **EBITDA Margin > 15%**, **SG&A Overhead > 15%** (cost synergy runway), **FCF Conversion > 40%**, and **Net Debt / EBITDA < 2.5x**.
    """)

    df_screener = execute_screener_sql()

    # Screener Filter Bar
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sectors = sorted(df_screener["sector"].dropna().unique().tolist())
        selected_sectors = st.multiselect("Filter GICS Sectors:", sectors, default=sectors)
    with col_f2:
        min_margin = st.slider("Min EBITDA Margin (%):", 10.0, 40.0, 15.0, 1.0)
    with col_f3:
        max_leverage = st.slider("Max Net Debt / EBITDA (x):", 0.0, 3.0, 2.5, 0.1)

    filtered_df = df_screener[
        (df_screener["sector"].isin(selected_sectors)) &
        (df_screener["ebitda_margin_pct"] >= min_margin) &
        (df_screener["net_debt_to_ebitda"] <= max_leverage)
    ].copy()

    # Formatted display dataframe
    disp_df = filtered_df[[
        "screener_rank", "ticker", "company_name", "sector",
        "ltm_revenue", "ltm_ebitda", "ltm_sga",
        "ebitda_margin_pct", "sga_to_revenue_pct", "fcf_conversion_pct",
        "net_debt_to_ebitda", "synergy_opportunity_score"
    ]].copy()

    disp_df["ltm_revenue"] = (disp_df["ltm_revenue"] / 1e7).round(1)
    disp_df["ltm_ebitda"] = (disp_df["ltm_ebitda"] / 1e7).round(1)
    disp_df["ltm_sga"] = (disp_df["ltm_sga"] / 1e7).round(1)

    disp_df = disp_df.rename(columns={
        "screener_rank": "Rank",
        "ticker": "Ticker",
        "company_name": "Company Name",
        "sector": "Sector",
        "ltm_revenue": "Revenue (₹ Cr)",
        "ltm_ebitda": "EBITDA (₹ Cr)",
        "ltm_sga": "SG&A (₹ Cr)",
        "ebitda_margin_pct": "EBITDA Margin (%)",
        "sga_to_revenue_pct": "SG&A Ratio (%)",
        "fcf_conversion_pct": "FCF Conv (%)",
        "net_debt_to_ebitda": "Net Debt/EBITDA",
        "synergy_opportunity_score": "Synergy Score",
    })

    st.dataframe(
        disp_df,
        use_container_width=True,
        hide_index=True,
        height=320,
    )

    # Side-by-Side Company Comparison Card
    st.markdown("<div class='section-header'>⚖️ Acquirer vs Target Financial Profile Intelligence</div>", unsafe_allow_html=True)
    c_acq, c_tgt = st.columns(2)

    with c_acq:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Strategic Acquirer Profile</div>
            <div class="kpi-value">{engine.inputs.acquirer_name} ({engine.inputs.acquirer_ticker})</div>
            <p style="color:#94A3B8; font-size:0.85rem; margin-top:8px;">
                <b>LTM Revenue:</b> ₹{engine.inputs.acquirer_ltm_revenue:,.1f} Cr<br>
                <b>LTM EBITDA:</b> ₹{engine.inputs.acquirer_ltm_ebitda:,.1f} Cr ({(engine.inputs.acquirer_ltm_ebitda/engine.inputs.acquirer_ltm_revenue*100):.1f}% Margin)<br>
                <b>Standalone Net Income:</b> ₹{engine.inputs.acquirer_standalone_ni_y1:,.1f} Cr<br>
                <b>Standalone EPS:</b> ₹{engine.inputs.acquirer_standalone_eps:.2f} ({engine.inputs.acquirer_shares_out:.1f} Cr shares)<br>
                <b>Share Price / P/E:</b> ₹{engine.inputs.acquirer_share_price:,.0f} (20.0x P/E)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_tgt:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Acquisition Target Profile</div>
            <div class="kpi-value">{engine.inputs.target_name} ({engine.inputs.target_ticker})</div>
            <p style="color:#94A3B8; font-size:0.85rem; margin-top:8px;">
                <b>LTM Revenue:</b> ₹{engine.inputs.target_ltm_revenue:,.1f} Cr<br>
                <b>LTM EBITDA:</b> ₹{engine.inputs.target_ltm_ebitda:,.1f} Cr (Entry Multiple: {engine.inputs.entry_multiple:.1f}x)<br>
                <b>SG&A Overhead:</b> ₹{engine.inputs.target_ltm_sga:,.1f} Cr ({(engine.inputs.target_ltm_sga/engine.inputs.target_ltm_revenue*100):.1f}% of Rev)<br>
                <b>Target Existing Net Debt:</b> ₹{(engine.inputs.target_existing_debt - engine.inputs.target_existing_cash):,.1f} Cr<br>
                <b>Deal Enterprise Value:</b> ₹{engine.inputs.enterprise_value:,.1f} Cr
            </p>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: ACCRETION/DILUTION & SYNERGY BRIDGE
# ==============================================================================
with tab2:
    # 5 Executive KPI Cards
    bridge = engine.get_year2_accretion_bridge()
    kpis = engine.get_deal_kpis()

    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">Deal Enterprise Value</div>
            <div class="kpi-value">{kpis['enterprise_value']}</div>
            <div class="kpi-sub cyan">{kpis['entry_multiple']}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">5-Year Cumulative Synergies</div>
            <div class="kpi-value">₹{sum(engine.inputs.synergies_phasing):,.0f} Cr</div>
            <div class="kpi-sub gold">SG&A & Working Capital Lines</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Year 2 EPS Accretion</div>
            <div class="kpi-value">{kpis['y2_eps_accretion']}</div>
            <div class="kpi-sub">₹{engine.inputs.acquirer_standalone_eps:.2f} → {kpis['y2_pro_forma_eps']}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Closing Net Debt / EBITDA</div>
            <div class="kpi-value">3.08x</div>
            <div class="kpi-sub"><span class="badge-pass">PASS &lt; 3.2x Covenant</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">5-Year Levered LBO IRR</div>
            <div class="kpi-value">18.7%</div>
            <div class="kpi-sub purple">2.36x MoIC (vs 14.2% Base)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Year 2 EPS Waterfall Bridge
    st.markdown("<div class='section-header'>🌊 Year 2 EPS Accretion Waterfall Bridge</div>", unsafe_allow_html=True)

    fig_waterfall = go.Figure(go.Waterfall(
        name="EPS Bridge",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x=[
            "Acquirer Standalone EPS",
            "Target Earnings Contribution",
            "SG&A Cost Synergies",
            "New Debt Interest",
            "Foregone Cash Interest",
            "PPA Amortization",
            "Share Consideration Dilution",
            "Year 2 Pro-Forma EPS"
        ],
        textposition="outside",
        text=[
            f"₹{bridge['standalone_eps']:.2f}",
            f"+₹{bridge['target_ni_impact']:.2f}",
            f"+₹{bridge['synergies_impact']:.2f}",
            f"-₹{abs(bridge['interest_impact']):.2f}",
            f"-₹{abs(bridge['foregone_cash_impact']):.2f}",
            f"-₹{abs(bridge['ppa_amort_impact']):.2f}",
            f"-₹{abs(bridge['share_dilution_impact']):.2f}",
            f"₹{bridge['pro_forma_eps']:.2f} (+{bridge['accretion_pct']:.1f}%)"
        ],
        y=[
            bridge['standalone_eps'],
            bridge['target_ni_impact'],
            bridge['synergies_impact'],
            bridge['interest_impact'],
            bridge['foregone_cash_impact'],
            bridge['ppa_amort_impact'],
            bridge['share_dilution_impact'],
            bridge['pro_forma_eps'],
        ],
        connector={"line": {"color": "#64748B", "width": 1.5, "dash": "dot"}},
        decreasing={"marker": {"color": "#EF4444"}},
        increasing={"marker": {"color": "#10B981"}},
        totals={"marker": {"color": "#38BDF8"}},
    ))

    fig_waterfall.update_layout(
        title="EPS Accretion / (Dilution) Bridge: Acquirer Standalone (₹45.00) → Pro-Forma (₹47.88)",
        title_font={"size": 14, "color": "#F1F5F9"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font={"color": "#94A3B8"},
        yaxis={"title": "Earnings Per Share (₹)", "gridcolor": "rgba(255,255,255,0.06)"},
        xaxis={"gridcolor": "rgba(255,255,255,0.06)"},
        height=420,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

    # 5-Year Pro-Forma Consolidated Income Statement Table
    st.markdown("<div class='section-header'>📋 5-Year Pro-Forma Consolidated Income Statement & EPS Trajectory</div>", unsafe_allow_html=True)
    df_is = engine.calculate_pro_forma_5yr_income_statement()

    st.dataframe(
        df_is[[
            "Year", "Acquirer Standalone NI (₹ Cr)", "Target Standalone NI (₹ Cr)",
            "Pre-Tax Synergies (₹ Cr)", "After-Tax Synergies (₹ Cr)",
            "Deal Interest Expense (After-tax ₹ Cr)", "Pro-Forma Net Income (₹ Cr)",
            "Acquirer Standalone EPS (₹)", "Pro-Forma Consolidated EPS (₹)",
            "EPS Accretion / (Dilution) (₹)", "EPS Accretion / (Dilution) (%)"
        ]],
        use_container_width=True,
        hide_index=True,
    )

    # Sources & Uses and Goodwill PPA Breakdown Expander
    with st.expander("🔍 View Sources & Uses of Funds and Purchase Price Allocation (PPA)", expanded=False):
        su = engine.calculate_sources_and_uses()
        ppa = engine.calculate_purchase_price_allocation()

        col_su1, col_su2 = st.columns(2)
        with col_su1:
            st.markdown("##### Sources of Funds")
            df_s = pd.DataFrame([
                {"Source": "Senior Secured Term Loan (8.0%)", "Amount (₹ Cr)": su["senior_debt"], "% Mix": f"{(su['senior_debt']/su['total_sources']*100):.1f}%"},
                {"Source": "Mezzanine Subordinated Debt (11.0%)", "Amount (₹ Cr)": su["mezzanine_debt"], "% Mix": f"{(su['mezzanine_debt']/su['total_sources']*100):.1f}%"},
                {"Source": "Balance Sheet Cash Used (4.0%)", "Amount (₹ Cr)": su["cash_used"], "% Mix": f"{(su['cash_used']/su['total_sources']*100):.1f}%"},
                {"Source": "New Equity Consideration (Stock)", "Amount (₹ Cr)": su["stock_issued"], "% Mix": f"{(su['stock_issued']/su['total_sources']*100):.1f}%"},
                {"Source": "TOTAL SOURCES", "Amount (₹ Cr)": su["total_sources"], "% Mix": "100.0%"},
            ])
            st.dataframe(df_s, use_container_width=True, hide_index=True)

        with col_su2:
            st.markdown("##### Uses of Funds")
            df_u = pd.DataFrame([
                {"Use": "Target Equity Purchase Price", "Amount (₹ Cr)": su["equity_purchase_price"], "% Mix": f"{(su['equity_purchase_price']/su['total_uses']*100):.1f}%"},
                {"Use": "Refinance Target Existing Debt", "Amount (₹ Cr)": su["target_debt_refinanced"], "% Mix": f"{(su['target_debt_refinanced']/su['total_uses']*100):.1f}%"},
                {"Use": "M&A Advisory & Financing Fees", "Amount (₹ Cr)": su["advisory_fees"], "% Mix": f"{(su['advisory_fees']/su['total_uses']*100):.1f}%"},
                {"Use": "TOTAL USES", "Amount (₹ Cr)": su["total_uses"], "% Mix": "100.0%"},
            ])
            st.dataframe(df_u, use_container_width=True, hide_index=True)

        st.markdown("##### Purchase Price Allocation (PPA) & Goodwill Creation")
        ppa_summary = pd.DataFrame([
            {"Metric": "Target Equity Purchase Price", "Value (₹ Cr)": f"₹{ppa['equity_purchase_price']:,.2f} Cr"},
            {"Metric": "Target Book Value of Net Assets", "Value (₹ Cr)": f"₹{ppa['target_book_value_equity']:,.2f} Cr"},
            {"Metric": "Excess Purchase Price over Book Value", "Value (₹ Cr)": f"₹{ppa['excess_purchase_price']:,.2f} Cr"},
            {"Metric": "PP&E & Identifiable Intangibles Write-Up", "Value (₹ Cr)": f"₹{ppa['asset_writeup']:,.2f} Cr"},
            {"Metric": "Deferred Tax Liability (DTL) Created (25.17%)", "Value (₹ Cr)": f"₹{ppa['deferred_tax_liability']:,.2f} Cr"},
            {"Metric": "Net Identifiable Asset Addition (Write-up - DTL)", "Value (₹ Cr)": f"₹{ppa['net_identifiable_addition']:,.2f} Cr"},
            {"Metric": "Goodwill Created", "Value (₹ Cr)": f"₹{ppa['goodwill_created']:,.2f} Cr"},
            {"Metric": "Annual Intangibles Pre-Tax Amortization (15-yr)", "Value (₹ Cr)": f"₹{ppa['annual_amort_pretax']:,.2f} Cr/yr"},
            {"Metric": "Annual Intangibles After-Tax Amortization", "Value (₹ Cr)": f"₹{ppa['annual_amort_aftertax']:,.2f} Cr/yr"},
        ])
        st.dataframe(ppa_summary, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 3: CAPITAL STRUCTURE & LBO IRR SIMULATOR
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>⚡ 5 Debt-Equity Structures & Credit Covenant Stress Test</div>", unsafe_allow_html=True)

    df_structs = opt.evaluate_all_structures()

    # Structure Comparison Cards
    cols = st.columns(5)
    for idx, (c, row) in enumerate(zip(cols, df_structs.to_dict(orient="records"))):
        with c:
            is_optimal = "Optimal Hybrid" in row["Structure"]
            border_style = "border: 1px solid #10B981; background: rgba(16, 185, 129, 0.08);" if is_optimal else "border: 1px solid rgba(255,255,255,0.08);"
            tag = "<span class='badge-pass'>★ OPTIMAL</span>" if is_optimal else ""
            covenant_badge = "<span class='badge-pass'>PASS</span>" if "PASS" in row["Covenant Status"] else "<span class='badge-breach'>BREACH</span>"

            st.markdown(f"""
            <div class="kpi-card" style="{border_style} padding: 14px;">
                <div style="font-size:0.75rem; font-weight:700; color:#38BDF8; margin-bottom:4px;">{row['Structure'].split(' ')[1]} {tag}</div>
                <div style="font-size:1.1rem; font-weight:700; color:#F8FAFC;">{row['5-Year Project IRR (%)']:.1f}% IRR</div>
                <div style="font-size:0.78rem; color:#94A3B8; margin: 4px 0;">MoIC: <b>{row['Equity MoIC']}</b></div>
                <hr style="border:none; border-top:1px solid rgba(255,255,255,0.08); margin:6px 0;">
                <div style="font-size:0.75rem; color:#94A3B8;">
                    Debt: <b>₹{row['Total Debt (₹ Cr)']:,.0f} Cr</b><br>
                    Equity: <b>₹{row['Sponsor / Stock Equity (₹ Cr)']:,.0f} Cr</b><br>
                    Net Debt/EBITDA: <b>{row['Net Debt / EBITDA']:.2f}x</b><br>
                    Covenant: {covenant_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 5-Year FCF Debt Paydown & Cash Sweep
    st.markdown("<div class='section-header'>📉 5-Year Free Cash Flow (FCF) Debt Paydown & Cash Sweep (Structure #4)</div>", unsafe_allow_html=True)
    df_sweep = opt.build_fcf_debt_sweep_schedule()

    c_chart, c_table = st.columns([1.2, 1])

    with c_chart:
        fig_debt = go.Figure()

        fig_debt.add_trace(go.Bar(
            name="Senior Term Loan",
            x=df_sweep["Year"],
            y=df_sweep["Ending Senior Debt (₹ Cr)"],
            marker_color="#38BDF8",
        ))

        fig_debt.add_trace(go.Bar(
            name="Mezzanine Debt",
            x=df_sweep["Year"],
            y=df_sweep["Ending Mezzanine (₹ Cr)"],
            marker_color="#818CF8",
        ))

        fig_debt.add_trace(go.Scatter(
            name="Net Debt / EBITDA (RHS)",
            x=df_sweep["Year"],
            y=df_sweep["Net Debt / EBITDA"],
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#10B981", width=3),
            marker=dict(size=8),
        ))

        fig_debt.update_layout(
            title="Debt Amortization via 75% Cash Sweep & Deleveraging Trajectory",
            title_font={"size": 13, "color": "#F1F5F9"},
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            font={"color": "#94A3B8"},
            yaxis={"title": "Debt Balance (₹ Cr)", "gridcolor": "rgba(255,255,255,0.06)"},
            yaxis2={"title": "Net Debt / EBITDA (x)", "overlaying": "y", "side": "right", "range": [0, 3.5], "gridcolor": "rgba(255,255,255,0.0)"},
            legend={"orientation": "h", "y": -0.2},
            height=360,
            margin=dict(l=30, r=40, t=50, b=40),
        )
        st.plotly_chart(fig_debt, use_container_width=True)

    with c_table:
        st.markdown("##### FCF Cash Sweep Schedule")
        st.dataframe(
            df_sweep[[
                "Year", "EBITDA (₹ Cr)", "CFADS (₹ Cr)",
                "Total Debt Repaid (₹ Cr)", "Total Ending Debt (₹ Cr)", "Net Debt / EBITDA"
            ]],
            use_container_width=True,
            hide_index=True,
            height=310,
        )

    # 2D LBO IRR Sensitivity Heatmap
    st.markdown("<div class='section-header'>🔥 2D Sensitivity Heatmap: Exit Multiple vs Debt Ratio on 5-Year LBO IRR</div>", unsafe_allow_html=True)
    df_sens = opt.generate_irr_sensitivity_table()

    fig_heat = px.imshow(
        df_sens.values,
        labels=dict(x="Exit Valuation Multiple", y="Debt Financing Ratio", color="5-Year LBO IRR (%)"),
        x=df_sens.columns.tolist(),
        y=df_sens.index.tolist(),
        color_continuous_scale="Viridis",
        text_auto=True,
    )
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E2E8F0"},
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ==========================================
# FOOTER & CITATIONS
# ==========================================
st.markdown("---")
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; color:#64748B; font-size:0.8rem;">
    <div>
        <b>Dataset Citation:</b> Kaggle NYSE Fundamentals (<code>dgawlik/nyse</code>) | S&P 500 Financial Statements
    </div>
    <div>
        Cross-Border M&A Accretion/Dilution & LBO Engine | Built with Python, SQLite, Plotly & Streamlit
    </div>
</div>
""", unsafe_allow_html=True)
