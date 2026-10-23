# PRODUCT REQUIREMENTS DOCUMENT (PRD)

## Geospatial Analytics for FMCG Supply Chain & Distribution Optimization

**Project Type:** End-to-End Data Analytics Project  
**Role:** Data Analyst / Project Lead  
**Target Industry:** Fast-Moving Consumer Goods (FMCG)  
**Target Users:** Supply Chain Manager, Logistics Coordinator, Distribution Planner  
**Technology Stack:** SQL, Python, Pandas, Scikit-learn, HDBSCAN, Power BI  
**Project Status:** Active / Portfolio Project  
**Data Source:** Synthetic FMCG sales and distribution dataset  

---

## 1. Executive Summary

Perusahaan FMCG mengelola distribusi produk ke ribuan outlet dengan karakteristik permintaan, lokasi geografis, dan kebutuhan pengiriman yang berbeda-beda. Dalam kondisi tertentu, distribusi yang tidak mempertimbangkan pola permintaan dan persebaran outlet dapat meningkatkan biaya logistik, memperpanjang waktu pengiriman, serta meningkatkan risiko stockout di tingkat outlet.

Proyek ini bertujuan membangun solusi analitik berbasis data untuk mengidentifikasi pola persebaran outlet, memetakan konsentrasi permintaan, dan mengevaluasi kinerja distribusi berdasarkan lokasi geografis.

Dengan mengintegrasikan data penjualan, koordinat outlet, riwayat pengiriman, dan frekuensi stockout, proyek ini menggunakan algoritma DBSCAN/HDBSCAN untuk mengidentifikasi klaster geografis serta outlet yang berada di luar area dengan kepadatan tinggi (*noise/outliers*). Hasil analisis kemudian disajikan melalui dashboard interaktif Power BI untuk membantu tim Supply Chain menentukan prioritas distribusi, mengidentifikasi area berisiko, dan mengevaluasi peluang peningkatan efisiensi operasional.

Proyek ini berfokus pada **decision support berbasis data**, bukan pengoptimalan rute secara otomatis. Hasil klastering digunakan sebagai dasar untuk menyusun rekomendasi distribusi yang dapat dievaluasi lebih lanjut menggunakan data operasional aktual.

---

## 2. Problem Statement

Distribusi FMCG menghadapi beberapa tantangan yang saling berkaitan:

1. **Ketimpangan distribusi geografis:** Outlet terkonsentrasi di wilayah tertentu, sementara outlet lain tersebar jauh dari pusat distribusi (*isolated outlets*).
2. **Permintaan yang bervariasi:** Outlet dengan volume penjualan tinggi membutuhkan pengisian stok yang lebih konsisten dibandingkan outlet dengan permintaan rendah.
3. **Risiko stockout yang tidak merata:** Beberapa outlet mengalami stockout berulang meskipun memiliki permintaan yang tinggi (*lost sales opportunity*).
4. **Keterbatasan visibilitas operasional:** Data penjualan, pengiriman, dan persediaan yang terpisah menyulitkan tim untuk mengidentifikasi area yang membutuhkan perhatian.
5. **Prioritas distribusi yang belum berbasis kombinasi indikator:** Kedekatan geografis saja tidak cukup untuk menentukan outlet yang perlu diprioritaskan karena tingkat permintaan dan risiko stockout juga harus dipertimbangkan.

### Core Business Question
> **Bagaimana perusahaan FMCG dapat memanfaatkan data geografis, permintaan, dan kinerja pengiriman untuk mengidentifikasi prioritas distribusi serta meningkatkan efisiensi operasional?**

---

## 3. Business Objectives

### 3.1 Primary Objectives
- **A. Mengidentifikasi pola distribusi outlet:**
  - Mengelompokkan outlet berdasarkan kepadatan geografis menggunakan Haversine distance.
  - Mengidentifikasi area dengan konsentrasi outlet dan permintaan tinggi.
  - Menemukan outlet yang secara geografis terisolasi dari kelompok outlet lainnya (*outliers/noise*).
- **B. Mengidentifikasi area dengan risiko stockout tinggi:**
  - Mengukur frekuensi stockout berdasarkan wilayah, klaster, dan tipe outlet.
  - Mengidentifikasi area dengan permintaan tinggi tetapi kinerja pemenuhan stok buruk.
  - Menentukan outlet prioritas untuk evaluasi distribusi.
- **C. Mengevaluasi efisiensi distribusi:**
  - Menganalisis hubungan antara karakteristik geografis, waktu pengiriman, dan permintaan.
  - Mengidentifikasi wilayah dengan waktu pengiriman dan keterlambatan yang relatif tinggi.
  - Menghasilkan rekomendasi pengelompokan area layanan dan prioritas distribusi.

### 3.2 Secondary Objectives
- Menyediakan dashboard terpusat untuk memantau performa distribusi.
- Membantu evaluasi kebutuhan kapasitas dan cakupan layanan pusat distribusi (DC).
- Menyediakan dasar analitis untuk pengembangan model prediksi stockout atau optimasi rute pada tahap selanjutnya.

---

## 4. Target Users & User Needs

