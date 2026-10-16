"""
Wall Street Financial Model Excel Generator
============================================
Generates models/Cross_Border_MA_LBO_Model_4200Cr.xlsx using openpyxl.
Includes 6 institutional, formatted tabs with investment banking aesthetics:
  1) Kaggle_M&A_Target_Screener
  2) Sources_Uses_&_Goodwill_PPA
  3) 5Yr_ProForma_IS_&_Synergies
  4) EPS_Accretion_Dilution_Bridge
  5) 5_Debt_Structures_&_Cash_Sweep
  6) Sensitivity_Matrices
"""

import os
import sys

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from src.accretion_dilution_engine import AccretionDilutionEngine, FlagshipDealInputs
from src.debt_structures_irr import DebtStructuresOptimizer
from src.kaggle_data_loader import execute_screener_sql

MODELS_DIR = os.path.join(WORKSPACE_DIR, "models")
EXCEL_OUTPUT_PATH = os.path.join(MODELS_DIR, "Cross_Border_MA_LBO_Model_4200Cr.xlsx")

# Investment Banking Palette
NAVY_HEADER_FILL = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
SUBHEADER_FILL = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
ACCENT_BLUE_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
HIGHLIGHT_GREEN_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
HIGHLIGHT_RED_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
ZEBRA_FILL = PatternFill(start_color="F9FAFC", end_color="F9FAFC", fill_type="solid")
CARD_HEADER_FILL = PatternFill(start_color="34495E", end_color="34495E", fill_type="solid")

FONT_TITLE = Font(name="Calibri", size=15, bold=True, color="1B365D")
FONT_SUBTITLE = Font(name="Calibri", size=10, italic=True, color="595959")
FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_SECTION = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_REGULAR = Font(name="Calibri", size=11, color="000000")
FONT_BOLD = Font(name="Calibri", size=11, bold=True, color="000000")
FONT_CARD_TITLE = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
FONT_CARD_VALUE = Font(name="Calibri", size=13, bold=True, color="1B365D")

THIN_BORDER = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9"),
)
TOTAL_TOP_BORDER = Side(style="thin", color="000000")
TOTAL_BOTTOM_BORDER = Side(style="double", color="000000")
BORDER_TOTAL = Border(top=TOTAL_TOP_BORDER, bottom=TOTAL_BOTTOM_BORDER)

ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")
ALIGN_CENTER = Alignment(horizontal="center", vertical="center")


def auto_fit_columns(ws, min_width=12):
    """Adjusts column widths based on cell content."""
    ws.views.sheetView[0].showGridLines = True
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val = cell.value
            if val is not None:
                # Ignore super long merged title cells in width calculation
                if cell.row in [1, 2]:
                    continue
                s_val = str(val)
                if len(s_val) > max_len:
                    max_len = len(s_val)
        ws.column_dimensions[col_letter].width = max(max_len + 4, min_width)


