-- ==============================================================================
-- INSTITUTIONAL M&A TARGET SCREENING QUERY
-- Dataset: Kaggle NYSE Fundamentals (dgawlik/nyse)
-- Database: SQLite (data/kaggle_ma_universe.db)
-- Methodology: Multi-CTE Architecture with Window Functions
-- Screening Criteria:
--   1. EBITDA Margin > 15.0% (Operational Profitability)
--   2. SG&A-to-Revenue > 15.0% (Significant Cost Synergy / Overhead Rationalization Potential)
--   3. Free Cash Flow Conversion > 40.0% (De-risked Debt Service & Cash Sweep Capacity)
--   4. Net Debt / EBITDA < 2.50x (Prudent Leverage Profile for Levered Acquisitions)
-- ==============================================================================

WITH latest_fiscal_periods AS (
    -- Extract the most recent fiscal period per company using Window Functions
    SELECT 
        f.ticker,
        f.period_ending,
        f.revenue,
        f.ebit,
        f.depreciation,
        f.ebitda,
        f.net_income,
        f.sga,
        f.total_debt,
        f.cash,
        f.net_debt,
        f.free_cash_flow,
        f.capex,
        f.operating_cash_flow,
        f.shares_outstanding,
        f.eps,
        ROW_NUMBER() OVER (
            PARTITION BY f.ticker 
            ORDER BY f.period_ending DESC
        ) AS period_rank
    FROM fundamentals f
    WHERE f.revenue > 0 AND f.ebitda > 0
),

target_metrics_normalized AS (
    -- Join security metadata and calculate institutional financial ratios
    SELECT 
        lp.ticker,
        s.security_name,
        s.gics_sector,
        s.gics_sub_industry,
        s.headquarters,
        lp.period_ending,
        lp.revenue,
        lp.ebitda,
        lp.sga,
        lp.net_income,
        lp.net_debt,
        lp.free_cash_flow,
        ROUND((lp.ebitda * 1.0 / lp.revenue) * 100, 2) AS ebitda_margin_pct,
        ROUND((lp.sga * 1.0 / lp.revenue) * 100, 2) AS sga_to_revenue_pct,
        ROUND((lp.net_debt * 1.0 / lp.ebitda), 2) AS net_debt_to_ebitda,
        ROUND((lp.free_cash_flow * 1.0 / lp.ebitda) * 100, 2) AS fcf_conversion_pct
    FROM latest_fiscal_periods lp
    LEFT JOIN securities s ON lp.ticker = s.ticker
    WHERE lp.period_rank = 1
),

screened_acquisition_targets AS (
    -- Apply strict institutional M&A screening hurdles
    SELECT 
        ticker,
        security_name,
        gics_sector,
        gics_sub_industry,
        headquarters,
        period_ending,
        revenue,
        ebitda,
        sga,
        net_income,
        net_debt,
        free_cash_flow,
        ebitda_margin_pct,
        sga_to_revenue_pct,
        net_debt_to_ebitda,
        fcf_conversion_pct,
        -- Synergy Opportunity Score: Combines SG&A cost-cutting upside with FCF cash generation
        ROUND(
            (sga_to_revenue_pct * 0.40) + 
            (ebitda_margin_pct * 0.35) + 
            (fcf_conversion_pct * 0.25) - 
            (CASE WHEN net_debt_to_ebitda > 0 THEN net_debt_to_ebitda * 3.0 ELSE 0 END),
            2
        ) AS synergy_opportunity_score
    FROM target_metrics_normalized
    WHERE 
        ebitda_margin_pct >= 15.00            -- Healthy core margins (>15%)
        AND sga_to_revenue_pct >= 15.00        -- Overhead rationalization runway (>15%)
        AND fcf_conversion_pct >= 40.00        -- Strong FCF conversion for debt paydown (>40%)
        AND net_debt_to_ebitda <= 2.50         -- Manageable existing leverage (<2.5x)
        AND net_debt_to_ebitda >= -3.00        -- Filter out extreme cash-heavy anomalies
        AND revenue >= 500000000               -- Enterprise scale (> $500M revenue)
),

ranked_ma_universe AS (
    -- Rank screened companies across sectors
    SELECT 
        DENSE_RANK() OVER (ORDER BY synergy_opportunity_score DESC) as screener_rank,
        ticker,
        security_name,
        gics_sector,
        gics_sub_industry,
        period_ending,
        revenue,
        ebitda,
        sga,
        net_debt,
        free_cash_flow,
        ebitda_margin_pct,
        sga_to_revenue_pct,
        fcf_conversion_pct,
        net_debt_to_ebitda,
        synergy_opportunity_score
    FROM screened_acquisition_targets
)

-- Output Top 25 Institutional Targets
SELECT 
    screener_rank,
    ticker,
    COALESCE(security_name, ticker) AS company_name,
    COALESCE(gics_sector, 'Technology') AS sector,
    revenue AS ltm_revenue,
    ebitda AS ltm_ebitda,
    sga AS ltm_sga,
    ebitda_margin_pct,
    sga_to_revenue_pct,
    fcf_conversion_pct,
    net_debt_to_ebitda,
    synergy_opportunity_score
FROM ranked_ma_universe
ORDER BY screener_rank ASC
LIMIT 25;
