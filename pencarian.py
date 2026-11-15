"""
Modul inti AI: algoritma pencarian (Intelligent Search) pada grid.

Studi kasus : Robot gudang mencari rute dari titik awal (S) ke titik tujuan (G).
Algoritma   : A* (utama), serta BFS, Greedy Best-First, dan Dijkstra sebagai pembanding.

Representasi:
  - Grid berisi sel dengan jenis: BEBAS (biaya 1), DINDING (tidak bisa dilewati),
    BERAT (biaya 3, misalnya area licin / padat rak).
  - Biaya langkah = biaya sel yang DIMASUKI. Langkah diagonal dikali sqrt(2).
"""
from __future__ import annotations

import heapq
import math
import time
from collections import deque
from dataclasses import dataclass, field

# ---------------------------------------------------------------- konstanta
BEBAS, DINDING, BERAT = 0, 1, 2
BIAYA_SEL = {BEBAS: 1.0, BERAT: 3.0}
BIAYA_MIN = 1.0  # biaya sel termurah, dipakai agar heuristik tetap admissible

SIMBOL = {".": BEBAS, "#": DINDING, "~": BERAT}

ARAH_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
ARAH_DIAGONAL = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

Posisi = tuple[int, int]  # (baris, kolom)


# ---------------------------------------------------------------- struktur data
class GridError(ValueError):
    """Kesalahan input peta / titik awal-tujuan."""


@dataclass
class Grid:
    sel: list[list[int]]

    @property
    def baris(self) -> int:
        return len(self.sel)

    @property
    def kolom(self) -> int:
        return len(self.sel[0])

    def di_dalam(self, p: Posisi) -> bool:
        return 0 <= p[0] < self.baris and 0 <= p[1] < self.kolom

    def bisa_dilewati(self, p: Posisi) -> bool:
        return self.di_dalam(p) and self.sel[p[0]][p[1]] != DINDING

    def biaya_masuk(self, p: Posisi) -> float:
        return BIAYA_SEL[self.sel[p[0]][p[1]]]

    def tetangga(self, p: Posisi, diagonal: bool = False):
        """Menghasilkan (posisi_tetangga, biaya_langkah)."""
        for dr, dc in ARAH_4:
            q = (p[0] + dr, p[1] + dc)
            if self.bisa_dilewati(q):
                yield q, self.biaya_masuk(q)
        if diagonal:
            for dr, dc in ARAH_DIAGONAL:
                q = (p[0] + dr, p[1] + dc)
                if not self.bisa_dilewati(q):
                    continue
                # larang "memotong sudut" di antara dua dinding
                if not (self.bisa_dilewati((p[0] + dr, p[1])) and self.bisa_dilewati((p[0], p[1] + dc))):
                    continue
                yield q, self.biaya_masuk(q) * math.sqrt(2)


@dataclass
class LangkahLog:
    """Satu langkah ekspansi node, untuk penjelasan proses AI."""
    urutan: int
    node: Posisi
    g: float
    h: float
    f: float
    ukuran_frontier: int


@dataclass
class Hasil:
    algoritma: str
    ditemukan: bool
    jalur: list[Posisi] = field(default_factory=list)
    biaya: float = 0.0          # total biaya sebenarnya sepanjang jalur
    langkah: int = 0            # jumlah langkah (panjang jalur - 1)
    node_diperluas: int = 0     # jumlah node yang di-expand
    frontier_maks: int = 0      # ukuran maksimum antrean
    waktu_ms: float = 0.0
    urutan_kunjungan: list[Posisi] = field(default_factory=list)
    log: list[LangkahLog] = field(default_factory=list)