### Persona 1 — Supply Chain Manager
- **Tujuan:** Mengevaluasi kinerja distribusi secara keseluruhan dan menentukan prioritas perbaikan jaringan logistik.
- **Kebutuhan:**
  - Melihat distribusi outlet dan konsentrasi permintaan per wilayah.
  - Membandingkan tingkat stockout dan keterlambatan antarwilayah.
  - Mengidentifikasi klaster dengan kontribusi omzet terbesar vs service level terendah.
  - Dashboard eksekutif berbasis indikator ringkas (OTIF, Stockout Rate, Priority Score).
- **Expected Outcome:** Keputusan strategis mengenai evaluasi jaringan distribusi dan alokasi armada didukung data empiris.

### Persona 2 — Logistics Coordinator & Distribution Planner
- **Tujuan:** Menentukan outlet dan wilayah yang membutuhkan perhatian harian/mingguan dalam perencanaan pengiriman.
- **Kebutuhan:**
  - Daftar outlet berisiko tinggi (*High Priority*).
  - Mengidentifikasi outlet terpencil dan wilayah dengan waktu pengiriman tinggi.
  - Memfilter data berdasarkan wilayah, tipe outlet, dan klaster.
- **Expected Outcome:** Penjadwalan pengiriman yang lebih terarah dan mitigasi stockout pada outlet kunci.

---

## 5. Proposed Solution

1. **Data Integration & Preparation (ETL):** Menggabungkan data outlet, penjualan, pengiriman, dan observasi stockout.
2. **Geospatial Clustering & Priority Scoring:**
   - Memodelkan kepadatan outlet dengan DBSCAN & HDBSCAN (metrik Haversine).
   - Menghitung **Distribution Priority Score (0-100)** berbasis kombinasi 4 pilar: Permintaan, Tingkat Stockout, Keterlambatan Pengiriman, dan Jarak ke DC.
3. **Interactive Distribution Intelligence Dashboard:** Power BI dashboard 5 halaman untuk operasional dan manajemen.

---

## 6. Functional Requirements

| ID | Requirement | Description | Priority |
|---|---|---|---|
| FR-01 | Data Integration | Menggabungkan data outlet, penjualan, pengiriman, dan stockout | Must Have |
| FR-02 | Data Validation | Memvalidasi koordinat, duplikasi, missing values, dan konsistensi data | Must Have |
| FR-03 | Geospatial Clustering | Menghasilkan label klaster menggunakan DBSCAN/HDBSCAN | Must Have |
| FR-04 | Demand Analysis | Menghitung volume permintaan dan kontribusi setiap klaster | Must Have |
| FR-05 | Stockout Analysis | Mengukur frekuensi dan tingkat stockout per outlet dan wilayah | Must Have |
| FR-06 | Delivery Performance | Mengevaluasi waktu pengiriman, delay, dan SLA pengiriman | Must Have |
| FR-07 | Interactive Map | Menampilkan persebaran outlet, klaster, dan outlet terpencil | Must Have |
| FR-08 | Outlet Prioritization | Menghitung Distribution Priority Score & kualifikasi urgensi | Must Have |
| FR-09 | Dynamic Filtering | Menyediakan filter periode, wilayah, tipe outlet, dan klaster | Must Have |
| FR-10 | Recommendation Summary | Menampilkan insight dan rekomendasi berbasis hasil analisis | Should Have |
| FR-11 | Scenario Comparison | Simulasi skenario pengelompokan layanan vs kondisi aktual | Future Enhancement |

---

## 7. Data Requirements & Schema

### 7.1 Raw Datasets
1. `outlets_raw.csv` (1,200+ outlets di Jabodetabek & sekitarnya)
2. `products_raw.csv` (Master data produk FMCG)
3. `sales_raw.csv` (Transaksi penjualan 90 hari terakhir)
4. `deliveries_raw.csv` (Riwayat pengiriman & SLA logistik)
5. `inventory_stockouts_raw.csv` (Log audit persediaan & stockout harian/mingguan)

### 7.2 Derived Metrics
- `Stockout_Rate_Pct` = (Jumlah Observasi Stockout / Total Observasi) * 100
- `Avg_Delivery_Delay_Mins` = Rata-rata selisih Actual Delivery Time vs Planned Delivery Time
- `Demand_Contribution_Pct` = (Demand Outlet / Total Demand Jaringan) * 100
- `Distance_to_DC_KM` = Jarak Haversine dari outlet ke DC induk
- `Distribution_Priority_Score` = Pembobotan multivariat (Demand, Stockout, Delay, Distance)

---

## 8. Portfolio Roadmap & Phased Execution

| Tahap | Fokus | Output |
|---|---|---|
| **Phase 1** | Raw Data Generation & ETL | Dataset mentah, skrip pembersihan, skema SQL |
| **Phase 2** | Geospatial Modeling & Scoring | Model DBSCAN/HDBSCAN, Haversine clustering, priority score |
| **Phase 3** | Analytics & Business Insights | Executive summary report, visualisasi peta interaktif |
| **Phase 4** | Power BI Dashboard Ready | Dataset teragregasi siap import, panduan data model Power BI |
