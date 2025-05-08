# Dashboard Analisis Harga Kalimantan Barat

## Ikhtisar
Dashboard ini memvisualisasikan dan menganalisis perubahan harga komoditas penting di berbagai kabupaten/kota di Kalimantan Barat, Indonesia. Dashboard ini memberikan wawasan tentang tren harga, disparitas, dan dampak komoditas tertentu terhadap perubahan harga secara keseluruhan.

## Rumus dan Metodologi

### 1. Indikator Perubahan Harga
Persentase perubahan harga dibandingkan dengan periode sebelumnya:

```
Indikator Perubahan Harga (%) = ((P₁ - P₀) / P₀) × 100
```
Dimana:
- P₁ = Harga periode saat ini
- P₀ = Harga periode sebelumnya

### 2. Andil Komoditas
Kontribusi komoditas tertentu terhadap perubahan harga secara keseluruhan:

```
Andil Komoditas = (w × (P₁ - P₀) / P₀) × 100
```
Dimana:
- w = Bobot komoditas dalam keranjang konsumsi
- P₁ = Harga komoditas periode saat ini
- P₀ = Harga komoditas periode sebelumnya

### 3. Disparitas Harga Antar Daerah
Perbedaan relatif harga antar daerah, dinyatakan dalam persentase:

```
Disparitas Harga = (P_max / P_min) × 100
```
Dimana:
- P_max = Harga maksimum keranjang komoditas di daerah
- P_min = Harga minimum keranjang komoditas yang sama di daerah

Nilai 100 menunjukkan tidak ada disparitas, sedangkan nilai di atas 100 menunjukkan disparitas yang lebih tinggi.

### 4. Analisis Tren
Untuk deret waktu dengan beberapa periode, regresi linier digunakan untuk menentukan tren harga:

```
y = mx + b
```
Dimana:
- y = Indikator perubahan harga
- x = Waktu (dalam hari)
- m = Kemiringan (arah dan besaran tren)
- b = Intersep

Arah tren ditentukan oleh tanda kemiringan (m):
- Kemiringan positif (m > 0): Tren naik (harga meningkat)
- Kemiringan negatif (m < 0): Tren turun (harga menurun)

### 5. Pengukuran Volatilitas
Standar deviasi digunakan untuk mengukur volatilitas harga:

```
σ = √(Σ(x - μ)² / n)
```
Dimana:
- σ = Standar deviasi
- x = Nilai perubahan harga individual
- μ = Rata-rata perubahan harga
- n = Jumlah observasi

## Sumber Data
Dashboard ini menggunakan data harga yang dikumpulkan oleh Badan Pusat Statistik (BPS) untuk provinsi Kalimantan Barat. Data mencakup pengamatan harga mingguan untuk komoditas penting di berbagai kabupaten/kota.

## Implementasi Teknis
Dashboard ini dibangun menggunakan:
- Streamlit untuk antarmuka web
- Pandas untuk manipulasi data
- Plotly untuk visualisasi interaktif
- NumPy untuk perhitungan numerik

## Cara Penggunaan
1. Pilih kabupaten/kota menggunakan filter di sidebar
2. Jelajahi berbagai visualisasi dan analisis
3. Pilih komoditas tertentu untuk menganalisis kontribusinya terhadap perubahan harga
4. Unduh data yang telah difilter sebagai CSV untuk analisis lebih lanjut
