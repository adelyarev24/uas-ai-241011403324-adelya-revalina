"""
Menjalankan semua skenario uji dan menulis tabel hasil ke hasil_pengujian.md
(tabel ini bisa langsung disalin ke Bab IV laporan).

Fungsi evaluasi_skenario() juga dipakai oleh aplikasi (tab "Pengujian Skenario").

Cara pakai:  python uji_skenario.py
"""
import math
from dataclasses import dataclass

from pencarian import Hasil, jalankan_semua, parse_peta
from skenario import SKENARIO, Skenario


def sama(a: float, b: float) -> bool:
    return math.isclose(a, b, abs_tol=1e-6)


@dataclass
class Evaluasi:
    skenario: Skenario
    start: tuple
    goal: tuple
    hasil: list[Hasil]      # urutan: A*, BFS, Greedy, Dijkstra
    input_teks: str
    diharapkan: str
    aktual: str
    sesuai: bool
    analisis: str


def evaluasi_skenario(s: Skenario) -> Evaluasi:
    """Jalankan satu skenario pada semua algoritma, lalu bandingkan dengan hasil yang diharapkan."""
    grid, start, goal = parse_peta(s.peta)
    hasil = jalankan_semua(grid, start, goal, s.diagonal)
    astar, bfs_h, greedy_h, dijk = hasil
    mode = "8 arah" if s.diagonal else "4 arah"

    if s.diharapkan_ditemukan:
        diharapkan = f"Jalur ditemukan, biaya {s.diharapkan_biaya:.2f}"
        aktual = (f"Jalur {'ditemukan' if astar.ditemukan else 'TIDAK ditemukan'}, "
                  f"biaya {astar.biaya:.2f}, {astar.langkah} langkah")
        ok = astar.ditemukan and sama(astar.biaya, s.diharapkan_biaya) and sama(astar.biaya, dijk.biaya)

        catatan = []
        if not sama(bfs_h.biaya, astar.biaya):
            catatan.append(f"BFS biaya {bfs_h.biaya:.2f} (tidak optimal)")
        if not sama(greedy_h.biaya, astar.biaya):
            catatan.append(f"Greedy biaya {greedy_h.biaya:.2f} (tidak optimal)")
        catatan.append(f"A* memperluas {astar.node_diperluas} node vs Dijkstra {dijk.node_diperluas}")
        analisis = "; ".join(catatan)
    else:
        diharapkan = "Tidak ada jalur"
        aktual = f"{'Jalur ditemukan' if astar.ditemukan else 'Tidak ada jalur'}, {astar.node_diperluas} node disapu"
        ok = (not astar.ditemukan) and all(not h.ditemukan for h in hasil)
        analisis = "Semua algoritma berhenti dan melapor tanpa error."

    return Evaluasi(s, start, goal, hasil, f"S{start} -> G{goal}, {mode}", diharapkan, aktual, ok, analisis)


def main() -> int:
    baris_utama = [
        "| Kode | Skenario | Input (S -> G, mode) | Hasil diharapkan | Hasil aktual (A*) | Status | Analisis |",
        "|---|---|---|---|---|---|---|",
    ]
    baris_banding = [
        "| Kode | Algoritma | Ditemukan | Langkah | Biaya | Node diperluas | Frontier maks | Waktu (ms) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    gagal = 0

    for s in SKENARIO:
        e = evaluasi_skenario(s)
        gagal += 0 if e.sesuai else 1
        status = "Sesuai" if e.sesuai else "TIDAK sesuai"
        baris_utama.append(
            f"| {s.kode} | {s.nama} | {e.input_teks} | {e.diharapkan} | {e.aktual} | {status} | {e.analisis} |"
        )
        for h in e.hasil:
            baris_banding.append(
                f"| {s.kode} | {h.algoritma} | {'Ya' if h.ditemukan else 'Tidak'} | "
                f"{h.langkah if h.ditemukan else '-'} | {f'{h.biaya:.2f}' if h.ditemukan else '-'} | "
                f"{h.node_diperluas} | {h.frontier_maks} | {h.waktu_ms:.3f} |"
            )

    isi = ("# Hasil Pengujian Skenario\n\n## Tabel skenario uji\n\n" + "\n".join(baris_utama) +
           "\n\n## Perbandingan algoritma per skenario\n\n" + "\n".join(baris_banding) + "\n")
    with open("hasil_pengujian.md", "w", encoding="utf-8") as f:
        f.write(isi)

    print(isi)
    print(f"Ringkasan: {len(SKENARIO) - gagal}/{len(SKENARIO)} skenario sesuai.")
    return 1 if gagal else 0


if __name__ == "__main__":
    raise SystemExit(main())
