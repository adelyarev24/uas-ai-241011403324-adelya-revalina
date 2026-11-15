# UAS Kecerdasan Buatan - Robot Gudang: Pencarian Rute Cerdas

**Kategori:** B. Intelligent Search
**Mata kuliah:** Kecerdasan Buatan, Universitas Pamulang (Fakultas Ilmu Komputer)
**Nama:** Adelya Revalina
**NIM:** 241011403324
**Kelas:** 05TPLP013
**Dosen pengampu:** HARDIANSYAH S.Kom., M.M., M.Kom.
**Tahun akademik:** 2026

## Deskripsi

Robot gudang harus berpindah dari titik awal **S** ke titik tujuan **G** pada denah berbentuk grid yang berisi
dinding/rak dan area berat (misalnya lantai licin atau padat). Aplikasi mencari rute berbiaya terkecil, menampilkan
proses penalarannya langkah demi langkah, dan membandingkan beberapa algoritma pencarian pada denah yang sama.

Algoritma yang diimplementasikan sendiri (tanpa pustaka pencarian jadi, tanpa API AI):

| Algoritma | Prioritas node | Optimal terhadap biaya? |
|---|---|---|
| A* (utama) | f(n) = g(n) + h(n) | Ya, jika heuristik admissible |
| BFS | FIFO | Hanya untuk jumlah langkah |
| Greedy Best-First | f(n) = h(n) | Tidak |
| Dijkstra (UCS) | f(n) = g(n) | Ya |

Fitur: peta 10x10 sampai 30x30, sel berbiaya berbeda, mode gerak 4 arah / 8 arah, heuristik Manhattan / Euclidean /
Octile, log ekspansi node (g, h, f), slider simulasi langkah demi langkah, perbandingan algoritma, validasi input,
peta acak, dan 7 skenario uji.

## Struktur berkas

| Berkas | Isi |
|---|---|
| `pencarian.py` | Modul inti AI: grid, algoritma, heuristik, parsing dan validasi peta |
| `skenario.py` | 7 skenario uji beserta hasil yang dihitung manual |
| `uji_skenario.py` | Menjalankan skenario dan menulis `hasil_pengujian.md` |
| `test_pencarian.py` | Unit test (kebenaran jalur, optimalitas A* vs Dijkstra, validasi input) |
| `app.py` | Antarmuka Streamlit |
| `requirements.txt` | Dependensi |

## Cara menjalankan

Butuh Python 3.10 atau lebih baru.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Aplikasi terbuka di browser (biasanya http://localhost:8501).

### Menjalankan pengujian

```bash
python test_pencarian.py     # unit test
python uji_skenario.py       # tabel skenario -> hasil_pengujian.md (untuk Bab IV laporan)
```

## Format peta

```
S.........      S = awal          . = lantai bebas (biaya 1)
~~~~~~~...      G = tujuan        ~ = area berat (biaya 3)
.....#....                        # = dinding
.........G
```

Setiap baris harus sama panjang; ukuran minimal 10x10, maksimal 30x30; tepat satu `S` dan satu `G`.

## Penggunaan AI generatif

Proyek ini dikerjakan dengan bantuan Claude (Anthropic) sebagai alat bantu untuk menyusun kerangka kode
(`pencarian.py`, `app.py`, skenario dan skrip pengujian), serta draf laporan. Seluruh kode ditinjau, dijalankan, dan
dapat dijelaskan oleh pemilik proyek. Pernyataan lengkap ada pada laporan (Bab IV).

## Catatan

Aplikasi ini merupakan prototipe akademik, bukan sistem navigasi robot sungguhan.
