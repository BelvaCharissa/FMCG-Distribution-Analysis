"""
generate_raw_data.py
--------------------------------------------------------------------------------
Generates realistic, synthetic FMCG supply chain and distribution raw datasets
modeled after real-world operations in the Jabodetabek (Greater Jakarta) region.

Tables generated:
1. data/raw/distribution_centers_raw.csv  (3 Primary Regional DCs)
2. data/raw/outlets_raw.csv               (1,250 Outlets with coordinates & types)
3. data/raw/products_raw.csv              (20 Top FMCG SKUs)
4. data/raw/sales_raw.csv                 (~30,000 Transaction records over 90 days)
5. data/raw/deliveries_raw.csv            (~8,500 Delivery fulfillment logs)
6. data/raw/inventory_stockouts_raw.csv   (~12,000 Inventory audit & stockout records)
--------------------------------------------------------------------------------
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set fixed seed for reproducibility
np.random.seed(42)
random.seed(42)

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# 1. DISTRIBUTION CENTERS MASTER
# ------------------------------------------------------------------------------
print("[1/6] Generating Distribution Centers...")
dcs = [
    {
        "Distribution_Center_ID": "DC-JKT-01",
        "DC_Name": "Central Jakarta Logistics Hub (Ciracas)",
        "City": "Jakarta Timur",
        "Latitude": -6.3250,
        "Longitude": 106.8720,
        "Daily_Capacity_Cartons": 15000,
        "Fleet_Size": 35
    },
    {
        "Distribution_Center_ID": "DC-BKS-02",
        "DC_Name": "East Megahub Cikarang",
        "City": "Bekasi",
        "Latitude": -6.2980,
        "Longitude": 107.1320,
        "Daily_Capacity_Cartons": 25000,
        "Fleet_Size": 50
    },
    {
        "Distribution_Center_ID": "DC-TNG-03",
        "DC_Name": "West Distribution Depot (Bitung)",
        "City": "Tangerang",
        "Latitude": -6.2410,
        "Longitude": 106.5620,
        "Daily_Capacity_Cartons": 18000,
        "Fleet_Size": 40
    }
]
df_dcs = pd.DataFrame(dcs)
df_dcs.to_csv(os.path.join(RAW_DATA_DIR, "distribution_centers_raw.csv"), index=False)

# ------------------------------------------------------------------------------
# 2. OUTLET MASTER DATA (1,250 Outlets with Spatial Clusters + Outliers)
# ------------------------------------------------------------------------------
print("[2/6] Generating 1,250 Outlets with spatial clusters and isolated points...")

# Cluster definitions (Lat, Lon, Spread, Region, Target count)
cluster_specs = [
    {"name": "Jakarta Selatan & Pusat", "lat": -6.225, "lon": 106.825, "std": 0.035, "region": "Jakarta", "count": 300},
    {"name": "Jakarta Timur & Utara", "lat": -6.185, "lon": 106.905, "std": 0.040, "region": "Jakarta", "count": 220},
    {"name": "Tangerang & BSD Modern", "lat": -6.245, "lon": 106.635, "std": 0.045, "region": "Tangerang", "count": 260},
    {"name": "Bekasi Kota & Tambun", "lat": -6.255, "lon": 107.015, "std": 0.040, "region": "Bekasi", "count": 240},
    {"name": "Depok & Cibinong Corridor", "lat": -6.415, "lon": 106.845, "std": 0.045, "region": "Depok-Bogor", "count": 130},
    # Isolated / Noise Outlets (Rural / Fringe areas)
    {"name": "Bogor Selatan & Perbukitan (Outlier)", "lat": -6.650, "lon": 106.820, "std": 0.090, "region": "Bogor Fringe", "count": 55},
    {"name": "Serang & Tangerang Barat (Outlier)", "lat": -6.180, "lon": 106.380, "std": 0.080, "region": "Banten Fringe", "count": 45}
]

outlet_types = ["Warung Kelontong", "Minimarket", "Supermarket", "Wholesaler"]
type_weights = [0.60, 0.25, 0.10, 0.05]

outlets_list = []
outlet_counter = 1

for spec in cluster_specs:
    lats = np.random.normal(loc=spec["lat"], scale=spec["std"], size=spec["count"])
    lons = np.random.normal(loc=spec["lon"], scale=spec["std"], size=spec["count"])
    
    for lat, lon in zip(lats, lons):
        otype = random.choices(outlet_types, weights=type_weights)[0]
        
        # Name generation based on type
        if otype == "Warung Kelontong":
            names = ["Warung Berkah", "Toko Sembako Barokah", "Kios Madura Rezeki", "Warung Sumber Rejeki", "Toko Bu Ani", "Warung Pak Joko", "Kios Sejahtera", "Warung Pojok Jaya", "Toko Kelontong Mitra"]
            oname = f"{random.choice(names)} #{outlet_counter}"
        elif otype == "Minimarket":
            chain = random.choice(["Indomakmur Express", "Alfamaju Mart", "Circle-Fresh", "FamilyPmart"])
            oname = f"{chain} {spec['region']} #{random.randint(10, 999)}"
        elif otype == "Supermarket":
            chain = random.choice(["Grand Mega Supermarket", "Heroic Fresh", "Total Food Center", "Lotte Star Mart"])
            oname = f"{chain} {spec['region']}"
        else:
            oname = f"Grosir Sembako Utama #{outlet_counter}"
            
        # Assign closest DC initially based on naive Euclidean
        dist_jkt = (lat - (-6.325))**2 + (lon - 106.872)**2
        dist_bks = (lat - (-6.298))**2 + (lon - 107.132)**2
        dist_tng = (lat - (-6.241))**2 + (lon - 106.562)**2
        
        assigned_dc = "DC-JKT-01"
        if dist_bks < dist_jkt and dist_bks < dist_tng:
            assigned_dc = "DC-BKS-02"
        elif dist_tng < dist_jkt and dist_tng < dist_bks:
            assigned_dc = "DC-TNG-03"
            
        outlets_list.append({
            "Outlet_ID": f"OUT-{outlet_counter:04d}",
            "Outlet_Name": oname,
            "Outlet_Type": otype,
            "Region": spec["region"],
            "Sub_District": f"{spec['region']} Sub-area {random.randint(1, 12)}",
            "Latitude": round(float(lat), 6),
            "Longitude": round(float(lon), 6),
            "Distribution_Center_ID": assigned_dc,
            "Store_Size_SQM": 15 if otype == "Warung Kelontong" else (90 if otype == "Minimarket" else (450 if otype == "Supermarket" else 200)),
            "Status": "Active"
        })
        outlet_counter += 1

# Introduce a small intentional raw data imperfection (2 duplicate rows, 3 trailing spaces)
df_outlets = pd.DataFrame(outlets_list)
# Add trailing spaces on a couple names to simulate raw entry
df_outlets.loc[5, "Outlet_Name"] = df_outlets.loc[5, "Outlet_Name"] + "   "
df_outlets.loc[12, "Outlet_Name"] = "  " + df_outlets.loc[12, "Outlet_Name"]
# Save raw
df_outlets.to_csv(os.path.join(RAW_DATA_DIR, "outlets_raw.csv"), index=False)

# ------------------------------------------------------------------------------
# 3. PRODUCTS MASTER (20 Fast-Moving FMCG SKUs)
# ------------------------------------------------------------------------------
print("[3/6] Generating 20 FMCG Products...")
products = [
    # Category, Product_ID, Product_Name, Unit_Price_IDR, Units_Per_Carton
    ("Beverage", "PRD-BEV-001", "Teh Kotak Melati 250ml", 4500, 24),
    ("Beverage", "PRD-BEV-002", "Air Mineral Aqua 600ml", 3500, 24),
    ("Beverage", "PRD-BEV-003", "Kopi Susu Mantap Botol 200ml", 7000, 24),
    ("Beverage", "PRD-BEV-004", "Minuman Isotonik Mizone 500ml", 6500, 24),
    ("Beverage", "PRD-BEV-005", "Sari Kacang Ijo Ultra 250ml", 5000, 24),
    ("Personal Care", "PRD-PC-001", "Shampoo Anti Ketombe Clear 160ml", 28000, 12),
    ("Personal Care", "PRD-PC-002", "Sabun Mandi Lifebuoy Bar 85g", 4200, 36),
    ("Personal Care", "PRD-PC-003", "Pasta Gigi Pepsodent 190g", 14500, 24),
    ("Personal Care", "PRD-PC-004", "Deterjen Rinso Molto 770g", 21500, 12),
    ("Personal Care", "PRD-PC-005", "Pembersih Lantai Super Pell 770ml", 13000, 12),
    ("Packaged Food", "PRD-FD-001", "Indomie Goreng Spesial 85g", 3100, 40),
    ("Packaged Food", "PRD-FD-002", "Indomie Kuah Ayam Bawang 69g", 2900, 40),
    ("Packaged Food", "PRD-FD-003", "Biskuit Roma Kelapa 300g", 11500, 20),
    ("Packaged Food", "PRD-FD-004", "Keripik Chitato Sapi Panggang 68g", 12000, 30),
    ("Packaged Food", "PRD-FD-005", "Kusuka Keripik Singkong 180g", 16000, 20),
    ("Packaged Food", "PRD-FD-006", "Samyang Hot Chicken Ramen 140g", 22000, 20),
    ("Dairy", "PRD-DY-001", "Susu UHT Ultra Milk Cokelat 1L", 21000, 12),
    ("Dairy", "PRD-DY-002", "Susu Kental Manis Frisian Flag 370g", 12500, 48),
    ("Dairy", "PRD-DY-003", "Susu UHT Dancow FortiGro 115ml", 4500, 36),
    ("Dairy", "PRD-DY-004", "Keju Kraft Cheddar All-in-One 160g", 15500, 24),
]

df_products = pd.DataFrame(products, columns=[
    "Category", "Product_ID", "Product_Name", "Unit_Price_IDR", "Units_Per_Carton"
])
df_products.to_csv(os.path.join(RAW_DATA_DIR, "products_raw.csv"), index=False)

# ------------------------------------------------------------------------------
# 4. SALES TRANSACTIONS (~32,000 Transactions over 90 Days)
# ------------------------------------------------------------------------------
print("[4/6] Generating ~32,000 Sales Transactions over 90 days...")

start_date = datetime(2026, 7, 1)
end_date = datetime(2026, 9, 30)
date_range_days = (end_date - start_date).days

sales_records = []
trx_id = 100001

# Multipliers based on outlet type
type_demand_mult = {
    "Warung Kelontong": 1.0,
    "Minimarket": 3.5,
    "Supermarket": 8.0,
    "Wholesaler": 12.0
}

# Precompute product price lookup
price_lookup = {p[1]: (p[3], p[4]) for p in products}
prod_ids = list(price_lookup.keys())

for idx, outlet in df_outlets.iterrows():
    oid = outlet["Outlet_ID"]
    otype = outlet["Outlet_Type"]
    mult = type_demand_mult[otype]
    
    # Warung has fewer orders, Supermarket orders very frequently
    order_freq = int(random.triangular(8, 25, 45) * (0.6 if otype == "Warung Kelontong" else 1.2))
    
    for _ in range(order_freq):
        day_offset = random.randint(0, date_range_days)
        t_date = start_date + timedelta(days=day_offset)
        
        # Basket size: 1 to 4 SKUs per transaction
        n_skus = random.randint(1, 3 if otype == "Warung Kelontong" else 6)
        chosen_skus = random.sample(prod_ids, n_skus)
        
        for pid in chosen_skus:
            u_price, carton_sz = price_lookup[pid]
            cartons = int(max(1, np.random.poisson(lam=1.5 * mult)))
            units = cartons * carton_sz
            sales_val = units * u_price
            
            sales_records.append({
                "Transaction_ID": f"TRX-{trx_id}",
                "Outlet_ID": oid,
                "Transaction_Date": t_date.strftime("%Y-%m-%d"),
                "Product_ID": pid,
                "Sales_Cartons": cartons,
                "Sales_Units": units,
                "Sales_Value_IDR": sales_val
            })
            trx_id += 1

df_sales = pd.DataFrame(sales_records)
# Add 5 intentional duplicate transaction rows at the bottom (raw data artifact)
duplicates = df_sales.iloc[:5].copy()
df_sales = pd.concat([df_sales, duplicates], ignore_index=True)
df_sales.to_csv(os.path.join(RAW_DATA_DIR, "sales_raw.csv"), index=False)
print(f"    Total sales rows generated: {len(df_sales):,}")

# ------------------------------------------------------------------------------
# 5. DELIVERY FULFILLMENT LOGS (~8,500 Deliveries)
# ------------------------------------------------------------------------------
print("[5/6] Generating Logistics & Delivery Logs...")

# Haversine distance helper (KM)
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2.0)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

dc_coords = {d["Distribution_Center_ID"]: (d["Latitude"], d["Longitude"]) for d in dcs}

delivery_records = []
del_id = 500001

for idx, outlet in df_outlets.iterrows():
    oid = outlet["Outlet_ID"]
    dc_id = outlet["Distribution_Center_ID"]
    dc_lat, dc_lon = dc_coords[dc_id]
    
    # Calculate baseline road distance
    straight_dist = haversine_km(dc_lat, dc_lon, outlet["Latitude"], outlet["Longitude"])
    # Actual road distance factor (~1.25x to 1.55x straight line)
    road_dist_km = round(straight_dist * random.uniform(1.25, 1.55), 2)
    
    # Delivery frequency depends on outlet volume
    num_deliveries = random.randint(4, 16)
    
    for _ in range(num_deliveries):
        day_offset = random.randint(0, date_range_days)
        d_date = start_date + timedelta(days=day_offset)
        
        # Planned delivery slot (e.g. 09:00 AM)
        planned_dt = d_date.replace(hour=random.randint(8, 12), minute=0, second=0)
        
        # Delay simulation:
        # Distance > 35km and fringe/outlier areas have higher probability of major delays
        is_far = road_dist_km > 35.0
        base_delay_minutes = np.random.exponential(scale=25 if not is_far else 70)
        
        # Occasional logistics anomaly (e.g., breakdown, heavy toll traffic, rainy season flood)
        if random.random() < 0.12:
            base_delay_minutes += random.randint(60, 180)
            
        actual_dt = planned_dt + timedelta(minutes=int(base_delay_minutes))
        delay_mins = int((actual_dt - planned_dt).total_seconds() / 60)
        is_delayed = 1 if delay_mins > 30 else 0
        
        delivery_records.append({
            "Delivery_ID": f"DEL-{del_id}",
            "Outlet_ID": oid,
            "Distribution_Center_ID": dc_id,
            "Delivery_Date": d_date.strftime("%Y-%m-%d"),
            "Planned_Delivery_Time": planned_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "Actual_Delivery_Time": actual_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "Delay_Minutes": delay_mins,
            "Is_Delayed": is_delayed,
            "Delivery_Distance_KM": road_dist_km,
            "Cartons_Delivered": random.randint(5, 60),
            "Vehicle_Type": "Blind Van" if road_dist_km < 20 else ("CDD Box Truck" if road_dist_km < 50 else "Fuso Heavy")
        })
        del_id += 1

df_deliveries = pd.DataFrame(delivery_records)
df_deliveries.to_csv(os.path.join(RAW_DATA_DIR, "deliveries_raw.csv"), index=False)
print(f"    Total delivery logs generated: {len(df_deliveries):,}")

# ------------------------------------------------------------------------------
# 6. INVENTORY & STOCKOUT LOGS (~12,500 Observations)
# ------------------------------------------------------------------------------
print("[6/6] Generating Inventory & Stockout Observation Logs...")

inventory_records = []
obs_dates = [start_date + timedelta(days=i*7 + random.randint(0, 3)) for i in range(12)]

# Compute delivery delay average per outlet to correlate with stockout likelihood
avg_delay_per_outlet = df_deliveries.groupby("Outlet_ID")["Delay_Minutes"].mean().to_dict()

for idx, outlet in df_outlets.iterrows():
    oid = outlet["Outlet_ID"]
    otype = outlet["Outlet_Type"]
    outlet_delay = avg_delay_per_outlet.get(oid, 20.0)
    
    # Probability of stockout increases with:
    # 1. Higher delivery delay
    # 2. Smaller outlet storage (Warung has tiny safety stock compared to Supermarket)
    base_stockout_prob = 0.14
    if otype == "Warung Kelontong":
        base_stockout_prob += 0.08
    elif otype == "Supermarket":
        base_stockout_prob -= 0.05
        
    if outlet_delay > 45:
        base_stockout_prob += 0.12
    if outlet_delay > 90:
        base_stockout_prob += 0.15
        
    base_stockout_prob = min(0.65, max(0.02, base_stockout_prob))
    
    for obs_dt in obs_dates:
        is_stockout = 1 if (random.random() < base_stockout_prob) else 0
        
        if is_stockout == 1:
            duration_hrs = round(random.triangular(4, 24, 72), 1)
            inv_level = 0
            reason = random.choice([
                "Late delivery from DC",
                "Unexpected demand surge",
                "Supplier stock constraint",
                "Storage capacity bottleneck",
                "Order frequency gap"
            ])
        else:
            duration_hrs = 0.0
            inv_level = random.randint(15, 250)
            reason = "In Stock"
            
        inventory_records.append({
            "Outlet_ID": oid,
            "Observation_Date": obs_dt.strftime("%Y-%m-%d"),
            "Current_Inventory_Units": inv_level,
            "Stockout_Flag": is_stockout,
            "Stockout_Duration_Hours": duration_hrs,
            "Stockout_Root_Cause": reason
        })

df_inventory = pd.DataFrame(inventory_records)
df_inventory.to_csv(os.path.join(RAW_DATA_DIR, "inventory_stockouts_raw.csv"), index=False)
print(f"    Total inventory observation records generated: {len(df_inventory):,}")

print("\nAll raw datasets successfully generated in: data/raw/")
