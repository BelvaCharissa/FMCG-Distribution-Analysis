-- =============================================================================
-- 01_schema.sql
-- FMCG Geospatial Supply Chain & Distribution Optimization
-- Relational Database Schema (ANSI SQL / PostgreSQL / SQLite / MySQL compatible)
-- =============================================================================

-- 1. Distribution Centers Master
DROP TABLE IF EXISTS distribution_centers CASCADE;
CREATE TABLE distribution_centers (
    distribution_center_id VARCHAR(20) PRIMARY KEY,
    dc_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    daily_capacity_cartons INTEGER NOT NULL,
    fleet_size INTEGER NOT NULL
);

-- 2. Outlets Master
DROP TABLE IF EXISTS outlets CASCADE;
CREATE TABLE outlets (
    outlet_id VARCHAR(20) PRIMARY KEY,
    outlet_name VARCHAR(150) NOT NULL,
    outlet_type VARCHAR(50) NOT NULL, -- 'Warung Kelontong', 'Minimarket', 'Supermarket', 'Wholesaler'
    region VARCHAR(50) NOT NULL,
    sub_district VARCHAR(100),
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    distribution_center_id VARCHAR(20) REFERENCES distribution_centers(distribution_center_id),
    store_size_sqm INTEGER,
    status VARCHAR(20) DEFAULT 'Active'
);

-- 3. Products Master (SKU Catalog)
DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products (
    category VARCHAR(50) NOT NULL,
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    unit_price_idr DECIMAL(12,2) NOT NULL,
    units_per_carton INTEGER NOT NULL
);

-- 4. Sales Transactions
DROP TABLE IF EXISTS sales CASCADE;
CREATE TABLE sales (
    transaction_id VARCHAR(30) PRIMARY KEY,
    outlet_id VARCHAR(20) NOT NULL REFERENCES outlets(outlet_id),
    transaction_date DATE NOT NULL,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    sales_cartons INTEGER NOT NULL,
    sales_units INTEGER NOT NULL,
    sales_value_idr DECIMAL(15,2) NOT NULL
);

-- 5. Delivery Logistics Fulfillment Logs
DROP TABLE IF EXISTS deliveries CASCADE;
CREATE TABLE deliveries (
    delivery_id VARCHAR(30) PRIMARY KEY,
    outlet_id VARCHAR(20) NOT NULL REFERENCES outlets(outlet_id),
    distribution_center_id VARCHAR(20) NOT NULL REFERENCES distribution_centers(distribution_center_id),
    delivery_date DATE NOT NULL,
    planned_delivery_time TIMESTAMP NOT NULL,
    actual_delivery_time TIMESTAMP NOT NULL,
    delay_minutes INTEGER NOT NULL,
    is_delayed SMALLINT NOT NULL DEFAULT 0, -- 1 if delay_minutes > 30, else 0
    delivery_distance_km DECIMAL(8,2) NOT NULL,
    cartons_delivered INTEGER NOT NULL,
    vehicle_type VARCHAR(50)
);

-- 6. Inventory & Stockout Observations
DROP TABLE IF EXISTS inventory_stockouts CASCADE;
CREATE TABLE inventory_stockouts (
    id SERIAL PRIMARY KEY,
    outlet_id VARCHAR(20) NOT NULL REFERENCES outlets(outlet_id),
    observation_date DATE NOT NULL,
    current_inventory_units INTEGER NOT NULL,
    stockout_flag SMALLINT NOT NULL, -- 1 = Stockout observed, 0 = In Stock
    stockout_duration_hours DECIMAL(6,1) DEFAULT 0.0,
    stockout_root_cause VARCHAR(150)
);

-- Indexes for high-performance analytical queries
CREATE INDEX idx_sales_outlet_date ON sales(outlet_id, transaction_date);
CREATE INDEX idx_deliveries_outlet_date ON deliveries(outlet_id, delivery_date);
CREATE INDEX idx_stockouts_outlet_date ON inventory_stockouts(outlet_id, observation_date);
CREATE INDEX idx_outlets_region ON outlets(region);
