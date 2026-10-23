/**
 * FMCG Distribution Analytics — Frontend Controller
 * Geospatial Map with Priority Ranking (Danger level) & Linked Data Table
 */

const state = {
    allOutlets: [],
    filteredOutlets: [],
    dcs: [],
    summary: null,
    leafletMap: null,
    leafletMarkersLayer: null,
    leafletDcsLayer: null,
    currentPage: 1,
    pageSize: 25
};

const CLUSTER_COLORS = {
    "3": "#3b82f6",
    "4": "#f97316",
    "2": "#10b981",
    "1": "#ef4444",
    "0": "#8b5cf6",
    "-1": "#94a3b8"
};

function formatIDR(val) {
    if (!val && val !== 0) return "IDR 0";
    if (val >= 1e12) return `IDR ${(val / 1e12).toFixed(2)} Triliun`;
    if (val >= 1e9) return `IDR ${(val / 1e9).toFixed(2)} Miliar`;
    if (val >= 1e6) return `IDR ${(val / 1e6).toFixed(1)} Juta`;
    return `IDR ${Math.round(val).toLocaleString("id-ID")}`;
}

// ─── INITIALIZATION ───
document.addEventListener("DOMContentLoaded", () => {
    initEvents();
    loadApplicationData();
});

function initEvents() {
    const btnRefresh = document.getElementById("btn-refresh");
    if (btnRefresh) btnRefresh.addEventListener("click", loadApplicationData);

    ["filter-region", "filter-type", "filter-cluster", "filter-tier"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("change", applyFilters);
    });

    const resetBtn = document.getElementById("btn-reset-filters");
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            ["filter-region", "filter-type", "filter-cluster", "filter-tier"].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = "all";
            });
            applyFilters();
        });
    }

    const searchInput = document.getElementById("table-search");
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            state.currentPage = 1;
            renderTable();
        });
    }

    const btnPrev = document.getElementById("btn-prev-page");
    if (btnPrev) {
        btnPrev.addEventListener("click", () => {
            if (state.currentPage > 1) {
                state.currentPage--;
                renderTable();
            }
        });
    }

    const btnNext = document.getElementById("btn-next-page");
    if (btnNext) {
        btnNext.addEventListener("click", () => {
            const total = getTableData().length;
            if (state.currentPage * state.pageSize < total) {
                state.currentPage++;
                renderTable();
            }
        });
    }

    const btnExport = document.getElementById("btn-export-csv");
    if (btnExport) btnExport.addEventListener("click", exportCSV);
}

// ─── DATA LOADING ───
async function loadApplicationData() {
    try {
        const [resSummary, resDcs, resOutlets] = await Promise.all([
            fetch("/api/summary").then(r => r.json()),
            fetch("/api/dcs").then(r => r.json()),
            fetch("/api/outlets").then(r => r.json())
        ]);

        state.summary = resSummary;
        state.dcs = resDcs;
        state.allOutlets = resOutlets?.outlets || [];
        state.filteredOutlets = [...state.allOutlets];

        updateKPIs();
        initLeafletMap();
        applyFilters();
    } catch (err) {
        console.error("Failed to load application data:", err);
    }
}

// ─── KPI UPDATE ───
function updateKPIs() {
    if (!state.summary?.metrics) return;
    const m = state.summary.metrics;

    setText("kpi-revenue", formatIDR(m.total_revenue_idr));
    setText("kpi-outlets", `${m.total_outlets.toLocaleString()} Toko`);
    setText("kpi-stockout", `${m.avg_stockout_rate_pct}%`);
    setText("kpi-otd", `${m.on_time_delivery_rate_pct}%`);
    setText("kpi-delay", `Rata-rata delay: ${m.avg_delay_mins} mnt`);
    setText("kpi-priority-count", `${m.high_priority_count} Toko`);
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}