# ---------------------------------------------------------------- parsing & validasi
def parse_peta(teks: str) -> tuple[Grid, Posisi, Posisi]:
    """
    Ubah teks peta menjadi (Grid, start, goal) sekaligus memvalidasi.
    Simbol: '.' bebas, '#' dinding, '~' area berat, 'S' awal, 'G' tujuan.
    """
    baris_teks = [b.strip() for b in teks.strip().splitlines() if b.strip()]
    if not baris_teks:
        raise GridError("Peta kosong.")
    lebar = len(baris_teks[0])
    if any(len(b) != lebar for b in baris_teks):
        raise GridError("Semua baris peta harus sama panjang.")
    if len(baris_teks) < 10 or lebar < 10:
        raise GridError(f"Ukuran peta minimal 10 x 10 (sekarang {len(baris_teks)} x {lebar}).")
    if len(baris_teks) > 30 or lebar > 30:
        raise GridError("Ukuran peta maksimal 30 x 30.")

    sel, start, goal = [], None, None
    for r, b in enumerate(baris_teks):
        baris = []
        for c, ch in enumerate(b):
            if ch == "S":
                if start is not None:
                    raise GridError("Titik awal 'S' hanya boleh satu.")
                start = (r, c)
                baris.append(BEBAS)
            elif ch == "G":
                if goal is not None:
                    raise GridError("Titik tujuan 'G' hanya boleh satu.")
                goal = (r, c)
                baris.append(BEBAS)
            elif ch in SIMBOL:
                baris.append(SIMBOL[ch])
            else:
                raise GridError(f"Karakter tidak dikenal '{ch}' di baris {r + 1}, kolom {c + 1}. "
                                "Gunakan . # ~ S G")
        sel.append(baris)
    if start is None:
        raise GridError("Titik awal 'S' belum ada.")
    if goal is None:
        raise GridError("Titik tujuan 'G' belum ada.")
    if start == goal:
        raise GridError("Titik awal dan tujuan tidak boleh sama.")
    return Grid(sel), start, goal


def validasi_titik(grid: Grid, start: Posisi, goal: Posisi) -> None:
    for nama, p in (("awal", start), ("tujuan", goal)):
        if not grid.di_dalam(p):
            raise GridError(f"Titik {nama} {p} berada di luar peta.")
        if not grid.bisa_dilewati(p):
            raise GridError(f"Titik {nama} {p} berada pada dinding.")
    if start == goal:
        raise GridError("Titik awal dan tujuan tidak boleh sama.")


# ---------------------------------------------------------------- heuristik
def heuristik(nama: str, a: Posisi, b: Posisi) -> float:
    dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
    if nama == "manhattan":
        return (dr + dc) * BIAYA_MIN
    if nama == "euclidean":
        return math.hypot(dr, dc) * BIAYA_MIN
    if nama == "octile":
        return (max(dr, dc) + (math.sqrt(2) - 1) * min(dr, dc)) * BIAYA_MIN
    if nama == "nol":
        return 0.0
    raise ValueError(f"Heuristik tidak dikenal: {nama}")


HEURISTIK_TERSEDIA = ["manhattan", "euclidean", "octile", "nol"]


# ---------------------------------------------------------------- pembantu
def _rekonstruksi(induk: dict, goal: Posisi) -> list[Posisi]:
    jalur = [goal]
    while induk[jalur[-1]] is not None:
        jalur.append(induk[jalur[-1]])
    jalur.reverse()
    return jalur


def _hitung_biaya(grid: Grid, jalur: list[Posisi]) -> float:
    total = 0.0
    for a, b in zip(jalur, jalur[1:]):
        langkah = grid.biaya_masuk(b)
        if a[0] != b[0] and a[1] != b[1]:
            langkah *= math.sqrt(2)
        total += langkah
    return total


