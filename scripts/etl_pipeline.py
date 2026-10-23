"""
etl_pipeline.py
--------------------------------------------------------------------------------
FMCG Supply Chain Analytics - Data Extraction, Cleaning, and Feature Engineering

Functions:
1. Load raw datasets from data/raw/
2. Clean data (trim whitespace, eliminate duplicate transactions, validate coordinates)
3. Calculate outlet-level business metrics across Sales, Deliveries, and Stockouts
4. Export clean analytical dataset to data/processed/
--------------------------------------------------------------------------------
"""

import os
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two points in km."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2.0)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def run_etl():
    print("=" * 70)
    print("FMCG SUPPLY CHAIN ETL & DATA INTEGRATION PIPELINE")
    print("=" * 70)

    # 1. LOAD RAW DATA
    print("[1/4] Loading raw CSV datasets...")
    df_dcs = pd.read_csv(os.path.join(RAW_DIR, "distribution_centers_raw.csv"))
    df_outlets = pd.read_csv(os.path.join(RAW_DIR, "outlets_raw.csv"))
    df_products = pd.read_csv(os.path.join(RAW_DIR, "products_raw.csv"))
    df_sales = pd.read_csv(os.path.join(RAW_DIR, "sales_raw.csv"))
    df_deliveries = pd.read_csv(os.path.join(RAW_DIR, "deliveries_raw.csv"))
    df_inventory = pd.read_csv(os.path.join(RAW_DIR, "inventory_stockouts_raw.csv"))

    print(f"  - Loaded Outlets: {len(df_outlets):,} records")
    print(f"  - Loaded Sales: {len(df_sales):,} records")
    print(f"  - Loaded Deliveries: {len(df_deliveries):,} records")
    print(f"  - Loaded Stockout Audits: {len(df_inventory):,} records")

    # 2. DATA CLEANING & AUDITING
    print("\n[2/4] Executing Data Quality Audits & Cleaning...")
    
    # Clean Outlets strings and coordinates
    df_outlets["Outlet_Name"] = df_outlets["Outlet_Name"].astype(str).str.strip()
    df_outlets["Region"] = df_outlets["Region"].astype(str).str.strip()
    
    # Coordinate validation (Indonesia coordinates: Lat [-11, 6], Lon [95, 141])
    valid_coords = (
        (df_outlets["Latitude"].between(-11.0, 6.0)) & 
        (df_outlets["Longitude"].between(95.0, 141.0))
    )
    invalid_coord_count = (~valid_coords).sum()
    if invalid_coord_count > 0:
        print(f"  ! Warning: Filtered out {invalid_coord_count} outlets with invalid coordinates.")
        df_outlets = df_outlets[valid_coords].copy()
    else:
        print("  - Coordinates validation passed (100% within valid geospatial bounds).")

    # Clean Sales: Remove duplicates
    initial_sales_len = len(df_sales)
    df_sales = df_sales.drop_duplicates(subset=["Transaction_ID"])
    dropped_sales = initial_sales_len - len(df_sales)
    print(f"  - Sales deduplication: Dropped {dropped_sales} duplicate transactions.")

    # 3. FEATURE ENGINEERING & METRIC AGGREGATION
    print("\n[3/4] Engineering Analytical Features per Outlet...")

    # A. Sales Aggregation
    sales_agg = df_sales.groupby("Outlet_ID").agg(
        Total_Orders=("Transaction_ID", "count"),
        Total_Cartons_Demanded=("Sales_Cartons", "sum"),
        Total_Units_Demanded=("Sales_Units", "sum"),
        Total_Revenue_IDR=("Sales_Value_IDR", "sum")
    ).reset_index()

    network_total_rev = sales_agg["Total_Revenue_IDR"].sum()
    sales_agg["Revenue_Contribution_Pct"] = (sales_agg["Total_Revenue_IDR"] / network_total_rev) * 100

    # B. Deliveries Aggregation
    deliveries_agg = df_deliveries.groupby("Outlet_ID").agg(
        Total_Deliveries=("Delivery_ID", "count"),
        Delayed_Deliveries=("Is_Delayed", "sum"),
        Avg_Delivery_Delay_Mins=("Delay_Minutes", "mean"),
        Max_Delivery_Delay_Mins=("Delay_Minutes", "max"),
        Avg_Delivery_Distance_KM=("Delivery_Distance_KM", "mean")
    ).reset_index()

    deliveries_agg["On_Time_Deliveries"] = deliveries_agg["Total_Deliveries"] - deliveries_agg["Delayed_Deliveries"]
    deliveries_agg["On_Time_Delivery_Rate_Pct"] = (
        deliveries_agg["On_Time_Deliveries"] / deliveries_agg["Total_Deliveries"]
    ) * 100

    # C. Stockout & Inventory Aggregation
    stockout_agg = df_inventory.groupby("Outlet_ID").agg(
        Total_Audits=("Observation_Date", "count"),
        Stockout_Occurrences=("Stockout_Flag", "sum"),
        Avg_Stockout_Duration_Hours=("Stockout_Duration_Hours", lambda x: x[x > 0].mean() if (x > 0).any() else 0.0),
        Avg_Inventory_Level=("Current_Inventory_Units", "mean")
    ).reset_index()

    stockout_agg["Stockout_Rate_Pct"] = (
        stockout_agg["Stockout_Occurrences"] / stockout_agg["Total_Audits"]
    ) * 100

    # 4. MERGE DATASETS INTO ANALYTICAL MASTER
    print("\n[4/4] Merging all dimensions into analytical master dataset...")
    df_analytical = df_outlets.merge(sales_agg, on="Outlet_ID", how="left")
    df_analytical = df_analytical.merge(deliveries_agg, on="Outlet_ID", how="left")
    df_analytical = df_analytical.merge(stockout_agg, on="Outlet_ID", how="left")

    # Add DC distance
    dc_lookup = df_dcs.set_index("Distribution_Center_ID")[["Latitude", "Longitude", "DC_Name"]].to_dict(orient="index")
    
    def get_dc_distance(row):
        dc_id = row["Distribution_Center_ID"]
        if dc_id in dc_lookup:
            dc_lat = dc_lookup[dc_id]["Latitude"]
            dc_lon = dc_lookup[dc_id]["Longitude"]
            return round(haversine_km(dc_lat, dc_lon, row["Latitude"], row["Longitude"]), 2)
        return np.nan

    df_analytical["Distance_to_Assigned_DC_KM"] = df_analytical.apply(get_dc_distance, axis=1)

    # Fill any null values for newly opened outlets without transactions
    df_analytical["Total_Orders"] = df_analytical["Total_Orders"].fillna(0)
    df_analytical["Total_Cartons_Demanded"] = df_analytical["Total_Cartons_Demanded"].fillna(0)
    df_analytical["Total_Revenue_IDR"] = df_analytical["Total_Revenue_IDR"].fillna(0)
    df_analytical["Revenue_Contribution_Pct"] = df_analytical["Revenue_Contribution_Pct"].fillna(0)
    df_analytical["Stockout_Rate_Pct"] = df_analytical["Stockout_Rate_Pct"].fillna(0)
    df_analytical["Avg_Delivery_Delay_Mins"] = df_analytical["Avg_Delivery_Delay_Mins"].fillna(0)
    df_analytical["On_Time_Delivery_Rate_Pct"] = df_analytical["On_Time_Delivery_Rate_Pct"].fillna(100)

    # Save to CSV
    output_path = os.path.join(PROCESSED_DIR, "clean_outlet_analytics.csv")
    df_analytical.to_csv(output_path, index=False)

    print(f"\nETL Completed Successfully!")
    print(f"Output File: {output_path}")
    print(f"Total Outlets Processed: {len(df_analytical):,}")
    print(f"Total Network Revenue: IDR {network_total_rev:,.2f}")
    print(f"Average Network Stockout Rate: {df_analytical['Stockout_Rate_Pct'].mean():.2f}%")
    print(f"Average On-Time Delivery Rate: {df_analytical['On_Time_Delivery_Rate_Pct'].mean():.2f}%\n")

if __name__ == "__main__":
    run_etl()