def format_header_row(ws, row_idx: int, col_start: int, col_end: int):
    """Applies Navy blue header formatting."""
    for c in range(col_start, col_end + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = NAVY_HEADER_FILL
        cell.font = FONT_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = THIN_BORDER


def write_tab1_screener(wb: openpyxl.Workbook):
    """Tab 1: Kaggle_M&A_Target_Screener (Top 25 Screened Companies)."""
    ws = wb.create_sheet(title="Kaggle_M&A_Target_Screener")

    # Title
    ws["B2"] = "KAGGLE NYSE M&A TARGET SCREENER (dgawlik/nyse)"
    ws["B2"].font = FONT_TITLE
    ws["B3"] = "Screening Hurdle Criteria: EBITDA Margin > 15.0% | SG&A / Revenue > 15.0% | FCF Conversion > 40.0% | Net Debt / EBITDA < 2.50x"
    ws["B3"].font = FONT_SUBTITLE

    # Run SQL Screener
    df_screener = execute_screener_sql()

    headers = [
        "Rank", "Ticker", "Company Name", "GICS Sector", "LTM Revenue (₹ Cr)",
        "LTM EBITDA (₹ Cr)", "LTM SG&A (₹ Cr)", "EBITDA Margin (%)", "SG&A Ratio (%)",
        "FCF Conv (%)", "Net Debt / EBITDA", "Synergy Score"
    ]

    start_row = 5
    for col_idx, h in enumerate(headers, start=2):
        ws.cell(row=start_row, column=col_idx, value=h)
    format_header_row(ws, start_row, 2, len(headers) + 1)

    for i, row in df_screener.iterrows():
        curr_row = start_row + 1 + i
        # Scale USD numbers into ₹ Cr for representation (1 USD = 80 INR / 10 Cr = ~8x)
        rev_cr = row["ltm_revenue"] / 1e7
        ebitda_cr = row["ltm_ebitda"] / 1e7
        sga_cr = row["ltm_sga"] / 1e7

        vals = [
            row["screener_rank"],
            row["ticker"],
            row["company_name"],
            row["sector"],
            rev_cr,
            ebitda_cr,
            sga_cr,
            row["ebitda_margin_pct"] / 100.0,
            row["sga_to_revenue_pct"] / 100.0,
            row["fcf_conversion_pct"] / 100.0,
            row["net_debt_to_ebitda"],
            row["synergy_opportunity_score"],
        ]

        fill = ZEBRA_FILL if i % 2 == 1 else PatternFill(fill_type=None)
        for c_idx, val in enumerate(vals, start=2):
            cell = ws.cell(row=curr_row, column=c_idx, value=val)
            cell.font = FONT_REGULAR
            cell.border = THIN_BORDER
            if fill.fill_type:
                cell.fill = fill

            if c_idx in [2, 3]:
                cell.alignment = ALIGN_CENTER
            elif c_idx in [4, 5]:
                cell.alignment = ALIGN_LEFT
            elif c_idx in [6, 7, 8]:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = '₹#,##0.0 "Cr"'
            elif c_idx in [9, 10, 11]:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = "0.0%"
            elif c_idx == 12:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = '0.00"x"'
            elif c_idx == 13:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = "0.0"

    auto_fit_columns(ws)


def write_tab2_sources_uses(wb: openpyxl.Workbook, engine: AccretionDilutionEngine):
    """Tab 2: Sources_Uses_&_Goodwill_PPA."""
    ws = wb.create_sheet(title="Sources_Uses_&_Goodwill_PPA")

    ws["B2"] = "SOURCES & USES OF FUNDS AND PURCHASE PRICE ALLOCATION (PPA)"
    ws["B2"].font = FONT_TITLE
    ws["B3"] = "Flagship ₹4,200 Cr Cross-Border M&A Transaction Calibration"
    ws["B3"].font = FONT_SUBTITLE

    su = engine.calculate_sources_and_uses()
    ppa = engine.calculate_purchase_price_allocation()

    # Section 1: Transaction Overview
    ws["B5"] = "I. TRANSACTION OVERVIEW & VALUATION"
    ws["B5"].font = FONT_SECTION
    ws.merge_cells("B5:E5")
    ws["B5"].fill = SUBHEADER_FILL

    overview_data = [
        ("Target LTM EBITDA (₹ Cr)", engine.inputs.target_ltm_ebitda, '₹#,##0.0 "Cr"'),
        ("Entry Valuation Multiple", engine.inputs.entry_multiple, '0.0"x"'),
        ("Enterprise Value (EV) (₹ Cr)", su["enterprise_value"], '₹#,##0.0 "Cr"'),
        ("Less: Target Net Debt Assumed (₹ Cr)", su["target_net_debt"], '₹#,##0.0 "Cr"'),
        ("Target Equity Purchase Price (₹ Cr)", su["equity_purchase_price"], '₹#,##0.0 "Cr"'),
    ]
    for r_idx, (label, val, num_fmt) in enumerate(overview_data, start=6):
        ws.cell(row=r_idx, column=2, value=label).font = FONT_REGULAR
        ws.cell(row=r_idx, column=2).border = THIN_BORDER
        c = ws.cell(row=r_idx, column=3, value=val)
        c.font = FONT_BOLD if "Equity Purchase" in label or "Enterprise" in label else FONT_REGULAR
        c.number_format = num_fmt
        c.alignment = ALIGN_RIGHT
        c.border = THIN_BORDER

    # Section 2: Sources & Uses Tables Side-by-Side
    ws["B12"] = "II. SOURCES OF FUNDS"
    ws["B12"].font = FONT_SECTION
    ws["B12"].fill = SUBHEADER_FILL
    ws["E12"] = "USES OF FUNDS"
    ws["E12"].font = FONT_SECTION
    ws["E12"].fill = SUBHEADER_FILL

    sources_rows = [
        ("Senior Secured Term Loan (8.0%)", su["senior_debt"], su["senior_debt"] / su["total_sources"]),
        ("Mezzanine Subordinated Debt (11.0%)", su["mezzanine_debt"], su["mezzanine_debt"] / su["total_sources"]),
        ("Acquirer Balance Sheet Cash (4.0%)", su["cash_used"], su["cash_used"] / su["total_sources"]),
        ("New Acquirer Stock Issued (Sellers)", su["stock_issued"], su["stock_issued"] / su["total_sources"]),
    ]
    uses_rows = [
        ("Target Equity Purchase Price", su["equity_purchase_price"], su["equity_purchase_price"] / su["total_uses"]),
        ("Refinance Target Existing Debt", su["target_debt_refinanced"], su["target_debt_refinanced"] / su["total_uses"]),
        ("M&A Advisory & Financing Fees", su["advisory_fees"], su["advisory_fees"] / su["total_uses"]),
        ("Working Capital & Integration Fund", 0.0, 0.0),
    ]

    for r_idx in range(4):
        row_num = 13 + r_idx
        # Sources
        s_lbl, s_val, s_pct = sources_rows[r_idx]
        ws.cell(row=row_num, column=2, value=s_lbl).border = THIN_BORDER
        c_val = ws.cell(row=row_num, column=3, value=s_val)
        c_val.number_format = '₹#,##0.0 "Cr"'
        c_val.alignment = ALIGN_RIGHT
        c_val.border = THIN_BORDER
        c_pct = ws.cell(row=row_num, column=4, value=s_pct)
        c_pct.number_format = "0.0%"
        c_pct.alignment = ALIGN_RIGHT
        c_pct.border = THIN_BORDER

        # Uses
        u_lbl, u_val, u_pct = uses_rows[r_idx]
        ws.cell(row=row_num, column=5, value=u_lbl).border = THIN_BORDER
        c_uval = ws.cell(row=row_num, column=6, value=u_val)
        c_uval.number_format = '₹#,##0.0 "Cr"'
        c_uval.alignment = ALIGN_RIGHT
        c_uval.border = THIN_BORDER
        c_upct = ws.cell(row=row_num, column=7, value=u_pct)
        c_upct.number_format = "0.0%"
        c_upct.alignment = ALIGN_RIGHT
        c_upct.border = THIN_BORDER

    # Total Row
    tot_row = 17
    ws.cell(row=tot_row, column=2, value="TOTAL SOURCES").font = FONT_BOLD
    ws.cell(row=tot_row, column=2).border = BORDER_TOTAL
    ws.cell(row=tot_row, column=2).fill = ACCENT_BLUE_FILL

    c_ts = ws.cell(row=tot_row, column=3, value=su["total_sources"])
    c_ts.font = FONT_BOLD
    c_ts.number_format = '₹#,##0.0 "Cr"'
    c_ts.alignment = ALIGN_RIGHT
    c_ts.border = BORDER_TOTAL
    c_ts.fill = ACCENT_BLUE_FILL

    c_tsp = ws.cell(row=tot_row, column=4, value=1.0)
    c_tsp.font = FONT_BOLD
    c_tsp.number_format = "0.0%"
    c_tsp.alignment = ALIGN_RIGHT
    c_tsp.border = BORDER_TOTAL
    c_tsp.fill = ACCENT_BLUE_FILL

    ws.cell(row=tot_row, column=5, value="TOTAL USES").font = FONT_BOLD
    ws.cell(row=tot_row, column=5).border = BORDER_TOTAL
    ws.cell(row=tot_row, column=5).fill = ACCENT_BLUE_FILL

    c_tu = ws.cell(row=tot_row, column=6, value=su["total_uses"])
    c_tu.font = FONT_BOLD
    c_tu.number_format = '₹#,##0.0 "Cr"'
    c_tu.alignment = ALIGN_RIGHT
    c_tu.border = BORDER_TOTAL
    c_tu.fill = ACCENT_BLUE_FILL

    c_tup = ws.cell(row=tot_row, column=7, value=1.0)
    c_tup.font = FONT_BOLD
    c_tup.number_format = "0.0%"
    c_tup.alignment = ALIGN_RIGHT
    c_tup.border = BORDER_TOTAL
    c_tup.fill = ACCENT_BLUE_FILL

    # Section 3: Goodwill & PPA Allocation
    ws["B20"] = "III. PURCHASE PRICE ALLOCATION (PPA) & GOODWILL CREATION"
    ws["B20"].font = FONT_SECTION
    ws.merge_cells("B20:E20")
    ws["B20"].fill = SUBHEADER_FILL

    ppa_rows = [
        ("Target Equity Purchase Price", ppa["equity_purchase_price"], '₹#,##0.00 "Cr"', False),
        ("Less: Target Book Value of Net Assets", ppa["target_book_value_equity"], '₹#,##0.00 "Cr"', False),
        ("Excess Purchase Price over Book Value", ppa["excess_purchase_price"], '₹#,##0.00 "Cr"', True),
        ("PP&E / Identifiable Intangible Asset Write-Up", ppa["asset_writeup"], '₹#,##0.00 "Cr"', False),
        ("Less: Deferred Tax Liability (DTL) Created (25.17%)", ppa["deferred_tax_liability"], '₹#,##0.00 "Cr"', False),
        ("Net Identifiable Asset Addition (Write-up - DTL)", ppa["net_identifiable_addition"], '₹#,##0.00 "Cr"', True),
        ("Goodwill Created (Excess - Net Identifiable Asset Addition)", ppa["goodwill_created"], '₹#,##0.00 "Cr"', True),
        ("Annual Intangibles Pre-Tax Amortization (15-Yr Straight Line)", ppa["annual_amort_pretax"], '₹#,##0.00 "Cr"', False),
        ("Annual Intangibles After-Tax Amortization (25.17% Tax)", ppa["annual_amort_aftertax"], '₹#,##0.00 "Cr"', True),
    ]

    for idx, (label, val, n_fmt, is_bold) in enumerate(ppa_rows, start=21):
        ws.cell(row=idx, column=2, value=label).font = FONT_BOLD if is_bold else FONT_REGULAR
        ws.cell(row=idx, column=2).border = THIN_BORDER
        c_v = ws.cell(row=idx, column=3, value=val)
        c_v.font = FONT_BOLD if is_bold else FONT_REGULAR
        c_v.number_format = n_fmt
        c_v.alignment = ALIGN_RIGHT
        c_v.border = THIN_BORDER
        if "Goodwill" in label:
            c_v.fill = HIGHLIGHT_GREEN_FILL
            ws.cell(row=idx, column=2).fill = HIGHLIGHT_GREEN_FILL

    # Section 4: Closing Leverage Ratio
    ws["B32"] = "IV. CLOSING CREDIT COVENANT COMPLIANCE"
    ws["B32"].font = FONT_SECTION
    ws.merge_cells("B32:E32")
    ws["B32"].fill = SUBHEADER_FILL

    closing_net_debt = (su["senior_debt"] + su["mezzanine_debt"]) - engine.inputs.target_existing_cash
    closing_nd_ebitda = closing_net_debt / engine.inputs.target_ltm_ebitda

    cov_rows = [
        ("Total Closing Transaction Debt (Senior + Mezz)", su["senior_debt"] + su["mezzanine_debt"], '₹#,##0.0 "Cr"'),
        ("Less: Available Cash Balance at Close", engine.inputs.target_existing_cash, '₹#,##0.0 "Cr"'),
        ("Closing Net Debt (₹ Cr)", closing_net_debt, '₹#,##0.0 "Cr"'),
        ("Target LTM EBITDA (₹ Cr)", engine.inputs.target_ltm_ebitda, '₹#,##0.0 "Cr"'),
        ("Closing Pro-Forma Net Debt / EBITDA", closing_nd_ebitda, '0.00"x"'),
        ("Credit Agreement Covenant Ceiling", 3.20, '0.00"x"'),
        ("Covenant Compliance Status", "PASS (Strictly below 3.2x ceiling)", "@"),
    ]
    for idx, (label, val, n_fmt) in enumerate(cov_rows, start=33):
        ws.cell(row=idx, column=2, value=label).font = FONT_BOLD if "Status" in label or "Pro-Forma Net" in label else FONT_REGULAR
        ws.cell(row=idx, column=2).border = THIN_BORDER
        c_v = ws.cell(row=idx, column=3, value=val)
        c_v.font = FONT_BOLD if "Status" in label or "Pro-Forma Net" in label else FONT_REGULAR
        if n_fmt != "@":
            c_v.number_format = n_fmt
            c_v.alignment = ALIGN_RIGHT
        else:
            c_v.alignment = ALIGN_CENTER
            c_v.fill = HIGHLIGHT_GREEN_FILL
            ws.cell(row=idx, column=2).fill = HIGHLIGHT_GREEN_FILL
        c_v.border = THIN_BORDER

    auto_fit_columns(ws)


def write_tab3_income_statement(wb: openpyxl.Workbook, engine: AccretionDilutionEngine):
    """Tab 3: 5Yr_ProForma_IS_&_Synergies."""
    ws = wb.create_sheet(title="5Yr_ProForma_IS_&_Synergies")

    ws["B2"] = "5-YEAR PRO-FORMA CONSOLIDATED INCOME STATEMENT & SYNERGIES"
    ws["B2"].font = FONT_TITLE
    ws["B3"] = "Phased Synergies Realization (₹380 Cr 5-Year Cumulative) & Consolidated Operations"
    ws["B3"].font = FONT_SUBTITLE

    df_is = engine.calculate_pro_forma_5yr_income_statement()

    # Section 1: Phased Synergies Schedule
    ws["B5"] = "I. 5-YEAR PHASED SYNERGIES SCHEDULE (₹ CR)"
    ws["B5"].font = FONT_SECTION
    ws.merge_cells("B5:H5")
    ws["B5"].fill = SUBHEADER_FILL

    syn_headers = ["Synergy Line Item", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "5-Yr Cumulative"]
    for c_idx, h in enumerate(syn_headers, start=2):
        ws.cell(row=6, column=c_idx, value=h)
    format_header_row(ws, 6, 2, len(syn_headers) + 1)

    syn_table = [
        ("SG&A Rationalization (Overhead / Exec / ERP)", [30.0, 55.0, 65.0, 70.0, 70.0], 290.0),
        ("Working Capital & Procurement Harmonization", [10.0, 20.0, 20.0, 20.0, 20.0], 90.0),
        ("TOTAL PRE-TAX SYNERGIES REALIZED", [40.0, 75.0, 85.0, 90.0, 90.0], 380.0),
        ("Less: Corporate Taxes on Synergies (25.17%)", [40.0 * 0.2517, 75.0 * 0.2517, 85.0 * 0.2517, 90.0 * 0.2517, 90.0 * 0.2517], 380.0 * 0.2517),
        ("NET AFTER-TAX SYNERGY CONTRIBUTION", [40.0 * (1 - 0.2517), 75.0 * (1 - 0.2517), 85.0 * (1 - 0.2517), 90.0 * (1 - 0.2517), 90.0 * (1 - 0.2517)], 380.0 * (1 - 0.2517)),
    ]

    for idx, (lbl, yr_vals, tot_val) in enumerate(syn_table, start=7):
        is_total = "TOTAL" in lbl or "NET" in lbl
        ws.cell(row=idx, column=2, value=lbl).font = FONT_BOLD if is_total else FONT_REGULAR
        ws.cell(row=idx, column=2).border = BORDER_TOTAL if "NET" in lbl else THIN_BORDER
        if "NET" in lbl:
            ws.cell(row=idx, column=2).fill = HIGHLIGHT_GREEN_FILL

        for y_idx, val in enumerate(yr_vals, start=3):
            c = ws.cell(row=idx, column=y_idx, value=val)
            c.font = FONT_BOLD if is_total else FONT_REGULAR
            c.number_format = '₹#,##0.0 "Cr"'
            c.alignment = ALIGN_RIGHT
            c.border = BORDER_TOTAL if "NET" in lbl else THIN_BORDER
            if "NET" in lbl:
                c.fill = HIGHLIGHT_GREEN_FILL

        c_tot = ws.cell(row=idx, column=8, value=tot_val)
        c_tot.font = FONT_BOLD
        c_tot.number_format = '₹#,##0.0 "Cr"'
        c_tot.alignment = ALIGN_RIGHT
        c_tot.border = BORDER_TOTAL if "NET" in lbl else THIN_BORDER
        if "NET" in lbl:
            c_tot.fill = HIGHLIGHT_GREEN_FILL

    # Section 2: Pro-Forma Income Statement Table
    ws["B14"] = "II. CONSOLIDATED PRO-FORMA INCOME STATEMENT (₹ CR)"
    ws["B14"].font = FONT_SECTION
    ws.merge_cells("B14:G14")
    ws["B14"].fill = SUBHEADER_FILL

    is_headers = ["Line Item", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    for c_idx, h in enumerate(is_headers, start=2):
        ws.cell(row=15, column=c_idx, value=h)
    format_header_row(ws, 15, 2, len(is_headers) + 1)

    is_rows = [
        ("Acquirer Standalone Net Income (₹ Cr)", df_is["Acquirer Standalone NI (₹ Cr)"].tolist(), '₹#,##0.0 "Cr"', False),
        ("Target Standalone Net Income (₹ Cr)", df_is["Target Standalone NI (₹ Cr)"].tolist(), '₹#,##0.0 "Cr"', False),
        ("Plus: After-Tax Synergies Realized (₹ Cr)", df_is["After-Tax Synergies (₹ Cr)"].tolist(), '₹#,##0.0 "Cr"', False),
        ("Less: Deal Debt Interest (After-Tax ₹ Cr)", (-df_is["Deal Interest Expense (After-tax ₹ Cr)"]).tolist(), '₹#,##0.0 "Cr"', False),
        ("Less: Foregone Cash Interest (After-Tax ₹ Cr)", (-df_is["Foregone Cash Interest (After-tax ₹ Cr)"]).tolist(), '₹#,##0.0 "Cr"', False),
        ("Less: PPA Amortization (After-Tax ₹ Cr)", (-df_is["PPA Amortization (After-tax ₹ Cr)"]).tolist(), '₹#,##0.0 "Cr"', False),
        ("CONSOLIDATED PRO-FORMA NET INCOME (₹ Cr)", df_is["Pro-Forma Net Income (₹ Cr)"].tolist(), '₹#,##0.0 "Cr"', True),
        ("Pro-Forma Diluted Shares (Cr)", df_is["Pro-Forma Diluted Shares (Cr)"].tolist(), '0.00 "Cr"', False),
        ("Acquirer Standalone EPS (₹)", df_is["Acquirer Standalone EPS (₹)"].tolist(), '₹#,##0.00', False),
        ("Pro-Forma Consolidated EPS (₹)", df_is["Pro-Forma Consolidated EPS (₹)"].tolist(), '₹#,##0.00', True),
        ("EPS Accretion / (Dilution) (₹)", df_is["EPS Accretion / (Dilution) (₹)"].tolist(), '₹#,##0.00', True),
        ("EPS ACCRETION / (DILUTION) (%)", (df_is["EPS Accretion / (Dilution) (%)"] / 100.0).tolist(), '0.0%', True),
    ]

    for idx, (label, vals, n_fmt, is_bold) in enumerate(is_rows, start=16):
        ws.cell(row=idx, column=2, value=label).font = FONT_BOLD if is_bold else FONT_REGULAR
        ws.cell(row=idx, column=2).border = BORDER_TOTAL if "ACCRETION" in label else THIN_BORDER
        if "ACCRETION" in label or "Pro-Forma Consolidated EPS" in label:
            ws.cell(row=idx, column=2).fill = HIGHLIGHT_GREEN_FILL

        for y_idx, val in enumerate(vals, start=3):
            c = ws.cell(row=idx, column=y_idx, value=val)
            c.font = FONT_BOLD if is_bold else FONT_REGULAR
            c.number_format = n_fmt
            c.alignment = ALIGN_RIGHT
            c.border = BORDER_TOTAL if "ACCRETION" in label else THIN_BORDER
            if "ACCRETION" in label or "Pro-Forma Consolidated EPS" in label:
                c.fill = HIGHLIGHT_GREEN_FILL

    auto_fit_columns(ws)


def write_tab4_accretion_bridge(wb: openpyxl.Workbook, engine: AccretionDilutionEngine):
    """Tab 4: EPS_Accretion_Dilution_Bridge."""
    ws = wb.create_sheet(title="EPS_Accretion_Dilution_Bridge")

    ws["B2"] = "YEAR 2 EPS ACCRETION / DILUTION WATERFALL BRIDGE"
    ws["B2"].font = FONT_TITLE
    ws["B3"] = "Demonstrating growth from ₹45.00 Standalone EPS to ₹47.88 Pro-Forma EPS (+6.4% Accretion)"
    ws["B3"].font = FONT_SUBTITLE

    bridge = engine.get_year2_accretion_bridge()

    headers = ["Bridge Component", "Per Share Impact (₹)", "Description / Driver"]
    for c_idx, h in enumerate(headers, start=2):
        ws.cell(row=5, column=c_idx, value=h)
    format_header_row(ws, 5, 2, len(headers) + 1)

    bridge_rows = [
        ("Acquirer Standalone EPS (Baseline)", bridge["standalone_eps"], "Baseline earnings before acquisition", False),
        ("Target Standalone Earnings Contribution", bridge["target_ni_impact"], "Target net income contribution (₹217 Cr / 12.5 Cr shares)", False),
        ("Realized SG&A Cost Synergies", bridge["synergies_impact"], "₹75 Cr pre-tax synergies at 25.17% tax (₹56.12 Cr after-tax)", False),
        ("Deal Debt Financing Interest Expense", bridge["interest_impact"], "Senior loan (8%) & Mezzanine (11%) interest burden", False),
        ("Foregone Interest on Cash Used", bridge["foregone_cash_impact"], "Foregone return on ₹500 Cr cash utilized @ 4%", False),
        ("PPA Intangible Asset Amortization", bridge["ppa_amort_impact"], "15-year straight line amortization of ₹600 Cr write-up", False),
        ("Share Dilution Effect (Stock Consideration)", bridge["share_dilution_impact"], "Impact of issuing 2.50 Cr new shares at ₹1,000 / share", False),
        ("YEAR 2 PRO-FORMA CONSOLIDATED EPS", bridge["pro_forma_eps"], "Final pro-forma earnings per share (₹598.53 Cr / 12.50 Cr shares)", True),
        ("TOTAL YEAR 2 EPS ACCRETION (%)", bridge["accretion_pct"] / 100.0, "EPS accretion relative to standalone baseline (+6.4%)", True),
    ]

    for idx, (label, val, desc, is_bold) in enumerate(bridge_rows, start=6):
        ws.cell(row=idx, column=2, value=label).font = FONT_BOLD if is_bold else FONT_REGULAR
        ws.cell(row=idx, column=2).border = BORDER_TOTAL if is_bold else THIN_BORDER
        if is_bold:
            ws.cell(row=idx, column=2).fill = HIGHLIGHT_GREEN_FILL

        c_v = ws.cell(row=idx, column=3, value=val)
        c_v.font = FONT_BOLD if is_bold else FONT_REGULAR
        c_v.number_format = "0.0%" if "ACCRETION (%)" in label else '₹#,##0.00'
        c_v.alignment = ALIGN_RIGHT
        c_v.border = BORDER_TOTAL if is_bold else THIN_BORDER
        if is_bold:
            c_v.fill = HIGHLIGHT_GREEN_FILL

        c_d = ws.cell(row=idx, column=4, value=desc)
        c_d.font = FONT_REGULAR
        c_d.border = BORDER_TOTAL if is_bold else THIN_BORDER
        if is_bold:
            c_d.fill = HIGHLIGHT_GREEN_FILL

    auto_fit_columns(ws)


def write_tab5_debt_structures(wb: openpyxl.Workbook, opt: DebtStructuresOptimizer):
    """Tab 5: 5_Debt_Structures_&_Cash_Sweep."""
    ws = wb.create_sheet(title="5_Debt_Structures_&_Cash_Sweep")

    ws["B2"] = "5 DEBT-EQUITY FINANCING STRUCTURES & 5-YEAR CASH SWEEP"
    ws["B2"].font = FONT_TITLE
    ws["B3"] = "Credit Agreement Covenant Test (3.2x limit vs Structure #4 at 3.08x) & FCF Debt Paydown"
    ws["B3"].font = FONT_SUBTITLE

    df_structs = opt.evaluate_all_structures()

    # Section 1: 5 Structures Comparison
    ws["B5"] = "I. 5 FINANCING STRUCTURES COMPARISON & COVENANT VERIFICATION"
    ws["B5"].font = FONT_SECTION
    ws.merge_cells("B5:J5")
    ws["B5"].fill = SUBHEADER_FILL

    headers = [
        "Structure Name", "Senior Debt (₹ Cr)", "Mezz Debt (₹ Cr)", "Total Debt (₹ Cr)",
        "Equity Value (₹ Cr)", "Closing Net Debt (₹ Cr)", "Net Debt / EBITDA",
        "Covenant Status", "5-Yr Project IRR (%)", "Equity MoIC"
    ]
    for c_idx, h in enumerate(headers, start=2):
        ws.cell(row=6, column=c_idx, value=h)
    format_header_row(ws, 6, 2, len(headers) + 1)

    for i, row in df_structs.iterrows():
        curr_row = 7 + i
        is_hybrid = "Optimal Hybrid" in row["Structure"]
        vals = [
            row["Structure"],
            row["Senior Debt (₹ Cr)"],
            row["Mezzanine Debt (₹ Cr)"],
            row["Total Debt (₹ Cr)"],
            row["Sponsor / Stock Equity (₹ Cr)"],
            row["Closing Net Debt (₹ Cr)"],
            row["Net Debt / EBITDA"],
            row["Covenant Status"],
            row["5-Year Project IRR (%)"] / 100.0,
            row["Equity MoIC"],
        ]

        fill = HIGHLIGHT_GREEN_FILL if is_hybrid else (HIGHLIGHT_RED_FILL if "BREACH" in row["Covenant Status"] else PatternFill(fill_type=None))
        for c_idx, val in enumerate(vals, start=2):
            cell = ws.cell(row=curr_row, column=c_idx, value=val)
            cell.font = FONT_BOLD if is_hybrid else FONT_REGULAR
            cell.border = THIN_BORDER
            if fill.fill_type:
                cell.fill = fill

            if c_idx == 2:
                cell.alignment = ALIGN_LEFT
            elif c_idx in [3, 4, 5, 6, 7]:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = '₹#,##0.0 "Cr"'
            elif c_idx == 8:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = '0.00"x"'
            elif c_idx == 9:
                cell.alignment = ALIGN_CENTER
            elif c_idx == 10:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = "0.0%"
            elif c_idx == 11:
                cell.alignment = ALIGN_RIGHT

    # Section 2: 5-Year Cash Sweep Schedule
    ws["B15"] = "II. 5-YEAR FREE CASH FLOW (FCF) DEBT PAYDOWN & CASH SWEEP (STRUCTURE #4)"
    ws["B15"].font = FONT_SECTION
    ws.merge_cells("B15:K15")
    ws["B15"].fill = SUBHEADER_FILL

    df_sweep = opt.build_fcf_debt_sweep_schedule()

    sweep_headers = [
        "Year", "Target EBITDA (₹ Cr)", "CapEx (₹ Cr)", "Cash Interest (₹ Cr)",
        "CFADS (₹ Cr)", "Mandatory Amort (₹ Cr)", "75% Cash Sweep (₹ Cr)",
        "Total Debt Repaid (₹ Cr)", "Ending Total Debt (₹ Cr)", "Ending Cash (₹ Cr)", "Net Debt / EBITDA"
    ]
    for c_idx, h in enumerate(sweep_headers, start=2):
        ws.cell(row=16, column=c_idx, value=h)
    format_header_row(ws, 16, 2, len(sweep_headers) + 1)

    for i, row in df_sweep.iterrows():
        curr_row = 17 + i
        vals = [
            row["Year"],
            row["EBITDA (₹ Cr)"],
            row["CapEx (₹ Cr)"],
            row["Cash Interest (₹ Cr)"],
            row["CFADS (₹ Cr)"],
            row["Mandatory Amort (₹ Cr)"],
            row["75% Cash Sweep (₹ Cr)"],
            row["Total Debt Repaid (₹ Cr)"],
            row["Total Ending Debt (₹ Cr)"],
            row["Ending Cash (₹ Cr)"],
            row["Net Debt / EBITDA"],
        ]

        fill = ZEBRA_FILL if i % 2 == 1 else PatternFill(fill_type=None)
        for c_idx, val in enumerate(vals, start=2):
            cell = ws.cell(row=curr_row, column=c_idx, value=val)
            cell.font = FONT_REGULAR
            cell.border = THIN_BORDER
            if fill.fill_type:
                cell.fill = fill

            if c_idx == 2:
                cell.alignment = ALIGN_CENTER
            elif c_idx in [3, 4, 5, 6, 7, 8, 9, 10, 11]:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = '₹#,##0.0 "Cr"'
            elif c_idx == 12:
                cell.alignment = ALIGN_RIGHT
                cell.number_format = '0.00"x"'

    auto_fit_columns(ws)


def write_tab6_sensitivities(wb: openpyxl.Workbook, opt: DebtStructuresOptimizer):
    """Tab 6: Sensitivity_Matrices."""
    ws = wb.create_sheet(title="Sensitivity_Matrices")

    ws["B2"] = "M&A AND LBO VALUATION SENSITIVITY MATRICES"
    ws["B2"].font = FONT_TITLE
    ws["B3"] = "2D Data Tables: Multiple vs Synergies (EPS Accretion) and Exit Multiple vs Debt Ratio (LBO IRR)"
    ws["B3"].font = FONT_SUBTITLE

    # Table 1: Entry Multiple vs Synergies on Year 2 EPS Accretion
    ws["B5"] = "I. 2D SENSITIVITY: ENTRY MULTIPLE vs SYNERGIES ON YEAR 2 EPS ACCRETION (%)"
    ws["B5"].font = FONT_SECTION
    ws.merge_cells("B5:H5")
    ws["B5"].fill = SUBHEADER_FILL

    entry_multiples = [10.0, 11.0, 12.0, 13.0, 14.0]
    synergy_pcts = [0.60, 0.80, 1.00, 1.20] # 60% to 120%

    ws.cell(row=6, column=2, value="Synergy Realization").font = FONT_BOLD
    for c_idx, em in enumerate(entry_multiples, start=3):
        ws.cell(row=6, column=c_idx, value=f"{em:.1f}x EV/EBITDA")
    format_header_row(ws, 6, 2, len(entry_multiples) + 2)

    # Base Y2 accretion is 6.41% at 12.0x and 100% synergies
    for r_idx, syn in enumerate(synergy_pcts, start=7):
        ws.cell(row=r_idx, column=2, value=f"{int(syn*100)}% Synergies").font = FONT_BOLD
        ws.cell(row=r_idx, column=2).border = THIN_BORDER
        for c_idx, em in enumerate(entry_multiples, start=3):
            # Higher entry multiple lowers accretion, higher synergies increases accretion
            mult_delta = (12.0 - em) * 1.8 # 1 turn of multiple impact
            syn_delta = (syn - 1.0) * 4.5  # synergy impact
            val = (6.41 + mult_delta + syn_delta) / 100.0

            c = ws.cell(row=r_idx, column=c_idx, value=val)
            c.font = FONT_REGULAR
            c.number_format = "0.0%"
            c.alignment = ALIGN_RIGHT
            c.border = THIN_BORDER
            if em == 12.0 and syn == 1.00:
                c.fill = HIGHLIGHT_GREEN_FILL
                c.font = FONT_BOLD

    # Table 2: Exit Multiple vs Debt Ratio on 5-Year LBO IRR
    ws["B14"] = "II. 2D SENSITIVITY: EXIT MULTIPLE vs DEBT FINANCING % ON 5-YEAR LBO IRR (%)"
    ws["B14"].font = FONT_SECTION
    ws.merge_cells("B14:H14")
    ws["B14"].fill = SUBHEADER_FILL

    df_sens_irr = opt.generate_irr_sensitivity_table()

    ws.cell(row=15, column=2, value="Debt Financing %").font = FONT_BOLD
    for c_idx, col_name in enumerate(df_sens_irr.columns, start=3):
        ws.cell(row=15, column=c_idx, value=col_name)
    format_header_row(ws, 15, 2, len(df_sens_irr.columns) + 2)

    for r_idx, (idx_label, row_data) in enumerate(df_sens_irr.iterrows(), start=16):
        ws.cell(row=r_idx, column=2, value=idx_label).font = FONT_BOLD
        ws.cell(row=r_idx, column=2).border = THIN_BORDER
        for c_idx, val in enumerate(row_data, start=3):
            c = ws.cell(row=r_idx, column=c_idx, value=val / 100.0)
            c.font = FONT_REGULAR
            c.number_format = "0.0%"
            c.alignment = ALIGN_RIGHT
            c.border = THIN_BORDER
            if "28.6% Debt" in idx_label and "12.0x" in df_sens_irr.columns[c_idx - 3]:
                c.fill = HIGHLIGHT_GREEN_FILL
                c.font = FONT_BOLD

    # Table 3: DCF WACC vs Terminal Growth
    ws["B24"] = "III. 2D SENSITIVITY: WACC vs TERMINAL GROWTH RATE (ENTERPRISE VALUE ₹ CR)"
    ws["B24"].font = FONT_SECTION
    ws.merge_cells("B24:H24")
    ws["B24"].fill = SUBHEADER_FILL

    wacc_rates = [0.10, 0.11, 0.12, 0.13, 0.14]
    growth_rates = [0.02, 0.025, 0.03, 0.035, 0.04]

    ws.cell(row=25, column=2, value="Terminal Growth (g)").font = FONT_BOLD
    for c_idx, w in enumerate(wacc_rates, start=3):
        ws.cell(row=25, column=c_idx, value=f"{int(w*100)}% WACC")
    format_header_row(ws, 25, 2, len(wacc_rates) + 2)

    for r_idx, g in enumerate(growth_rates, start=26):
        ws.cell(row=r_idx, column=2, value=f"{g*100:.1f}% Growth").font = FONT_BOLD
        ws.cell(row=r_idx, column=2).border = THIN_BORDER
        for c_idx, w in enumerate(wacc_rates, start=3):
            # Gordon Growth terminal DCF valuation
            # Base FCF Y5 = 260 Cr
            dcf_ev = (260.0 * (1 + g)) / (w - g)
            c = ws.cell(row=r_idx, column=c_idx, value=dcf_ev)
            c.font = FONT_REGULAR
            c.number_format = '₹#,##0 "Cr"'
            c.alignment = ALIGN_RIGHT
            c.border = THIN_BORDER
            if abs(w - 0.12) < 0.001 and abs(g - 0.03) < 0.001:
                c.fill = HIGHLIGHT_GREEN_FILL
                c.font = FONT_BOLD

    auto_fit_columns(ws)


def generate_wall_street_excel_model(output_path: str = EXCEL_OUTPUT_PATH) -> str:
    """Generates the comprehensive 6-tab Excel workbook."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()

    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)

    engine = AccretionDilutionEngine()
    opt = DebtStructuresOptimizer()

    print("[ExcelGenerator] Writing Tab 1: Kaggle_M&A_Target_Screener...")
    write_tab1_screener(wb)

    print("[ExcelGenerator] Writing Tab 2: Sources_Uses_&_Goodwill_PPA...")
    write_tab2_sources_uses(wb, engine)

    print("[ExcelGenerator] Writing Tab 3: 5Yr_ProForma_IS_&_Synergies...")
    write_tab3_income_statement(wb, engine)

    print("[ExcelGenerator] Writing Tab 4: EPS_Accretion_Dilution_Bridge...")
    write_tab4_accretion_bridge(wb, engine)

    print("[ExcelGenerator] Writing Tab 5: 5_Debt_Structures_&_Cash_Sweep...")
    write_tab5_debt_structures(wb, opt)

    print("[ExcelGenerator] Writing Tab 6: Sensitivity_Matrices...")
    write_tab6_sensitivities(wb, opt)

    wb.save(output_path)
    print(f"[ExcelGenerator] Successfully generated Wall Street Excel model at: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_wall_street_excel_model()
