"""
Unit test modul pencarian. Jalankan dengan:  python test_pencarian.py   (atau: pytest)
"""
import math
import random

from pencarian import (BEBAS, DINDING, Grid, GridError, a_star, bfs, dijkstra,
                       greedy_best_first, jalankan_semua, parse_peta)

PETA_KOSONG = "\n".join(["S........."] + [".........."] * 8 + [".........G"])


def test_astar_grid_kosong():
    g, s, t = parse_peta(PETA_KOSONG)
    h = a_star(g, s, t)
    assert h.ditemukan and h.langkah == 18 and math.isclose(h.biaya, 18)


def test_jalur_valid_tidak_menembus_dinding():
    g, s, t = parse_peta(PETA_KOSONG.replace("..........", "....#.....", 3))
    for h in jalankan_semua(g, s, t):
        if h.ditemukan:
            assert h.jalur[0] == s and h.jalur[-1] == t
            assert all(g.bisa_dilewati(p) for p in h.jalur)
            for a, b in zip(h.jalur, h.jalur[1:]):
                assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1  # mode 4 arah


def test_astar_sama_optimal_dengan_dijkstra_pada_peta_acak():
    rnd = random.Random(42)
    for _ in range(200):
        sel = [[DINDING if rnd.random() < 0.25 else (2 if rnd.random() < 0.2 else BEBAS)
                for _ in range(12)] for _ in range(12)]
        sel[0][0] = BEBAS
        sel[11][11] = BEBAS
        g = Grid(sel)
        for diag, heur in ((False, "manhattan"), (False, "euclidean"), (True, "octile")):
            a = a_star(g, (0, 0), (11, 11), heur, diag)
            d = dijkstra(g, (0, 0), (11, 11), diag)
            assert a.ditemukan == d.ditemukan
            if a.ditemukan:
                assert math.isclose(a.biaya, d.biaya, abs_tol=1e-9), (heur, diag)


def test_bfs_langkah_minimum():
    g, s, t = parse_peta(PETA_KOSONG)
    assert bfs(g, s, t).langkah == 18


def test_astar_lebih_efisien_dari_dijkstra():
    g, s, t = parse_peta(PETA_KOSONG)
    assert a_star(g, s, t).node_diperluas <= dijkstra(g, s, t).node_diperluas


def test_tanpa_jalur():
    peta = PETA_KOSONG.replace(".........G", "........#G").replace(
        "..........", ".........#", 1).splitlines()
    peta = ["S........."] + [".........."] * 7 + [".........#", "........#G"]
    g, s, t = parse_peta("\n".join(peta))
    for h in jalankan_semua(g, s, t):
        assert not h.ditemukan and h.node_diperluas == 97


def test_greedy_bisa_tidak_optimal_tapi_valid():
    from skenario import SKENARIO
    sk = next(x for x in SKENARIO if x.kode == "S7")
    g, s, t = parse_peta(sk.peta)
    gr = greedy_best_first(g, s, t)
    assert gr.ditemukan and gr.biaya >= a_star(g, s, t).biaya


def _harus_error(fungsi, *args):
    try:
        fungsi(*args)
    except GridError:
        return
    raise AssertionError("GridError seharusnya muncul")


def test_validasi_input():
    _harus_error(parse_peta, "")
    _harus_error(parse_peta, "S.\n.G")  # terlalu kecil
    _harus_error(parse_peta, PETA_KOSONG.replace("S", "."))  # tanpa S
    _harus_error(parse_peta, PETA_KOSONG.replace("G", "."))  # tanpa G
    _harus_error(parse_peta, PETA_KOSONG.replace("S.", "SS", 1))  # dua S
    _harus_error(parse_peta, PETA_KOSONG.replace("..........", "...?......", 1))  # karakter asing
    _harus_error(parse_peta, PETA_KOSONG + "\n....")  # baris tidak sama panjang


def test_titik_di_dinding_ditolak():
    g, _, _ = parse_peta(PETA_KOSONG)
    g.sel[0][1] = DINDING
    _harus_error(a_star, g, (0, 1), (9, 9))
    _harus_error(a_star, g, (0, 0), (20, 20))


if __name__ == "__main__":
    daftar = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    for nama, fungsi in daftar:
        fungsi()
        print(f"LULUS  {nama}")
    print(f"\n{len(daftar)} tes lulus.")
