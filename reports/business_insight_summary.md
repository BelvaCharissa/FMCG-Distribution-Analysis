# FMCG Supply Chain & Distribution Intelligence: Business Insight Report

**Target Industry:** Fast-Moving Consumer Goods (FMCG)  
**Author:** Data Analyst / Project Lead  
**Scope:** Greater Jakarta & Outskirts Distribution Network (1,250 Outlets, 3 Distribution Centers)  
**Methodology:** Haversine DBSCAN/HDBSCAN Geospatial Clustering + Multivariate Priority Scoring  

---

## 1. Executive Summary

Jaringan distribusi FMCG Jabodetabek mencakup 1,250 outlet aktif yang dilayani oleh 3 Distribution Center (DC Ciracas, DC Cikarang, dan DC Bitung). Evaluasi operasional selama 90 hari terakhir mencatat total omzet **IDR 112.68 Miliar**, namun terhambat oleh **Stockout Rate jaringan sebesar 22.59%** dan **rata-rata keterlambatan pengiriman 38.1 menit** (On-Time Delivery rate hanya 60.8%).

Melalui integrasi data transaksi, logistik, dan audit stok menggunakan algoritma **HDBSCAN (Hierarchical Density-Based Spatial Clustering)** dengan metrik Haversine (radian), jaringan outlet berhasil dipetakan ke dalam 6 klaster spasial utama dan 1 kelompok outlet terisolasi (*noise fringe*, 146 outlet).

Paling krusial, proyek ini mentransformasikan hasil klaster spasial menjadi **Distribution Priority Score (0 - 100)** berbasis 4 pilar: Permintaan (35%), Stockout Rate (30%), Keterlambatan Pengiriman (20%), dan Jarak ke DC (15%). Hasilnya mengidentifikasi **9 outlet berisiko kritis (Priority 1 - Urgent Action)** yang terkonsentrasi di Klaster 01 dan titik-titik pinggiran terpencil.

---

## 2. Key Analytical Findings

### Finding 1: Konsentrasi Pendapatan vs Kerentanan Layanan
- **Klaster 03 (Jakarta Urban Core)** menyumbang **58.62% dari total pendapatan** (IDR 66.06 Miliar) dengan 716 outlet. Klaster ini relatif stabil dengan rata-rata keterlambatan 38.1 menit dan jarak rata-rata ke DC 13.98 km.
- **Klaster 01 (Fringe Peripheral Corridor)** memiliki **tingkat stockout tertinggi (35.49%)** dan **rata-rata keterlambatan terparah (87.8 menit)**, dengan jarak rata-rata ke DC mencapai 36.0 km. Klaster ini menampung 6 dari 9 outlet berstatus paling darurat di seluruh jaringan.

| Cluster ID | Nama Klaster | Jumlah Outlet | Total Omzet (IDR) | Share Omzet | Stockout Rate (%) | Avg Delay (Mnt) | Jarak ke DC (KM) | Outlet Prioritas Tinggi |
|---|---|---|---|---|---|---|---|---|
| **Cluster 03** | Core Urban Jakarta | 716 | 66.06 M | 58.6% | 21.78% | 38.1 | 13.98 | 0 |
| **Cluster 04** | West Corridor (Tangerang) | 221 | 17.77 M | 15.8% | 23.15% | 39.7 | 9.37 | 0 |
| **Cluster -1** | Noise / Isolated Fringe | 146 | 12.52 M | 11.1% | 24.09% | 50.2 | 20.32 | 2 |
| **Cluster 02** | East Corridor (Bekasi) | 119 | 10.89 M | 9.7% | 21.85% | 36.7 | 11.50 | 1 |
| **Cluster 01** | Sub-Regional South/Far East | 27 | 2.84 M | 2.5% | **35.49%** | **87.8** | **36.01** | **6** |
| **Cluster 00** | South-West Secondary | 21 | 2.61 M | 2.3% | 21.83% | 44.9 | 19.81 | 0 |

