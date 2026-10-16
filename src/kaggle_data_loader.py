"""
Kaggle NYSE Fundamentals Data Loader & Database Ingestion Engine
================================================================
Handles automated downloading, cleaning of the 79 financial statement columns,
SQLite database ingestion, and analytical metric calculations for the M&A Screener.
Dataset: dgawlik/nyse (New York Stock Exchange Fundamentals & Securities)
"""

import os
import re
import shutil
import sqlite3
import zipfile
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "kaggle_ma_universe.db")
FUNDAMENTALS_CSV = os.path.join(DATA_DIR, "fundamentals.csv")
SECURITIES_CSV = os.path.join(DATA_DIR, "securities.csv")


def ensure_data_available() -> Tuple[str, str]:
    """
    Ensures fundamentals.csv and securities.csv exist in the data/ directory.
    Uses multi-stage fallback:
    1. Existing CSVs in data/
    2. Local workspace archive (3).zip extraction
    3. kagglehub download (dgawlik/nyse)
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    # Check if files already present
    if os.path.exists(FUNDAMENTALS_CSV) and os.path.exists(SECURITIES_CSV):
        return FUNDAMENTALS_CSV, SECURITIES_CSV

    # Fallback 1: Extract from archive (3).zip in workspace
    archive_paths = [
        os.path.join(WORKSPACE_DIR, "archive (3).zip"),
        os.path.join(WORKSPACE_DIR, "archive.zip"),
    ]
    for archive_path in archive_paths:
        if os.path.exists(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "r") as z:
                    for filename in ["fundamentals.csv", "securities.csv"]:
                        if filename in z.namelist():
                            z.extract(filename, DATA_DIR)
                if os.path.exists(FUNDAMENTALS_CSV) and os.path.exists(SECURITIES_CSV):
                    print(f"[DataLoader] Successfully extracted dataset from {archive_path}")
                    return FUNDAMENTALS_CSV, SECURITIES_CSV
            except Exception as e:
                print(f"[DataLoader] Warning: Failed to extract from {archive_path}: {e}")

    # Fallback 2: kagglehub dataset download
    try:
        import kagglehub
        print("[DataLoader] Attempting download via kagglehub ('dgawlik/nyse')...")
        download_path = kagglehub.dataset_download("dgawlik/nyse")
        for fname in ["fundamentals.csv", "securities.csv"]:
            src_file = os.path.join(download_path, fname)
            dst_file = os.path.join(DATA_DIR, fname)
            if os.path.exists(src_file):
                shutil.copy2(src_file, dst_file)
        if os.path.exists(FUNDAMENTALS_CSV) and os.path.exists(SECURITIES_CSV):
            print(f"[DataLoader] Successfully downloaded via kagglehub to {DATA_DIR}")
            return FUNDAMENTALS_CSV, SECURITIES_CSV
    except Exception as e:
        print(f"[DataLoader] Notice: kagglehub download unavailable or not required: {e}")

    if not os.path.exists(FUNDAMENTALS_CSV) or not os.path.exists(SECURITIES_CSV):
        raise FileNotFoundError(
            "Could not locate or download fundamentals.csv and securities.csv. "
            "Please ensure data/fundamentals.csv and data/securities.csv exist."
        )

    return FUNDAMENTALS_CSV, SECURITIES_CSV


def to_clean_identifier(col_name: str) -> str:
    """Converts raw Kaggle column name to unique snake_case SQL identifier."""
    c = col_name.strip().lower()
    c = re.sub(r"[^a-z0-9]+", "_", c).strip("_")
    return c


def clean_fundamentals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans all 79 financial statement columns:
    - Normalizes column names to unique snake_case
    - Fills missing values with zero or derived accounting values
    - Handles EPS and Share count reconciliation
    - Calculates standardized metrics: EBITDA, Net Debt, Margins, FCF, FCF conversion
    """
    df = df.copy()

    # Drop unnamed index column if present
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    ticker_col = "Ticker Symbol"
    period_col = "Period Ending"
    if ticker_col not in df.columns or period_col not in df.columns:
        raise ValueError("Fundamentals dataset missing Ticker Symbol or Period Ending")

    # Clean ticker and dates
    df["Ticker Symbol"] = df["Ticker Symbol"].astype(str).str.strip().str.upper()
    df["Period Ending"] = pd.to_datetime(df["Period Ending"], errors="coerce")
    df = df.dropna(subset=["Ticker Symbol", "Period Ending"])

    # Identify numerical columns (all except Ticker and Period)
    num_cols = [c for c in df.columns if c not in ["Ticker Symbol", "Period Ending"]]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    # Reconcile Shares & EPS where one was missing
    if "Earnings Per Share" in df.columns and "Estimated Shares Outstanding" in df.columns:
        mask_shares_missing = (df["Estimated Shares Outstanding"] == 0) & (df["Earnings Per Share"] != 0)
        df.loc[mask_shares_missing, "Estimated Shares Outstanding"] = (
            df.loc[mask_shares_missing, "Net Income"] / df.loc[mask_shares_missing, "Earnings Per Share"]
        ).abs()

        mask_eps_missing = (df["Earnings Per Share"] == 0) & (df["Estimated Shares Outstanding"] != 0)
        df.loc[mask_eps_missing, "Earnings Per Share"] = (
            df.loc[mask_eps_missing, "Net Income"] / df.loc[mask_eps_missing, "Estimated Shares Outstanding"]
        )

    # Calculate key metrics before renaming
    rev = df["Total Revenue"]
    ebit_val = df["Earnings Before Interest and Tax"]
    depr_val = df["Depreciation"]
    ebitda_val = ebit_val + depr_val
    ni_val = df["Net Income"]
    sga_val = df["Sales, General and Admin."]
    lt_debt = df["Long-Term Debt"]
    st_debt = df["Short-Term Debt / Current Portion of Long-Term Debt"]
    tot_debt = lt_debt + st_debt
    cash_val = df["Cash and Cash Equivalents"]
    net_debt_val = tot_debt - cash_val
    tot_assets = df["Total Assets"]
    tot_liab = df["Total Liabilities"]
    capex_abs = df["Capital Expenditures"].abs()
    ocf_val = df["Net Cash Flow-Operating"]
    fcf_val = ocf_val - capex_abs
    eps_val = df["Earnings Per Share"]
    shares_val = df["Estimated Shares Outstanding"]

    # Ratios
    rev_safe = np.where(rev > 0, rev, np.nan)
    ebitda_safe = np.where(ebitda_val.abs() > 0, ebitda_val, np.nan)
    ebitda_margin_val = np.where(np.isnan(rev_safe), 0.0, ebitda_val / rev_safe)
    sga_margin_val = np.where(np.isnan(rev_safe), 0.0, sga_val / rev_safe)
    net_debt_ebitda_val = np.where(np.isnan(ebitda_safe), 0.0, net_debt_val / ebitda_safe)
    fcf_conv_val = np.where(np.isnan(ebitda_safe), 0.0, fcf_val / ebitda_safe)

    # Rename original columns to clean snake_case
    col_rename = {}
    for col in df.columns:
        c_clean = to_clean_identifier(col)
        # Avoid conflict with derived names
        col_rename[col] = f"raw_{c_clean}" if c_clean in [
            "ebitda", "net_debt", "free_cash_flow", "ebitda_margin", "sga_margin", "net_debt_ebitda", "fcf_conversion"
        ] else c_clean

    df = df.rename(columns=col_rename)

    # Assign standardized columns
    df["ticker"] = df["ticker_symbol"]
    df["period_ending"] = df["period_ending"].dt.strftime("%Y-%m-%d")
    df["revenue"] = rev
    df["ebit"] = ebit_val
    df["depreciation"] = depr_val
    df["ebitda"] = ebitda_val
    df["net_income"] = ni_val
    df["sga"] = sga_val
    df["long_term_debt"] = lt_debt
    df["short_term_debt"] = st_debt
    df["total_debt"] = tot_debt
    df["cash"] = cash_val
    df["net_debt"] = net_debt_val
    df["total_assets"] = tot_assets
    df["total_liabilities"] = tot_liab
    df["capex"] = capex_abs
    df["operating_cash_flow"] = ocf_val
    df["free_cash_flow"] = fcf_val
    df["eps"] = eps_val
    df["shares_outstanding"] = shares_val
    df["ebitda_margin"] = ebitda_margin_val
    df["sga_margin"] = sga_margin_val
    df["net_debt_ebitda"] = net_debt_ebitda_val
    df["fcf_conversion"] = fcf_conv_val

    # Ensure no duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    return df