// ─── LEAFLET MAP ───
function initLeafletMap() {
    if (state.leafletMap || typeof L === "undefined") return;

    const el = document.getElementById("leaflet-map");
    if (!el) return;

    state.leafletMap = L.map("leaflet-map", {
        zoomControl: true,
        attributionControl: false
    }).setView([-2.5489, 118.0149], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 12,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(state.leafletMap);

    state.leafletMarkersLayer = L.layerGroup().addTo(state.leafletMap);
    state.leafletDcsLayer = L.layerGroup().addTo(state.leafletMap);

    renderDCMarkers();
    renderOutletMarkers(state.filteredOutlets);

    setTimeout(() => {
        if (state.leafletMap) {
            state.leafletMap.invalidateSize();
            if (state.filteredOutlets.length > 0) {
                const bounds = L.latLngBounds(state.filteredOutlets.map(o => [o.Latitude, o.Longitude]));
                //state.leafletMap.fitBounds(bounds, { padding: [15, 15], maxZoom: 11 });
            }
        }
    }, 150);
}

function renderDCMarkers() {
    if (!state.leafletDcsLayer || typeof L === "undefined") return;
    state.leafletDcsLayer.clearLayers();

    state.dcs.forEach(dc => {
        const icon = L.divIcon({
            className: "dc-custom-marker",
            html: `<div style="
                background:#dc2626;
                width:24px;height:24px;
                border-radius:50%;
                border:3px solid #ffffff;
                box-shadow:0 2px 8px rgba(0,0,0,0.35);
                display:flex;align-items:center;justify-content:center;
            "><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="9" y1="10" x2="9" y2="14"/><line x1="15" y1="10" x2="15" y2="14"/></svg></div>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });

        const marker = L.marker([dc.Latitude, dc.Longitude], { icon });
        marker.bindPopup(`
            <div class="popup-card">
                <h4>${dc.DC_Name}</h4>
                <div class="popup-row"><span>Kode DC:</span><strong>${dc.Distribution_Center_ID}</strong></div>
                <div class="popup-row"><span>Kota/Wilayah:</span><strong>${dc.City}</strong></div>
                <div class="popup-row"><span>Kapasitas Harian:</span><strong>${Number(dc.Daily_Capacity_Cartons).toLocaleString()} Karton</strong></div>
                <div class="popup-row"><span>Armada Truk:</span><strong>${dc.Fleet_Size} Unit</strong></div>
            </div>
        `);
        marker.addTo(state.leafletDcsLayer);
    });
}

function renderOutletMarkers(outlets) {
    if (!state.leafletMarkersLayer || typeof L === "undefined") return;
    state.leafletMarkersLayer.clearLayers();

    outlets.forEach(out => {
        const cid = String(out.Primary_Cluster);
        const isUrgent = out.Distribution_Priority_Score >= 65;

        let color = CLUSTER_COLORS[cid] || "#3b82f6";
        let radius = 4;
        let fillOpacity = 0.75;

        if (isUrgent) {
            color = "#dc2626";
            radius = 6;
            fillOpacity = 0.95;
        } else if (cid === "-1") {
            color = "#94a3b8";
            radius = 3.5;
            fillOpacity = 0.5;
        }

        const circle = L.circleMarker([out.Latitude, out.Longitude], {
            radius,
            color: isUrgent ? "#ffffff" : color,
            weight: isUrgent ? 1.5 : 0.6,
            fillColor: color,
            fillOpacity
        });

        circle.bindPopup(buildOutletPopup(out), { maxWidth: 280 });
        circle.addTo(state.leafletMarkersLayer);
    });
}

function buildOutletPopup(out) {
    const isHighStockout = out.Stockout_Rate_Pct > 25;
    return `
        <div class="popup-card">
            <h4>${out.Outlet_Name}</h4>
            <div class="popup-row"><span>ID Outlet:</span><strong>${out.Outlet_ID}</strong></div>
            <div class="popup-row"><span>Tipe:</span><strong>${out.Outlet_Type}</strong></div>
            <div class="popup-row"><span>Wilayah:</span><strong>${out.Region}</strong></div>
            <div class="popup-row"><span>Klaster Bisnis:</span><strong>${out.Business_Cluster_Name || out.Cluster_Name}</strong></div>
            <div class="popup-row"><span>Omzet 90 Hari:</span><strong>${formatIDR(out.Total_Revenue_IDR)}</strong></div>
            <div class="popup-row"><span>Tingkat Stockout:</span><strong style="color:${isHighStockout ? '#dc2626' : '#059669'}">${out.Stockout_Rate_Pct.toFixed(1)}%</strong></div>
            <div class="popup-row"><span>Rata Delay:</span><strong>${out.Avg_Delivery_Delay_Mins.toFixed(1)} mnt</strong></div>
            <div class="popup-row"><span>Jarak ke DC:</span><strong>${out.Distance_to_Assigned_DC_KM.toFixed(1)} km</strong></div>
            <div class="popup-row"><span>Skor Bahaya:</span><strong style="color:#b91c1c">${out.Distribution_Priority_Score}</strong></div>
            <div class="popup-action">${out.Action_Recommendation}</div>
        </div>
    `;
}

function flyToOutlet(outletId) {
    const out = state.filteredOutlets.find(o => o.Outlet_ID === outletId);
    if (!out || !state.leafletMap) return;
    state.leafletMap.setView([out.Latitude, out.Longitude], 14, { animate: true });

    state.leafletMarkersLayer.eachLayer(layer => {
        if (layer.getLatLng) {
            const ll = layer.getLatLng();
            if (Math.abs(ll.lat - out.Latitude) < 0.0001 && Math.abs(ll.lng - out.Longitude) < 0.0001) {
                layer.openPopup();
            }
        }
    });
}
window.flyToOutlet = flyToOutlet;

// ─── FILTERS ───
function applyFilters() {
    const region = getVal("filter-region");
    const type = getVal("filter-type");
    const cluster = getVal("filter-cluster");
    const tier = getVal("filter-tier");

    state.filteredOutlets = state.allOutlets.filter(out => {
        if (region !== "all" && out.Region !== region) return false;
        if (type !== "all" && out.Outlet_Type !== type) return false;
        if (cluster !== "all" && String(out.Primary_Cluster) !== cluster) return false;
        if (tier === "high" && out.Distribution_Priority_Score < 65) return false;
        if (tier === "medium" && (out.Distribution_Priority_Score < 45 || out.Distribution_Priority_Score >= 65)) return false;
        if (tier === "noise" && out.Primary_Cluster !== -1) return false;
        return true;
    });

    renderOutletMarkers(state.filteredOutlets);
    updateFilterSummary();
    renderPriorityList();
    state.currentPage = 1;
    renderTable();
}

function getVal(id) {
    const el = document.getElementById(id);
    return el ? el.value : "all";
}

function updateFilterSummary() {
    const count = state.filteredOutlets.length;
    const rev = state.filteredOutlets.reduce((sum, o) => sum + (o.Total_Revenue_IDR || 0), 0);
    const avgDelay = count > 0
        ? (state.filteredOutlets.reduce((sum, o) => sum + (o.Avg_Delivery_Delay_Mins || 0), 0) / count).toFixed(1)
        : "0";

    setText("filtered-count", `${count.toLocaleString()}`);
    setText("filtered-revenue", formatIDR(rev));
    setText("filtered-delay", `${avgDelay} mnt`);
}

// ─── PRIORITY RANKING LIST (MOST TO LEAST DANGEROUS) ───
function renderPriorityList() {
    const container = document.getElementById("priority-list");
    const countBadge = document.getElementById("priority-list-count");
    if (!container) return;

    // Sort descending by danger priority score
    const sorted = [...state.filteredOutlets]
        .sort((a, b) => b.Distribution_Priority_Score - a.Distribution_Priority_Score);

    if (countBadge) countBadge.innerText = `${sorted.length} Toko`;

    if (sorted.length === 0) {
        container.innerHTML = `<div style="text-align:center;padding:24px;color:#94a3b8;font-size:11px;">Tidak ada outlet sesuai kriteria.</div>`;
        return;
    }

    container.innerHTML = sorted.slice(0, 60).map((out, i) => {
        const score = out.Distribution_Priority_Score;
        let scoreClass = "score-low";
        if (score >= 65) scoreClass = "score-crit";
        else if (score >= 45) scoreClass = "score-med";

        return `
            <div class="priority-row" onclick="flyToOutlet('${out.Outlet_ID}')">
                <span class="priority-badge-rank">#${i + 1}</span>
                <div class="priority-content">
                    <span class="priority-store-name">${out.Outlet_Name}</span>
                    <span class="priority-store-meta">${out.Region} · ${out.Outlet_Type} · Stockout ${out.Stockout_Rate_Pct.toFixed(1)}%</span>
                </div>
                <span class="priority-danger-score ${scoreClass}" title="Skor Bahaya Distribusi">${score}</span>
            </div>
        `;
    }).join("");
}

// ─── DATA TABLE ───
function getTableData() {
    const query = (document.getElementById("table-search")?.value || "").toLowerCase().trim();

    return state.filteredOutlets.filter(out => {
        if (query) {
            const match = [out.Outlet_Name, out.Outlet_ID, out.Region, out.Business_Cluster_Name || ""]
                .some(field => field.toLowerCase().includes(query));
            if (!match) return false;
        }
        return true;
    });
}

function renderTable() {
    const data = getTableData();
    const tbody = document.getElementById("table-body");
    if (!tbody) return;

    const start = (state.currentPage - 1) * state.pageSize;
    const page = data.slice(start, start + state.pageSize);

    if (page.length === 0) {
        tbody.innerHTML = `<tr><td colspan="12" style="text-align:center;padding:28px;color:#94a3b8;">Tidak ada data outlet yang cocok dengan pencarian filter.</td></tr>`;
        setText("pagination-info", "0 outlet");
        return;
    }

    tbody.innerHTML = page.map(out => {
        let badgeClass = "quad-q4", badgeLabel = "K4: Rutin";
        if (out.Quadrant === "Q1") { badgeClass = "quad-q1"; badgeLabel = "K1: Kritis"; }
        else if (out.Quadrant === "Q2") { badgeClass = "quad-q2"; badgeLabel = "K2: Stabil"; }
        else if (out.Quadrant === "Q3") { badgeClass = "quad-q3"; badgeLabel = "K3: Evaluasi"; }

        const stockoutColor = out.Stockout_Rate_Pct > 25 ? "#dc2626" : "#059669";

        return `<tr style="cursor:pointer;" onclick="flyToOutlet('${out.Outlet_ID}')">
            <td><code style="font-family:var(--font-mono);font-size:11px;color:#2563eb;">${out.Outlet_ID}</code></td>
            <td><strong>${out.Outlet_Name}</strong></td>
            <td>${out.Outlet_Type}</td>
            <td>${out.Region}</td>
            <td style="font-size:11px;color:#475569;">${out.Business_Cluster_Name || out.Cluster_Name}</td>
            <td><strong>${formatIDR(out.Total_Revenue_IDR)}</strong></td>
            <td style="color:${stockoutColor};font-weight:700;">${out.Stockout_Rate_Pct.toFixed(1)}%</td>
            <td>${out.Avg_Delivery_Delay_Mins.toFixed(1)} mnt</td>
            <td>${out.Distance_to_Assigned_DC_KM.toFixed(1)} km</td>
            <td><span style="font-family:var(--font-mono);font-weight:800;font-size:12px;">${out.Distribution_Priority_Score}</span></td>
            <td><span class="badge-quad ${badgeClass}">${badgeLabel}</span></td>
            <td style="font-size:11px;color:#334155;max-width:200px;">${out.Action_Recommendation}</td>
        </tr>`;
    }).join("");

    const total = data.length;
    const end = Math.min(start + state.pageSize, total);
    setText("pagination-info", `Menampilkan ${start + 1}–${end} dari ${total.toLocaleString()} outlet`);
    setText("page-num", `Hal. ${state.currentPage}`);

    const btnPrev = document.getElementById("btn-prev-page");
    const btnNext = document.getElementById("btn-next-page");
    if (btnPrev) btnPrev.disabled = state.currentPage === 1;
    if (btnNext) btnNext.disabled = end >= total;
}

function exportCSV() {
    const data = getTableData();
    if (data.length === 0) return;

    const headers = [
        "Outlet_ID", "Nama_Toko", "Tipe", "Wilayah", "Cluster",
        "Omzet_IDR", "Stockout_Pct", "Avg_Delay_Mnt", "Jarak_DC_KM",
        "Skor_Bahaya", "Kuadran", "Rekomendasi"
    ];

    let csv = headers.join(",") + "\n";
    data.forEach(r => {
        csv += [
            `"${r.Outlet_ID}"`, `"${r.Outlet_Name}"`, `"${r.Outlet_Type}"`, `"${r.Region}"`,
            `"${r.Business_Cluster_Name || r.Cluster_Name}"`, r.Total_Revenue_IDR,
            r.Stockout_Rate_Pct, r.Avg_Delivery_Delay_Mins, r.Distance_to_Assigned_DC_KM,
            r.Distribution_Priority_Score, `"${r.Quadrant}"`, `"${r.Action_Recommendation}"`
        ].join(",") + "\n";
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `fmcg_outlet_priorities_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
