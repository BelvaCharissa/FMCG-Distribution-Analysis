"""
geospatial_clustering.py
--------------------------------------------------------------------------------
FMCG Supply Chain Geospatial Clustering & Distribution Priority Intelligence

1. Implements DBSCAN and HDBSCAN using Haversine distance metric (radians).
2. Benchmarks model outputs (cluster counts, noise distribution, regional coverage).
3. Computes the multi-factor 'Distribution Priority Score' (0 - 100).
4. Generates an interactive HTML map for executive presentation.
5. Exports analytical master datasets for Power BI dashboard consumption.
--------------------------------------------------------------------------------
"""

import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, HDBSCAN
from sklearn.preprocessing import MinMaxScaler
import folium
from folium.plugins import MarkerCluster

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(REPORTS_DIR, exist_ok=True)

def run_clustering_and_scoring():
    print("=" * 75)
    print("FMCG GEOSPATIAL CLUSTERING & DISTRIBUTION PRIORITY MODELING")
    print("=" * 75)

    input_file = os.path.join(PROCESSED_DIR, "clean_outlet_analytics.csv")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Clean analytical dataset not found at {input_file}. Run etl_pipeline.py first!")

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df):,} outlets for geospatial modeling.")

    # 1. PREPARE COORDINATES FOR HAVERSINE METRIC
    # Scikit-learn haversine metric requires coordinates in radians: [latitude, longitude]
    coords_rad = np.radians(df[["Latitude", "Longitude"]].values)
    EARTH_RADIUS_KM = 6371.0

    # 2. RUN DBSCAN
    # Parameter tuning: eps = 4.5 km neighborhood, min_samples = 12
    eps_km = 4.5
    eps_rad = eps_km / EARTH_RADIUS_KM
    min_samples_dbscan = 12

    print(f"\n[1/4] Running DBSCAN (eps={eps_km} km, min_samples={min_samples_dbscan})...")
    dbscan = DBSCAN(eps=eps_rad, min_samples=min_samples_dbscan, metric="haversine")
    df["Cluster_DBSCAN"] = dbscan.fit_predict(coords_rad)

    db_n_clusters = len(set(df["Cluster_DBSCAN"])) - (1 if -1 in df["Cluster_DBSCAN"] else 0)
    db_noise_count = (df["Cluster_DBSCAN"] == -1).sum()
    print(f"  - DBSCAN generated: {db_n_clusters} clusters")
    print(f"  - DBSCAN noise/outliers: {db_noise_count} outlets ({db_noise_count/len(df)*100:.1f}%)")

    # 3. RUN HDBSCAN (Hierarchical Density-Based Spatial Clustering)
    # HDBSCAN adapts to varying density across dense urban core vs suburban outskirts
    min_cluster_size_hdb = 15
    min_samples_hdb = 8

    print(f"\n[2/4] Running HDBSCAN (min_cluster_size={min_cluster_size_hdb}, min_samples={min_samples_hdb})...")
    hdb = HDBSCAN(
        min_cluster_size=min_cluster_size_hdb,
        min_samples=min_samples_hdb,
        metric="haversine",
        store_centers="centroid",
        copy=True
    )
    df["Cluster_HDBSCAN"] = hdb.fit_predict(coords_rad)
    df["HDBSCAN_Membership_Prob"] = hdb.probabilities_
    df["HDBSCAN_Outlier_Score"] = 1.0 - hdb.probabilities_

    hdb_n_clusters = len(set(df["Cluster_HDBSCAN"])) - (1 if -1 in df["Cluster_HDBSCAN"] else 0)
    hdb_noise_count = (df["Cluster_HDBSCAN"] == -1).sum()
    print(f"  - HDBSCAN generated: {hdb_n_clusters} clusters")
    print(f"  - HDBSCAN noise/outliers: {hdb_noise_count} outlets ({hdb_noise_count/len(df)*100:.1f}%)")

    # We select HDBSCAN as primary model because it naturally handles density gradients
    # between dense Central Jakarta and sprawling Bekasi/Tangerang corridors.
    df["Primary_Cluster"] = df["Cluster_HDBSCAN"]
    df["Is_Noise_Outlet"] = df["Primary_Cluster"].apply(lambda x: 1 if x == -1 else 0)

    # Descriptive Cluster Naming
    def get_cluster_name(cid):
        if cid == -1:
            return "Noise / Isolated Fringe"
        return f"Geospatial Cluster {cid:02d}"

    df["Cluster_Name"] = df["Primary_Cluster"].apply(get_cluster_name)

    # 4. COMPUTE DISTRIBUTION PRIORITY SCORE (0 - 100)
    # Combining: High Demand + High Stockout Rate + High Delivery Delay + High Distance
    print("\n[3/4] Computing Multi-Factor Distribution Priority Score...")

    scaler = MinMaxScaler()
    
    # Pillar 1: Demand Volume (Log-scaled to avoid extreme supermarket skew)
    log_demand = np.log1p(df["Total_Revenue_IDR"])
    scaled_demand = scaler.fit_transform(log_demand.values.reshape(-1, 1)).flatten()

    # Pillar 2: Stockout Rate (%)
    scaled_stockout = scaler.fit_transform(df[["Stockout_Rate_Pct"]].values).flatten()

    # Pillar 3: Delivery Delay (Minutes)
    scaled_delay = scaler.fit_transform(df[["Avg_Delivery_Delay_Mins"]].values).flatten()

    # Pillar 4: Distance from DC (KM)
    scaled_dist = scaler.fit_transform(df[["Distance_to_Assigned_DC_KM"]].values).flatten()

    # Weights:
    # Demand (35%): Outlets generating revenue are vital to protect
    # Stockout (30%): Immediate symptom of lost revenue / service failure
    # Delay (20%): Logistics bottleneck contributing to stockouts
    # Distance (15%): Logistics friction / service vulnerability
    w_demand = 0.35
    w_stockout = 0.30
    w_delay = 0.20
    w_dist = 0.15

    raw_score = (
        (w_demand * scaled_demand) +
        (w_stockout * scaled_stockout) +
        (w_delay * scaled_delay) +
        (w_dist * scaled_dist)
    ) * 100

    df["Distribution_Priority_Score"] = np.round(raw_score, 1)

    # Actionable Strategic Classification
    def classify_action(row):
        score = row["Distribution_Priority_Score"]
        is_isolated = row["Is_Noise_Outlet"] == 1
        
        if is_isolated and score >= 50:
            return "Priority Tier 1 - Isolated High-Risk (Consolidate / 3PL Hub)"
        elif is_isolated:
            return "Strategic Fringe - Remote Low-Density (Periodic Dispatch)"
        elif score >= 65:
            return "Priority Tier 1 - Urgent Supply Chain Intervention"
        elif score >= 45:
            return "Priority Tier 2 - Medium Risk (Optimize & Monitor)"
        else:
            return "Priority Tier 3 - Stable Routine Fulfillment"

    df["Action_Recommendation"] = df.apply(classify_action, axis=1)

    # 5. AGGREGATE CLUSTER SUMMARY
    cluster_summary = df.groupby(["Primary_Cluster", "Cluster_Name"]).agg(
        Total_Outlets=("Outlet_ID", "count"),
        Total_Revenue_IDR=("Total_Revenue_IDR", "sum"),
        Revenue_Share_Pct=("Revenue_Contribution_Pct", "sum"),
        Avg_Stockout_Rate_Pct=("Stockout_Rate_Pct", "mean"),
        Avg_Delivery_Delay_Mins=("Avg_Delivery_Delay_Mins", "mean"),
        Avg_Distance_to_DC_KM=("Distance_to_Assigned_DC_KM", "mean"),
        Avg_Priority_Score=("Distribution_Priority_Score", "mean"),
        High_Priority_Outlet_Count=("Distribution_Priority_Score", lambda x: (x >= 65).sum())
    ).reset_index().sort_values(by="Total_Revenue_IDR", ascending=False)

    # High Priority Table
    high_priority_outlets = df[df["Distribution_Priority_Score"] >= 65].sort_values(
        by="Distribution_Priority_Score", ascending=False
    )

    # 6. EXPORT PROCESSED DATASETS
    output_master = os.path.join(PROCESSED_DIR, "analytical_outlet_master.csv")
    output_summary = os.path.join(PROCESSED_DIR, "clusters_summary.csv")
    output_high_pri = os.path.join(PROCESSED_DIR, "high_priority_outlets.csv")

    df.to_csv(output_master, index=False)
    cluster_summary.to_csv(output_summary, index=False)
    high_priority_outlets.to_csv(output_high_pri, index=False)

    print(f"\n[4/4] Processed Datasets Exported:")
    print(f"  - Master Dataset: {output_master} ({len(df):,} rows)")
    print(f"  - Clusters Summary: {output_summary} ({len(cluster_summary):,} clusters)")
    print(f"  - High Priority Action Outlets: {output_high_pri} ({len(high_priority_outlets):,} outlets)")

    # 7. GENERATE INTERACTIVE FOLIUM MAP
    print("\nGenerating Interactive Map (HTML) for Executive Visual Presentation...")
    df_dcs = pd.read_csv(os.path.join(RAW_DIR, "distribution_centers_raw.csv"))

    # Map centered at Jakarta
    fmap = folium.Map(location=[-6.28, 106.85], zoom_start=10, tiles="CartoDB positron")

    # Add Distribution Centers
    for _, dc in df_dcs.iterrows():
        folium.Marker(
            location=[dc["Latitude"], dc["Longitude"]],
            popup=f"<b>DC HUB: {dc['DC_Name']}</b><br>City: {dc['City']}<br>Capacity: {dc['Daily_Capacity_Cartons']:,} cartons/day<br>Fleet: {dc['Fleet_Size']} trucks",
            tooltip=f"Distribution Center: {dc['DC_Name']}",
            icon=folium.Icon(color="red", icon="home", prefix="fa")
        ).add_to(fmap)

    # Cluster Colors
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    
    # Add Outlets
    for _, out in df.iterrows():
        cid = out["Primary_Cluster"]
        score = out["Distribution_Priority_Score"]
        
        if cid == -1:
            color = "#555555" # Grey for noise
            radius = 4
        elif score >= 65:
            color = "#d90429" # Bright Red for high priority
            radius = 6
        else:
            color = palette[cid % len(palette)]
            radius = 4

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; width: 220px;">
            <h4 style="margin: 0 0 5px 0; color: #111;">{out['Outlet_Name']}</h4>
            <b>ID:</b> {out['Outlet_ID']}<br>
            <b>Type:</b> {out['Outlet_Type']}<br>
            <b>Region:</b> {out['Region']}<br>
            <hr style="margin: 5px 0;">
            <b>Cluster:</b> {out['Cluster_Name']}<br>
            <b>Priority Score:</b> <span style="color: {'red' if score >= 65 else 'black'}; font-weight: bold;">{score} / 100</span><br>
            <b>Action:</b> {out['Action_Recommendation']}<br>
            <hr style="margin: 5px 0;">
            <b>Revenue:</b> IDR {out['Total_Revenue_IDR']:,.0f}<br>
            <b>Stockout Rate:</b> {out['Stockout_Rate_Pct']:.1f}%<br>
            <b>Avg Delivery Delay:</b> {out['Avg_Delivery_Delay_Mins']:.1f} mins<br>
            <b>Distance to DC:</b> {out['Distance_to_Assigned_DC_KM']:.1f} km
        </div>
        """
        
        folium.CircleMarker(
            location=[out["Latitude"], out["Longitude"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{out['Outlet_Name']} (Priority: {score})"
        ).add_to(fmap)

    map_path = os.path.join(REPORTS_DIR, "interactive_distribution_map.html")
    fmap.save(map_path)
    print(f"Map successfully generated: {map_path}")
    print("=" * 75)

if __name__ == "__main__":
    run_clustering_and_scoring()