def clean_securities(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans securities.csv metadata table."""
    df = df.copy()
    col_mapping = {
        "Ticker symbol": "ticker",
        "Security": "security_name",
        "SEC filings": "sec_filings",
        "GICS Sector": "gics_sector",
        "GICS Sub Industry": "gics_sub_industry",
        "Address of Headquarters": "headquarters",
        "Date first added": "date_added",
        "CIK": "cik",
    }
    df = df.rename(columns=col_mapping)
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    return df


def init_sqlite_database(fund_df: pd.DataFrame, sec_df: pd.DataFrame, db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Creates and populates the SQLite database with:
    - fundamentals: full 79 cleaned columns + standard analytical metrics
    - securities: company descriptive metadata
    - v_latest_financials: SQL view containing latest fiscal year per company joined with metadata
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Drop existing tables/views if rebuilding
    cur.execute("DROP VIEW IF EXISTS v_latest_financials")
    cur.execute("DROP TABLE IF EXISTS fundamentals")
    cur.execute("DROP TABLE IF EXISTS securities")

    # Store DataFrames
    fund_df.to_sql("fundamentals", conn, if_exists="replace", index=False)
    sec_df.to_sql("securities", conn, if_exists="replace", index=False)

    # Create Indexes for fast querying
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fund_ticker ON fundamentals (ticker)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fund_period ON fundamentals (period_ending)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sec_ticker ON securities (ticker)")

    # Create View for Latest Fiscal Year Financials
    create_view_sql = """
    CREATE VIEW v_latest_financials AS
    WITH ranked_periods AS (
        SELECT 
            f.*,
            ROW_NUMBER() OVER (
                PARTITION BY f.ticker 
                ORDER BY f.period_ending DESC
            ) as period_rank
        FROM fundamentals f
    )
    SELECT 
        r.ticker,
        s.security_name,
        s.gics_sector,
        s.gics_sub_industry,
        s.headquarters,
        r.period_ending AS latest_period,
        r.revenue,
        r.ebit,
        r.depreciation,
        r.ebitda,
        r.net_income,
        r.sga,
        r.long_term_debt,
        r.short_term_debt,
        r.total_debt,
        r.cash,
        r.net_debt,
        r.total_assets,
        r.total_liabilities,
        r.capex,
        r.operating_cash_flow,
        r.free_cash_flow,
        r.eps,
        r.shares_outstanding,
        r.ebitda_margin,
        r.sga_margin,
        r.net_debt_ebitda,
        r.fcf_conversion
    FROM ranked_periods r
    LEFT JOIN securities s ON r.ticker = s.ticker
    WHERE r.period_rank = 1;
    """
    cur.execute(create_view_sql)
    conn.commit()
    print(f"[DataLoader] Successfully initialized SQLite database at {db_path}")
    return conn


def load_kaggle_universe() -> sqlite3.Connection:
    """Main entry point to guarantee data availability and database state."""
    fund_path, sec_path = ensure_data_available()
    print(f"[DataLoader] Loading raw fundamentals from {fund_path}...")
    raw_fund = pd.read_csv(fund_path)
    raw_sec = pd.read_csv(sec_path)

    clean_fund = clean_fundamentals(raw_fund)
    clean_sec = clean_securities(raw_sec)

    conn = init_sqlite_database(clean_fund, clean_sec, DB_PATH)
    return conn


def get_db_connection() -> sqlite3.Connection:
    """Returns an active SQLite connection, building DB if necessary."""
    if not os.path.exists(DB_PATH):
        return load_kaggle_universe()
    conn = sqlite3.connect(DB_PATH)
    return conn


def get_all_tickers() -> List[Dict[str, str]]:
    """Returns sorted list of all available tickers with security name and sector."""
    conn = get_db_connection()
    query = """
    SELECT ticker, security_name, gics_sector, gics_sub_industry 
    FROM v_latest_financials 
    WHERE revenue > 0
    ORDER BY ticker ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict(orient="records")


def get_company_profile(ticker: str) -> Optional[Dict]:
    """Retrieves full company profile and latest financial metrics for a ticker."""
    conn = get_db_connection()
    query = "SELECT * FROM v_latest_financials WHERE ticker = ?"
    df = pd.read_sql_query(query, conn, params=(ticker.upper(),))
    conn.close()
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def get_company_history(ticker: str) -> pd.DataFrame:
    """Retrieves historical financial statements for a given ticker."""
    conn = get_db_connection()
    query = """
    SELECT 
        period_ending as period,
        revenue, ebit, depreciation, ebitda, net_income, sga, 
        total_debt, cash, net_debt, free_cash_flow, eps
    FROM fundamentals 
    WHERE ticker = ?
    ORDER BY period_ending ASC
    """
    df = pd.read_sql_query(query, conn, params=(ticker.upper(),))
    conn.close()
    return df


def execute_screener_sql(sql_file_path: Optional[str] = None) -> pd.DataFrame:
    """Executes sql/target_screener.sql against SQLite database."""
    if sql_file_path is None:
        sql_file_path = os.path.join(WORKSPACE_DIR, "sql", "target_screener.sql")
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = get_db_connection()
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


if __name__ == "__main__":
    conn = load_kaggle_universe()
    tickers = get_all_tickers()
    print(f"Loaded universe with {len(tickers)} companies.")
    sample = get_company_profile("ADBE")
    print("Sample profile for ADBE (Adobe):", sample.get("security_name"), "Revenue:", sample.get("revenue"))
    screened_df = execute_screener_sql()
    print(f"Top Screened M&A Targets ({len(screened_df)} rows):")
    print(screened_df[["screener_rank", "ticker", "company_name", "sector", "ebitda_margin_pct", "sga_to_revenue_pct", "net_debt_to_ebitda", "fcf_conversion_pct"]].head(10))
