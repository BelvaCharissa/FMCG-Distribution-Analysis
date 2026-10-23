-- =============================================================================
-- 03_analytical_queries.sql
-- Core Business Analytics Queries for FMCG Supply Chain & Distribution
-- =============================================================================

-- -----------------------------------------------------------------------------
-- QUERY 1: PARETO 80/20 ANALYSIS - OUTLET REVENUE & VOLUME CONTRIBUTION
-- Identifies key volume drivers across the distribution network
-- -----------------------------------------------------------------------------
WITH outlet_sales_agg AS (
    SELECT 
        o.outlet_id,
        o.outlet_name,
        o.outlet_type,
        o.region,
        COUNT(s.transaction_id) AS total_orders,
        SUM(s.sales_cartons) AS total_cartons_demanded,
        SUM(s.sales_value_idr) AS total_revenue_idr
    FROM outlets o
    JOIN sales s ON o.outlet_id = s.outlet_id
    GROUP BY o.outlet_id, o.outlet_name, o.outlet_type, o.region
),
ranked_outlets AS (
    SELECT 
        *,
        SUM(total_revenue_idr) OVER () AS network_total_revenue,
        SUM(total_revenue_idr) OVER (ORDER BY total_revenue_idr DESC) AS running_cumulative_revenue
    FROM outlet_sales_agg
)
SELECT 
    outlet_id,
    outlet_name,
    outlet_type,
    region,
    total_orders,
    total_cartons_demanded,
    total_revenue_idr,
    ROUND((total_revenue_idr / network_total_revenue) * 100, 3) AS revenue_share_pct,
    ROUND((running_cumulative_revenue / network_total_revenue) * 100, 2) AS cumulative_revenue_pct,
    CASE 
        WHEN (running_cumulative_revenue / network_total_revenue) <= 0.80 THEN 'Tier 1 - Top 80% Revenue (Core)'
        ELSE 'Tier 2 - Long Tail (20% Revenue)'
    END AS pareto_tier
FROM ranked_outlets
ORDER BY total_revenue_idr DESC
LIMIT 50;


-- -----------------------------------------------------------------------------
-- QUERY 2: REGIONAL LOGISTICS PERFORMANCE & ON-TIME DELIVERY (OTD %)
-- Evaluates SLA compliance and average delay minutes per Distribution Center
-- -----------------------------------------------------------------------------
SELECT 
    d.distribution_center_id,
    dc.dc_name,
    o.region,
    COUNT(d.delivery_id) AS total_deliveries,
    SUM(d.is_delayed) AS delayed_deliveries,
    ROUND((1.0 - (CAST(SUM(d.is_delayed) AS DECIMAL) / COUNT(d.delivery_id))) * 100, 2) AS on_time_delivery_rate_pct,
    ROUND(AVG(d.delay_minutes), 1) AS avg_delay_minutes,
    ROUND(AVG(d.delivery_distance_km), 2) AS avg_distance_km,
    SUM(d.cartons_delivered) AS total_cartons_dispatched
FROM deliveries d
JOIN distribution_centers dc ON d.distribution_center_id = dc.distribution_center_id
JOIN outlets o ON d.outlet_id = o.outlet_id
GROUP BY d.distribution_center_id, dc.dc_name, o.region
ORDER BY d.distribution_center_id, avg_delay_minutes DESC;


-- -----------------------------------------------------------------------------
-- QUERY 3: STOCKOUT RATE & LOST SALES ESTIMATION BY REGION & OUTLET TYPE
-- Identifies which channels and geography suffer the most severe product unavailability
-- -----------------------------------------------------------------------------
WITH stockout_metrics AS (
    SELECT 
        o.region,
        o.outlet_type,
        COUNT(inv.id) AS total_audits,
        SUM(inv.stockout_flag) AS stockout_count,
        ROUND((CAST(SUM(inv.stockout_flag) AS DECIMAL) / COUNT(inv.id)) * 100, 2) AS stockout_rate_pct,
        ROUND(AVG(CASE WHEN inv.stockout_flag = 1 THEN inv.stockout_duration_hours ELSE NULL END), 1) AS avg_stockout_duration_hours
    FROM inventory_stockouts inv
    JOIN outlets o ON inv.outlet_id = o.outlet_id
    GROUP BY o.region, o.outlet_type
)
SELECT 
    region,
    outlet_type,
    total_audits,
    stockout_count,
    stockout_rate_pct,
    COALESCE(avg_stockout_duration_hours, 0) AS avg_stockout_duration_hours,
    CASE 
        WHEN stockout_rate_pct >= 25.0 THEN 'High Stockout Risk (>25%)'
        WHEN stockout_rate_pct >= 15.0 THEN 'Moderate Stockout Risk (15-25%)'
        ELSE 'Healthy Inventory (<15%)'
    END AS risk_classification
FROM stockout_metrics
ORDER BY stockout_rate_pct DESC;


-- -----------------------------------------------------------------------------
-- QUERY 4: CRITICAL QUADRANT - HIGH DEMAND VS. HIGH STOCKOUT (URGENT ATTENTION)
-- Highlights outlets generating substantial revenue that suffer frequent stockouts
-- -----------------------------------------------------------------------------
WITH outlet_demand AS (
    SELECT 
        outlet_id,
        SUM(sales_value_idr) AS total_revenue_idr,
        SUM(sales_cartons) AS total_cartons
    FROM sales
    GROUP BY outlet_id
),
outlet_stockout AS (
    SELECT 
        outlet_id,
        COUNT(*) AS total_checks,
        SUM(stockout_flag) AS stockout_count,
        ROUND((CAST(SUM(stockout_flag) AS DECIMAL) / COUNT(*)) * 100, 2) AS stockout_rate_pct
    FROM inventory_stockouts
    GROUP BY outlet_id
),
outlet_delivery AS (
    SELECT 
        outlet_id,
        ROUND(AVG(delay_minutes), 1) AS avg_delay_mins,
        ROUND(AVG(delivery_distance_km), 2) AS avg_delivery_distance_km
    FROM deliveries
    GROUP BY outlet_id
)
SELECT 
    o.outlet_id,
    o.outlet_name,
    o.outlet_type,
    o.region,
    o.distribution_center_id,
    od.total_revenue_idr,
    od.total_cartons,
    os.stockout_rate_pct,
    dl.avg_delay_mins,
    dl.avg_delivery_distance_km,
    CASE 
        WHEN od.total_revenue_idr >= 100000000 AND os.stockout_rate_pct >= 25.0 
            THEN 'Priority 1: High Revenue + High Stockout (Revenue Leak)'
        WHEN od.total_revenue_idr < 100000000 AND os.stockout_rate_pct >= 25.0 
            THEN 'Priority 2: Low Revenue + High Stockout (Service Inefficiency)'
        WHEN od.total_revenue_idr >= 100000000 AND os.stockout_rate_pct < 25.0 
            THEN 'Priority 3: High Revenue + Stable Stock (Sustain / Protect)'
        ELSE 'Priority 4: Low Revenue + Stable Stock'
    END AS strategic_segment
FROM outlets o
JOIN outlet_demand od ON o.outlet_id = od.outlet_id
JOIN outlet_stockout os ON o.outlet_id = os.outlet_id
JOIN outlet_delivery dl ON o.outlet_id = dl.outlet_id
ORDER BY od.total_revenue_idr DESC, os.stockout_rate_pct DESC
LIMIT 50;
