"""
app.py
--------------------------------------------------------------------------------
FMCG Supply Chain & Distribution Analytics Web Application
Decision Support & Geospatial Distribution Intelligence System
--------------------------------------------------------------------------------
"""

import os
import json
import numpy as np
import pandas as pd
from flask import Flask, render_template, jsonify, request

app = Flask(__name__, static_folder="static", template_folder="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "analytical_outlet_master.csv")
RAW_DCS_PATH = os.path.join(BASE_DIR, "data", "raw", "distribution_centers_raw.csv")
CLUSTERS_SUMMARY_PATH = os.path.join(BASE_DIR, "data", "processed", "clusters_summary.csv")

# Indonesian Business Cluster Names mapping
BUSINESS_CLUSTER_NAMES = {
    3: "Kelompok Jakarta Pusat & Selatan (Wilayah Inti)",
    4: "Kelompok Tangerang & Serpong (Koridor Barat)",
    2: "Kelompok Bekasi & Tambun (Koridor Timur)",
    1: "Kelompok Sub-Regional Selatan (Jarak Jauh & Rawan Stockout)",
    0: "Kelompok Barat Daya (Sekunder)",
    -1: "Outlet di Luar Kelompok Utama (Terpencil / Non-Klaster)"
}

def load_data():
    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError("Processed analytical dataset missing. Run etl_pipeline.py and geospatial_clustering.py!")
    df_outlets = pd.read_csv(PROCESSED_DATA_PATH)
    df_dcs = pd.read_csv(RAW_DCS_PATH)
    df_clusters = pd.read_csv(CLUSTERS_SUMMARY_PATH)

    # Attach natural business cluster name
    df_outlets["Business_Cluster_Name"] = df_outlets["Primary_Cluster"].map(
        lambda c: BUSINESS_CLUSTER_NAMES.get(c, f"Kelompok Wilayah {c}")
    )

    # Calculate Quadrants based on network medians
    med_revenue = float(df_outlets["Total_Revenue_IDR"].median())
    med_stockout = float(df_outlets["Stockout_Rate_Pct"].median())

    def assign_quadrant(row):
        rev = row["Total_Revenue_IDR"]
        stock = row["Stockout_Rate_Pct"]
        if rev >= med_revenue and stock >= med_stockout:
            return "Q1"  # Permintaan Tinggi, Stockout Tinggi (Prioritas Utama)
        elif rev >= med_revenue and stock < med_stockout:
            return "Q2"  # Permintaan Tinggi, Stockout Rendah (Pertahankan)
        elif rev < med_revenue and stock >= med_stockout:
            return "Q3"  # Permintaan Rendah, Stockout Tinggi (Evaluasi Pola Pengiriman)
        else:
            return "Q4"  # Permintaan Rendah, Stockout Rendah (Pemantauan Rutin)

    df_outlets["Quadrant"] = df_outlets.apply(assign_quadrant, axis=1)

    return df_outlets, df_dcs, df_clusters, med_revenue, med_stockout

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return ("", 204)

@app.route("/api/summary")
def get_summary():
    df_outlets, df_dcs, df_clusters, med_revenue, med_stockout = load_data()

    total_outlets = len(df_outlets)
    total_revenue = float(df_outlets["Total_Revenue_IDR"].sum())
    avg_stockout_rate = float(df_outlets["Stockout_Rate_Pct"].mean())
    avg_delay_mins = float(df_outlets["Avg_Delivery_Delay_Mins"].mean())
    on_time_delivery_rate = float(df_outlets["On_Time_Delivery_Rate_Pct"].mean())
    total_clusters = int(df_outlets["Primary_Cluster"].nunique() - (1 if -1 in df_outlets["Primary_Cluster"].values else 0))
    noise_outlets = int((df_outlets["Primary_Cluster"] == -1).sum())
    high_priority_count = int((df_outlets["Distribution_Priority_Score"] >= 65).sum())

    # Quadrant counts
    q1_count = int((df_outlets["Quadrant"] == "Q1").sum())
    q2_count = int((df_outlets["Quadrant"] == "Q2").sum())
    q3_count = int((df_outlets["Quadrant"] == "Q3").sum())
    q4_count = int((df_outlets["Quadrant"] == "Q4").sum())

    # Summary by Outlet Type
    by_type = df_outlets.groupby("Outlet_Type").agg(
        Count=("Outlet_ID", "count"),
        Total_Revenue=("Total_Revenue_IDR", "sum"),
        Avg_Stockout_Rate=("Stockout_Rate_Pct", "mean"),
        Avg_Priority=("Distribution_Priority_Score", "mean")
    ).reset_index().to_dict(orient="records")

    # Summary by Region
    by_region = df_outlets.groupby("Region").agg(
        Count=("Outlet_ID", "count"),
        Total_Revenue=("Total_Revenue_IDR", "sum"),
        Avg_Stockout_Rate=("Stockout_Rate_Pct", "mean"),
        Avg_Delay=("Avg_Delivery_Delay_Mins", "mean")
    ).reset_index().to_dict(orient="records")

    return jsonify({
        "metrics": {
            "total_outlets": total_outlets,
            "total_revenue_idr": total_revenue,
            "avg_stockout_rate_pct": round(avg_stockout_rate, 2),
            "avg_delay_mins": round(avg_delay_mins, 1),
            "on_time_delivery_rate_pct": round(on_time_delivery_rate, 2),
            "total_clusters": total_clusters,
            "noise_outlets_count": noise_outlets,
            "high_priority_count": high_priority_count
        },
        "quadrant_info": {
            "med_revenue_idr": round(med_revenue, 0),
            "med_stockout_pct": round(med_stockout, 2),
            "q1_count": q1_count,
            "q2_count": q2_count,
            "q3_count": q3_count,
            "q4_count": q4_count
        },
        "by_type": by_type,
        "by_region": by_region
    })

@app.route("/api/outlets")
def get_outlets():
    df_outlets, _, _, _, _ = load_data()

    # Query filters
    region = request.args.get("region")
    outlet_type = request.args.get("type")
    cluster = request.args.get("cluster")
    priority_tier = request.args.get("tier")
    quadrant = request.args.get("quadrant")

    df_filtered = df_outlets.copy()
    if region and region != "all":
        df_filtered = df_filtered[df_filtered["Region"] == region]
    if outlet_type and outlet_type != "all":
        df_filtered = df_filtered[df_filtered["Outlet_Type"] == outlet_type]
    if cluster and cluster != "all":
        df_filtered = df_filtered[df_filtered["Primary_Cluster"] == int(cluster)]
    if quadrant and quadrant != "all":
        df_filtered = df_filtered[df_filtered["Quadrant"] == quadrant.upper()]
    if priority_tier:
        if priority_tier == "high":
            df_filtered = df_filtered[df_filtered["Distribution_Priority_Score"] >= 65]
        elif priority_tier == "medium":
            df_filtered = df_filtered[(df_filtered["Distribution_Priority_Score"] >= 45) & (df_filtered["Distribution_Priority_Score"] < 65)]
        elif priority_tier == "noise":
            df_filtered = df_filtered[df_filtered["Primary_Cluster"] == -1]

    outlets_data = df_filtered.to_dict(orient="records")
    return jsonify({
        "count": len(outlets_data),
        "outlets": outlets_data
    })

@app.route("/api/dcs")
def get_dcs():
    _, df_dcs, _, _, _ = load_data()
    return jsonify(df_dcs.to_dict(orient="records"))

@app.route("/api/clusters")
def get_clusters():
    _, _, df_clusters, _, _ = load_data()
    # Map business cluster names
    clusters_data = df_clusters.to_dict(orient="records")
    for c in clusters_data:
        cid = c.get("Primary_Cluster")
        c["Business_Name"] = BUSINESS_CLUSTER_NAMES.get(cid, c.get("Cluster_Name"))
    return jsonify(clusters_data)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"[FMCG Dashboard Server] Starting Web App on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