### Finding 2: Perbandingan Algoritma: Mengapa HDBSCAN Lebih Unggul dari DBSCAN?
- **DBSCAN Standar (`eps = 4.5 km`, `min_samples = 12`)** hanya mendeteksi 3 klaster besar karena mengasumsikan kepadatan seragam (*homogeneous density*). Area pinggiran dengan kepadatan sedang terpaksa digabung secara paksa ke dalam klaster utama.
- **HDBSCAN (`min_cluster_size = 15`, `min_samples = 8`)** berhasil mengekstrak 6 klaster hirarkis yang mencerminkan topografi kepadatan sebenarnya: memisahkan koridor padat perkotaan dari koridor sub-regional dan mengisolasi 146 titik pinggiran (*noise points*).

### Finding 3: Dilema Outlet Terisolasi (Noise / Outliers)
- Terdapat **146 outlet (11.7% jaringan)** yang secara geografis berada di luar klaster kepadatan tinggi (tersebar di pelosok Bogor Selatan dan batas barat Banten).
- Meskipun hanya menyumbang 11.1% pendapatan, melayani outlet-outlet ini secara reguler dengan armada sendiri (*dedicated fleet*) menyebabkan pemborosan biaya pengiriman per karton (*Delivery Distance per Volume* tinggi) dan keterlambatan rata-rata 50.2 menit.

---

## 3. Actionable Supply Chain Recommendations

### Rekomendasi 1: Intervensi Khusus untuk Klaster 01 (Buffer Stock & Delivery Slot Adjustment)
- **Tindakan:** Mengubah frekuensi pengiriman ke 27 outlet di Klaster 01 dari pengiriman pesanan kecil harian (*frequent small orders*) menjadi pengiriman konsolidasi 2x seminggu dengan peningkatan safety stock (*buffer stock*) sebesar +25%.
- **Dampak yang Diharapkan:** Menekan frekuensi perjalanan jarak jauh (36 km), mengurangi stockout rate dari 35.5% ke level target < 20%, serta menghemat jam tempuh armada.

### Rekomendasi 2: Skema Distribusi Kemitraan (3PL / Wholesaler Hub) untuk 146 Outlet Terisolasi
- **Tindakan:** Jangan memaksakan rute armada mandiri ke 146 outlet *noise/isolated*. Manfaatkan kemitraan dengan Agen Grosir Lokal (*Wholesaler Key Account*) atau penyedia logistik pihak ketiga (3PL) berbasis konsolidasi mingguan.
- **Dampak yang Diharapkan:** Membebaskan kapasitas armada internal di DC Ciracas dan DC Bitung untuk fokus melayani Klaster 03 dan 04 yang menyumbang 74% pendapatan.

### Rekomendasi 3: Penataan Ulang Batas Wilayah Layanan DC (*Re-Zoning Boundary*)
- Analisis jarak menunjukkan beberapa outlet di perbatasan timur Jakarta dan barat Bekasi saat ini dilayani oleh DC yang lebih jauh karena batas administratif, bukan jarak rute aktual. Penyesuaian *assignment* outlet ke DC terdekat berdasarkan koordinat Haversine dapat memangkas estimasi jarak tempuh kumulatif hingga 12%.

---

## 4. Evaluasi & Metrik Keberhasilan Portfolio (Interview Talking Points)

Saat mendiskusikan proyek ini dalam wawancara Data Analyst FMCG:

1. **Bukan Sekadar Model Klasifikasi / Akurasi Kosong:**  
   Tekankan bahwa DBSCAN/HDBSCAN adalah algoritma *unsupervised*. Keberhasilannya tidak diukur dengan "akurasi > 90%", melainkan dari relevansi segmentasi operasional, rasio *noise* yang masuk akal (~11.7%), dan interpretasi bisnis klaster.
2. **Menghubungkan Analitik ke Eksekusi Bisnis:**  
   Soroti bagaimana *Distribution Priority Score* menggabungkan data permintaan, logistik, dan persediaan menjadi satu angka yang dapat langsung disortir oleh Logistics Planner setiap pagi.
3. **Peta Interaktif Sebagai Alat Kolaborasi:**  
   Buka file `reports/interactive_distribution_map.html` untuk mendemonstrasikan visualisasi spasial interaktif kepada pewawancara.