# ---------------------------------------------------------------- algoritma best-first umum
def _best_first(grid: Grid, start: Posisi, goal: Posisi, mode: str,
                nama_heuristik: str, diagonal: bool, nama_tampil: str) -> Hasil:
    """
    Satu kerangka untuk tiga algoritma berbasis antrean prioritas:
      mode 'astar'    -> f(n) = g(n) + h(n)
      mode 'greedy'   -> f(n) = h(n)
      mode 'dijkstra' -> f(n) = g(n)
    """
    validasi_titik(grid, start, goal)
    t0 = time.perf_counter()

    def h(p: Posisi) -> float:
        return heuristik(nama_heuristik, p, goal)

    def prioritas(g: float, p: Posisi) -> float:
        if mode == "astar":
            return g + h(p)
        if mode == "greedy":
            return h(p)
        return g  # dijkstra

    cacah = 0  # pemecah seri agar urutan deterministik
    # Isi antrean: (prioritas, h, urutan, node). Saat f sama, pilih node dengan h lebih kecil
    # (lebih dekat ke tujuan) sebagai pemecah seri, agar A* tidak menyapu area yang tak perlu.
    frontier = [(prioritas(0.0, start), h(start), cacah, start)]
    g_terbaik = {start: 0.0}
    induk: dict[Posisi, Posisi | None] = {start: None}
    tertutup: set[Posisi] = set()
    hasil = Hasil(algoritma=nama_tampil, ditemukan=False)
    hasil.frontier_maks = 1

    while frontier:
        f, _, _, node = heapq.heappop(frontier)
        if node in tertutup:
            continue  # entri usang
        tertutup.add(node)
        g = g_terbaik[node]
        hasil.urutan_kunjungan.append(node)
        hasil.log.append(LangkahLog(len(hasil.urutan_kunjungan), node, g, h(node), f, len(frontier)))

        if node == goal:
            hasil.ditemukan = True
            hasil.jalur = _rekonstruksi(induk, goal)
            break

        for tetangga, biaya in grid.tetangga(node, diagonal):
            if tetangga in tertutup:
                continue
            g_baru = g + biaya
            if mode == "greedy":
                # Greedy hanya menandai node sekali (tanpa memperbaiki g)
                if tetangga in g_terbaik:
                    continue
            elif g_baru >= g_terbaik.get(tetangga, math.inf):
                continue
            g_terbaik[tetangga] = g_baru
            induk[tetangga] = node
            cacah += 1
            heapq.heappush(frontier, (prioritas(g_baru, tetangga), h(tetangga), cacah, tetangga))
        hasil.frontier_maks = max(hasil.frontier_maks, len(frontier))

    return _selesaikan(grid, hasil, t0)


def _selesaikan(grid: Grid, hasil: Hasil, t0: float) -> Hasil:
    hasil.waktu_ms = (time.perf_counter() - t0) * 1000
    hasil.node_diperluas = len(hasil.urutan_kunjungan)
    if hasil.ditemukan:
        hasil.langkah = len(hasil.jalur) - 1
        hasil.biaya = _hitung_biaya(grid, hasil.jalur)
    return hasil


# ---------------------------------------------------------------- antarmuka algoritma
def a_star(grid: Grid, start: Posisi, goal: Posisi, nama_heuristik: str = "manhattan",
           diagonal: bool = False) -> Hasil:
    return _best_first(grid, start, goal, "astar", nama_heuristik, diagonal,
                       f"A* ({nama_heuristik})")


def greedy_best_first(grid: Grid, start: Posisi, goal: Posisi, nama_heuristik: str = "manhattan",
                      diagonal: bool = False) -> Hasil:
    return _best_first(grid, start, goal, "greedy", nama_heuristik, diagonal,
                       f"Greedy Best-First ({nama_heuristik})")


def dijkstra(grid: Grid, start: Posisi, goal: Posisi, diagonal: bool = False) -> Hasil:
    return _best_first(grid, start, goal, "dijkstra", "nol", diagonal, "Dijkstra (UCS)")


def bfs(grid: Grid, start: Posisi, goal: Posisi, diagonal: bool = False) -> Hasil:
    """BFS: menjamin langkah paling sedikit, tetapi mengabaikan biaya sel."""
    validasi_titik(grid, start, goal)
    t0 = time.perf_counter()
    antrean = deque([start])
    induk: dict[Posisi, Posisi | None] = {start: None}
    hasil = Hasil(algoritma="BFS", ditemukan=False)
    hasil.frontier_maks = 1

    while antrean:
        node = antrean.popleft()
        hasil.urutan_kunjungan.append(node)
        hasil.log.append(LangkahLog(len(hasil.urutan_kunjungan), node, 0.0, 0.0, 0.0, len(antrean)))
        if node == goal:
            hasil.ditemukan = True
            hasil.jalur = _rekonstruksi(induk, goal)
            break
        for tetangga, _ in grid.tetangga(node, diagonal):
            if tetangga not in induk:
                induk[tetangga] = node
                antrean.append(tetangga)
        hasil.frontier_maks = max(hasil.frontier_maks, len(antrean))

    return _selesaikan(grid, hasil, t0)


def jalankan_semua(grid: Grid, start: Posisi, goal: Posisi, diagonal: bool = False) -> list[Hasil]:
    """Jalankan semua algoritma pada konfigurasi yang sama untuk perbandingan."""
    h = "octile" if diagonal else "manhattan"
    return [
        a_star(grid, start, goal, h, diagonal),
        bfs(grid, start, goal, diagonal),
        greedy_best_first(grid, start, goal, h, diagonal),
        dijkstra(grid, start, goal, diagonal),
    ]
