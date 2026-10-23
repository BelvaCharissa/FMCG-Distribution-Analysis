# Sistem Analisis Distribusi & Rantai Pasok FMCG

Aplikasi web pendukung keputusan (*decision support tool*) berbasis data geospasial dan kinerja rantai pasok untuk industri FMCG (*Fast-Moving Consumer Goods*).

Aplikasi ini menghubungkan data transaksi penjualan, pemenuhan pengiriman logistik, audit ketersediaan persediaan (*stockout*), dan koordinat geospasial untuk mengevaluasi jaringan distribusi di wilayah Jabodetabek (1.250 outlet dan 3 Distribution Center).

---

## 🚀 Menjalankan Aplikasi di Lokal

Aplikasi web dapat langsung diakses melalui browser:

👉 **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

Jika Anda ingin menjalankan ulang server dari terminal PowerShell:
```powershell
# Masuk ke direktori proyek
cd "c:\Users\Belva\Documents\Project FMCG"

# Jalankan server aplikasi
python -u app.py
```

---

## 🗺️ Konfigurasi Peta (Google Maps Platform & OpenStreetMap Fallback)

Aplikasi dirancang dengan arsitektur **Dual-Engine Map**:
- **Default & Fallback:** Menggunakan OpenStreetMap (Leaflet.js) yang dapat berjalan langsung secara lokal tanpa memerlukan API key maupun billing account.
- **Google Maps Platform:** Jika Anda memiliki Google Maps JavaScript API Key, Anda dapat memasangnya tanpa perlu mengubah kode sumber:

### Cara Memasang Google Maps API Key:
Set environment variable di terminal sebelum menjalankan `app.py`:
```powershell
# Set API Key di sesi PowerShell
$env:GOOGLE_MAPS_API_KEY = "YOUR_ACTUAL_GOOGLE_MAPS_API_KEY"

# Jalankan aplikasi
python -u app.py
```
> **Catatan Keamanan:** 
> - Jangan pernah melakukan *hardcode* API key di file frontend (`index.html` atau `app.js`).
> - Pada Google Cloud Console, disarankan untuk membatasi API Key menggunakan **HTTP Referrer restriction** (misal: `http://127.0.0.1:5050/*` atau domain produksi Anda) dan hanya mengizinkan **Maps JavaScript API**.
> - Jika API Key tidak diset atau kuota habis, aplikasi akan secara otomatis menggunakan OpenStreetMap sehingga dashboard tetap dapat digunakan secara normal.

---

## 📋 Fitur Utama Dashboard

### 1. 🗺️ Peta Persebaran Outlet
- Memetakan 1.250 outlet dan 3 Distribution Center (Ciracas, Cikarang, Bitung).
- Titik outlet diwarnai berdasarkan **Kelompok Kedekatan Wilayah** dan status urgensi (Merah untuk prioritas darurat, Abu-abu untuk outlet di luar kelompok utama).
- Klik pada marker toko untuk melihat pop-up: nama toko, omzet 90 hari, tingkat stockout, rata-rata keterlambatan, jarak ke DC, dan saran tindakan.
- Filter interaktif: Wilayah, Tipe Saluran Toko, Kelompok Wilayah, dan Tingkat Prioritas.

### 2. 📊 Diagnostik & Temuan Operasional
Menyajikan temuan berbasis 4 pertanyaan bisnis:
1. **Apa masalah yang ditemukan?**
2. **Di wilayah mana masalah terjadi?**
3. **Seberapa penting bagi operasional?**
4. **Apa tindakan yang disarankan?**

Tiga temuan utama yang didukung bukti data aktual:
- **Temuan 1:** Ketiadaan Stok Kritis di Wilayah Sub-Regional Selatan (Stockout 35,5%, keterlambatan 87,8 menit, jarak tempuh 36 km).
- **Temuan 2:** Beban Logistik Tinggi pada 146 Outlet Terpencil di Luar Kelompok Utama (Omzet 11,1%, delay 50,2 menit).
- **Temuan 3:** Ketimpangan Beban Layanan pada DC Ciracas (>58% volume jaringan).

### 3. 📋 Matriks Prioritas Outlet (2x2 Kuadran)
Memetakan outlet berdasarkan 2 indikator bisnis utama menggunakan nilai tengah (median) data aktual:
- **Kuadran 1 (Prioritas Utama - 245 Toko):** Permintaan Tinggi, Stockout Tinggi. *Risiko lost sales terbesar; memerlukan peninjauan stok pengaman dan jadwal pengiriman segera.*
- **Kuadran 2 (Pertahankan Pasokan - 380 Toko):** Permintaan Tinggi, Stockout Rendah. *Penopang omzet utama yang berjalan sehat; pertahankan jadwal rutin.*
- **Kuadran 3 (Evaluasi Pengiriman - 396 Toko):** Permintaan Rendah, Stockout Tinggi. *Evaluasi frekuensi pengiriman atau ukuran minimum pemesanan (MOQ).*
- **Kuadran 4 (Pemantauan Rutin - 229 Toko):** Permintaan Rendah, Stockout Rendah. *Kondisi stabil, pengawasan berkala.*

Klik salah satu kuadran untuk langsung memfilter tabel outlet di bawahnya. Tabel mendukung pencarian teks, paginasi, dan tombol **Ekspor CSV**.

### 4. ⚡ Simulasi Skenario (What-If Analysis)
- Memproyeksikan dampak penurunan keterlambatan pengiriman (%) dan penambahan stok pengaman (%) terhadap penurunan persentase stockout.
- Menyajikan perbandingan transparan antara **Kondisi Awal (Baseline)** vs **Hasil Proyeksi**.
- Menghitung estimasi omzet yang diselamatkan (*recovered revenue*) dan efisiensi bahan bakar armada.
