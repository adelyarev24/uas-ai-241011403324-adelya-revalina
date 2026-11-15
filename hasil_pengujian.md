# Hasil Pengujian Skenario

## Tabel skenario uji

| Kode | Skenario | Input (S -> G, mode) | Hasil diharapkan | Hasil aktual (A*) | Status | Analisis |
|---|---|---|---|---|---|---|
| S1 | Grid kosong | S(0, 0) -> G(9, 9), 4 arah | Jalur ditemukan, biaya 18.00 | Jalur ditemukan, biaya 18.00, 18 langkah | Sesuai | A* memperluas 19 node vs Dijkstra 100 |
| S2 | Dinding dengan celah di bawah | S(0, 0) -> G(0, 9), 4 arah | Jalur ditemukan, biaya 27.00 | Jalur ditemukan, biaya 27.00, 27 langkah | Sesuai | A* memperluas 60 node vs Dijkstra 91 |
| S3 | Area berat (biaya berbeda) | S(0, 0) -> G(9, 0), 4 arah | Jalur ditemukan, biaya 23.00 | Jalur ditemukan, biaya 23.00, 23 langkah | Sesuai | BFS biaya 25.00 (tidak optimal); Greedy biaya 25.00 (tidak optimal); A* memperluas 52 node vs Dijkstra 96 |
| S4 | Labirin berkelok (serpentine) | S(0, 0) -> G(9, 9), 4 arah | Jalur ditemukan, biaya 54.00 | Jalur ditemukan, biaya 54.00, 54 langkah | Sesuai | A* memperluas 55 node vs Dijkstra 55 |
| S5 | Tujuan terkurung (tanpa jalur) | S(0, 0) -> G(9, 9), 4 arah | Tidak ada jalur | Tidak ada jalur, 97 node disapu | Sesuai | Semua algoritma berhenti dan melapor tanpa error. |
| S6 | Gerak diagonal (8 arah) | S(0, 0) -> G(9, 9), 8 arah | Jalur ditemukan, biaya 12.73 | Jalur ditemukan, biaya 12.73, 9 langkah | Sesuai | A* memperluas 10 node vs Dijkstra 100 |
| S7 | Perangkap berbentuk U | S(4, 0) -> G(4, 9), 4 arah | Jalur ditemukan, biaya 15.00 | Jalur ditemukan, biaya 15.00, 15 langkah | Sesuai | A* memperluas 35 node vs Dijkstra 89 |

## Perbandingan algoritma per skenario

| Kode | Algoritma | Ditemukan | Langkah | Biaya | Node diperluas | Frontier maks | Waktu (ms) |
|---|---|---|---|---|---|---|---|
| S1 | A* (manhattan) | Ya | 18 | 18.00 | 19 | 17 | 0.227 |
| S1 | BFS | Ya | 18 | 18.00 | 100 | 10 | 0.852 |
| S1 | Greedy Best-First (manhattan) | Ya | 18 | 18.00 | 19 | 17 | 0.178 |
| S1 | Dijkstra (UCS) | Ya | 18 | 18.00 | 100 | 10 | 0.686 |
| S2 | A* (manhattan) | Ya | 27 | 27.00 | 60 | 15 | 0.471 |
| S2 | BFS | Ya | 27 | 27.00 | 91 | 6 | 0.431 |
| S2 | Greedy Best-First (manhattan) | Ya | 27 | 27.00 | 54 | 15 | 0.409 |
| S2 | Dijkstra (UCS) | Ya | 27 | 27.00 | 91 | 6 | 0.640 |
| S3 | A* (manhattan) | Ya | 23 | 23.00 | 52 | 42 | 0.471 |
| S3 | BFS | Ya | 9 | 25.00 | 46 | 10 | 0.219 |
| S3 | Greedy Best-First (manhattan) | Ya | 9 | 25.00 | 10 | 10 | 0.085 |
| S3 | Dijkstra (UCS) | Ya | 23 | 23.00 | 96 | 14 | 0.956 |
| S4 | A* (manhattan) | Ya | 54 | 54.00 | 55 | 1 | 0.423 |
| S4 | BFS | Ya | 54 | 54.00 | 55 | 1 | 0.279 |
| S4 | Greedy Best-First (manhattan) | Ya | 54 | 54.00 | 55 | 1 | 0.395 |
| S4 | Dijkstra (UCS) | Ya | 54 | 54.00 | 55 | 1 | 0.372 |
| S5 | A* (manhattan) | Tidak | - | - | 97 | 70 | 1.039 |
| S5 | BFS | Tidak | - | - | 97 | 10 | 0.573 |
| S5 | Greedy Best-First (manhattan) | Tidak | - | - | 97 | 17 | 0.827 |
| S5 | Dijkstra (UCS) | Tidak | - | - | 97 | 10 | 0.780 |
| S6 | A* (octile) | Ya | 9 | 12.73 | 10 | 35 | 0.378 |
| S6 | BFS | Ya | 9 | 12.73 | 100 | 19 | 1.331 |
| S6 | Greedy Best-First (octile) | Ya | 9 | 12.73 | 10 | 35 | 0.310 |
| S6 | Dijkstra (UCS) | Ya | 9 | 12.73 | 100 | 23 | 1.787 |
| S7 | A* (manhattan) | Ya | 15 | 15.00 | 35 | 17 | 0.327 |
| S7 | BFS | Ya | 15 | 15.00 | 89 | 10 | 0.410 |
| S7 | Greedy Best-First (manhattan) | Ya | 15 | 15.00 | 33 | 17 | 0.302 |
| S7 | Dijkstra (UCS) | Ya | 15 | 15.00 | 89 | 10 | 0.589 |
