"""
Aplikasi: Robot Gudang - Pencarian Rute Cerdas (UAS Kecerdasan Buatan, Kategori B: Intelligent Search)

Jalankan dengan:  streamlit run app.py
"""

import random

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch, Rectangle

from pencarian import (BERAT, DINDING, GridError, Hasil, a_star, bfs, dijkstra,
                       greedy_best_first, jalankan_semua, parse_peta)
from skenario import SKENARIO
from uji_skenario import evaluasi_skenario

st.set_page_config(page_title="Robot Gudang - Pencarian Rute", page_icon="🤖", layout="wide")

WARNA = {
    "bebas": "#FFFFFF", "dinding": "#2B2B2B", "berat": "#F4C27A",
    "dikunjungi": "#BFD7EA", "dikunjungi_berat": "#D9C7A3",
    "awal": "#1E88E5", "tujuan": "#E53935", "jalur": "#1B8A3A", "sekarang": "#FF9800",
}
NAMA_ALGO = ["A*", "BFS", "Greedy Best-First", "Dijkstra"]


# ================================================================ fungsi bantu
def buat_peta_acak(ukuran: int, p_dinding: float, p_berat: float, seed: int) -> str:
    rnd = random.Random(seed)
    baris = []
    for r in range(ukuran):
        teks = ""
        for c in range(ukuran):
            x = rnd.random()
            teks += "#" if x < p_dinding else ("~" if x < p_dinding + p_berat else ".")
        baris.append(list(teks))
    baris[0][0] = "S"
    baris[-1][-1] = "G"
    return "\n".join("".join(b) for b in baris)


def muat_skenario(kode: str):
    s = next(x for x in SKENARIO if x.kode == kode)
    st.session_state["peta_teks"] = s.peta.strip()
    st.session_state["mode_gerak"] = "8 arah" if s.diagonal else "4 arah"


def callback_muat_dari_sidebar():
    muat_skenario(st.session_state["pilih_skenario"].split(" - ")[0])


def callback_peta_acak():
    st.session_state["peta_teks"] = buat_peta_acak(
        int(st.session_state["acak_ukuran"]), st.session_state["acak_dinding"],
        st.session_state["acak_berat"], int(st.session_state["acak_seed"]))


def jalankan(algo: str, grid, start, goal, diagonal: bool, heur: str) -> Hasil:
    if algo == "A*":
        return a_star(grid, start, goal, heur, diagonal)
    if algo == "BFS":
        return bfs(grid, start, goal, diagonal)
    if algo == "Greedy Best-First":
        return greedy_best_first(grid, start, goal, heur, diagonal)
    return dijkstra(grid, start, goal, diagonal)


def gambar(grid, start, goal, hasil: Hasil, k: int, ukuran=5.0):
    """Gambar grid: dinding, area berat, node yang sudah dikunjungi (sampai langkah k), dan jalur."""
    img = []
    for baris in grid.sel:
        img.append([to_rgb(WARNA["dinding"] if c == DINDING else WARNA["berat"] if c == BERAT else WARNA["bebas"])
                    for c in baris])
    dikunjungi = hasil.urutan_kunjungan[:k]
    for r, c in dikunjungi:
        img[r][c] = to_rgb(WARNA["dikunjungi_berat"] if grid.sel[r][c] == BERAT else WARNA["dikunjungi"])

    fig, ax = plt.subplots(figsize=(ukuran, ukuran))
    ax.imshow(img, interpolation="nearest")
    ax.set_xticks([x - 0.5 for x in range(grid.kolom + 1)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(grid.baris + 1)], minor=True)
    ax.grid(which="minor", color="#CCCCCC", linewidth=0.6)
    ax.tick_params(which="both", length=0)
    ax.set_xticks(range(grid.kolom))
    ax.set_yticks(range(grid.baris))
    ax.tick_params(labelsize=7)

    if hasil.ditemukan and k >= len(hasil.urutan_kunjungan):
        ax.plot([p[1] for p in hasil.jalur], [p[0] for p in hasil.jalur],
                color=WARNA["jalur"], linewidth=3, solid_capstyle="round", zorder=3)
    elif dikunjungi:
        r, c = dikunjungi[-1]
        ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False, edgecolor=WARNA["sekarang"], linewidth=2.5, zorder=4))

    for (r, c), warna, huruf in ((start, WARNA["awal"], "S"), (goal, WARNA["tujuan"], "G")):
        ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, color=warna, zorder=5))
        ax.text(c, r, huruf, ha="center", va="center", color="white", fontweight="bold", zorder=6)

    ax.legend(handles=[
        Patch(facecolor=WARNA["dinding"], label="Dinding"),
        Patch(facecolor=WARNA["berat"], label="Area berat (biaya 3)"),
        Patch(facecolor=WARNA["dikunjungi"], label="Sudah diperluas"),
        Patch(facecolor=WARNA["jalur"], label="Jalur"),
    ], loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=2, fontsize=7, frameon=False)
    fig.tight_layout()
    return fig


def tampilkan(fig):
    st.pyplot(fig)
    plt.close(fig)


def penjelasan_langkah(algo: str, hasil: Hasil, k: int) -> str:
    total = len(hasil.urutan_kunjungan)
    if k >= total:
        if hasil.ditemukan:
            return (f"**Selesai.** Node tujuan {hasil.jalur[-1]} dikeluarkan dari antrean. Jalur dibentuk mundur lewat "
                    f"penunjuk induk: **{hasil.langkah} langkah, biaya total {hasil.biaya:.2f}**.")
        return "**Selesai.** Antrean kosong dan tujuan tidak pernah tercapai, sehingga **tidak ada jalur**."
    lg = hasil.log[k - 1]
    if algo == "BFS":
        return (f"Langkah {lg.urutan}: node {lg.node} diambil dari **depan antrean (FIFO)**. Tetangga yang belum pernah "
                f"dikunjungi dimasukkan ke belakang antrean. Isi antrean: {lg.ukuran_frontier}.")
    rumus = {"A*": "f = g + h", "Greedy Best-First": "f = h", "Dijkstra": "f = g"}[algo]
    return (f"Langkah {lg.urutan}: node {lg.node} dipilih karena memiliki **{rumus}** terkecil di antrean "
            f"(g = {lg.g:.2f}, h = {lg.h:.2f}, f = {lg.f:.2f}). Isi antrean: {lg.ukuran_frontier}.")


# ================================================================ keadaan awal & sidebar
if "peta_teks" not in st.session_state:
    muat_skenario("S3")
    st.session_state["pilih_skenario"] = next(f"{s.kode} - {s.nama}" for s in SKENARIO if s.kode == "S3")

with st.sidebar:
    st.header("Pengaturan")
    st.selectbox("Skenario bawaan", [f"{s.kode} - {s.nama}" for s in SKENARIO], key="pilih_skenario")
    st.button("Muat skenario", on_click=callback_muat_dari_sidebar, use_container_width=True)

    st.divider()
    st.subheader("Peta acak")
    st.number_input("Ukuran (n x n)", 10, 30, 12, key="acak_ukuran")
    st.slider("Kepadatan dinding", 0.0, 0.45, 0.25, 0.05, key="acak_dinding")
    st.slider("Kepadatan area berat", 0.0, 0.40, 0.15, 0.05, key="acak_berat")
    st.number_input("Seed", 0, 99999, 1, key="acak_seed")
    st.button("Buat peta acak", on_click=callback_peta_acak, use_container_width=True)

    st.divider()
    st.subheader("Gerak & heuristik")
    mode = st.radio("Arah gerak", ["4 arah", "8 arah"], key="mode_gerak")
    diagonal = mode == "8 arah"
    opsi_heur = ["octile", "euclidean"] if diagonal else ["manhattan", "euclidean"]
    heur = st.selectbox("Heuristik (A* dan Greedy)", opsi_heur, key=f"heuristik_{mode}",
                        help="Heuristik dibatasi pada yang admissible untuk mode gerak terpilih.")

# ================================================================ halaman utama
st.title("🤖 Robot Gudang: Pencarian Rute Cerdas")
st.caption("UAS Kecerdasan Buatan - Kategori B: Intelligent Search (A*, BFS, Greedy Best-First, Dijkstra)")

tab_beranda, tab_sim, tab_banding, tab_uji = st.tabs(
    ["Beranda", "Simulasi", "Perbandingan", "Pengujian Skenario"])

# ---------------------------------------------------------------- beranda
with tab_beranda:
    st.subheader("Apa fungsi aplikasi ini?")
    st.write(
        "Sebuah robot gudang harus berpindah dari titik awal **S** ke titik tujuan **G** pada denah gudang berbentuk "
        "grid. Aplikasi mencari rute dengan **biaya terkecil** menggunakan algoritma pencarian AI, menampilkan proses "
        "penalarannya langkah demi langkah, dan membandingkan beberapa algoritma pada denah yang sama.")
    kiri, kanan = st.columns(2)
    with kiri:
        st.markdown("""
**Cara menggunakan**
1. Pilih **skenario bawaan** atau buat **peta acak** di panel kiri, lalu atur arah gerak dan heuristik.
2. Buka tab **Simulasi**: peta dapat diedit sebagai teks, pilih algoritma, lalu geser slider untuk melihat urutan
   node yang diperluas beserta nilai g, h, f.
3. Buka tab **Perbandingan** untuk melihat kinerja keempat algoritma pada peta yang sama.
4. Buka tab **Pengujian Skenario** untuk melihat 7 skenario uji dan kesesuaian hasilnya.
5. Ingin mengulang? Ubah peta/pengaturan atau tekan **Muat skenario** kembali.
""")
    with kanan:
        st.markdown("""
**Simbol peta**

| Simbol | Arti |
|---|---|
| `S` | Titik awal robot |
| `G` | Titik tujuan |
| `.` | Lantai bebas (biaya 1) |
| `~` | Area berat / licin (biaya 3) |
| `#` | Dinding / rak (tidak bisa dilewati) |

Ukuran peta 10x10 sampai 30x30. Biaya langkah = biaya sel yang dimasuki; langkah diagonal dikalikan akar 2.
""")
    st.subheader("Ringkasan metode")
    st.markdown("""
| Algoritma | Prioritas node | Menjamin biaya optimal? |
|---|---|---|
| **A\\*** | f(n) = g(n) + h(n) | Ya, bila heuristik admissible |
| **BFS** | Urutan masuk (FIFO) | Hanya optimal untuk jumlah langkah, mengabaikan biaya sel |
| **Greedy Best-First** | f(n) = h(n) | Tidak |
| **Dijkstra** | f(n) = g(n) | Ya, tetapi menyapu area lebih luas |
""")
    st.info("Aplikasi ini adalah prototipe akademik untuk pembelajaran, bukan sistem navigasi robot sungguhan.")

# ---------------------------------------------------------------- simulasi
peta_ok = False
with tab_sim:
    kol_peta, kol_hasil = st.columns([1, 1.3])
    with kol_peta:
        st.subheader("Peta & algoritma")
        teks_peta = st.text_area("Peta (bisa diedit)", key="peta_teks", height=300,
                                 help="Gunakan simbol: . # ~ S G. Setiap baris harus sama panjang.")
        algo = st.selectbox("Algoritma", NAMA_ALGO, key="algo_pilihan")
        try:
            grid, start, goal = parse_peta(teks_peta)
            peta_ok = True
        except GridError as e:
            st.error(f"Peta tidak valid: {e}")

    with kol_hasil:
        if peta_ok:
            hasil = jalankan(algo, grid, start, goal, diagonal, heur)
            total = len(hasil.urutan_kunjungan)
            st.subheader(f"Hasil: {hasil.algoritma}")

            if hasil.ditemukan:
                st.success("Jalur ditemukan.")
            else:
                st.warning("Tidak ada jalur dari S ke G pada peta ini.")

            m = st.columns(5)
            m[0].metric("Langkah", hasil.langkah if hasil.ditemukan else "-")
            m[1].metric("Biaya total", f"{hasil.biaya:.2f}" if hasil.ditemukan else "-")
            m[2].metric("Node diperluas", hasil.node_diperluas)
            m[3].metric("Frontier maks", hasil.frontier_maks)
            m[4].metric("Waktu (ms)", f"{hasil.waktu_ms:.2f}")

            kunci = f"langkah_{algo}_{mode}_{heur}_{hash(teks_peta)}"
            if total > 1:
                k = st.slider("Langkah simulasi (jumlah node yang sudah diperluas)", 1, total, total, key=kunci)
            else:
                k = total
            tampilkan(gambar(grid, start, goal, hasil, k))
            st.markdown(penjelasan_langkah(algo, hasil, k))

            with st.expander("Tabel log ekspansi node (baris, kolom dimulai dari 0)"):
                df_log = pd.DataFrame([{
                    "Urutan": lg.urutan, "Node": str(lg.node), "g": round(lg.g, 2), "h": round(lg.h, 2),
                    "f": round(lg.f, 2), "Isi antrean": lg.ukuran_frontier} for lg in hasil.log[:k]])
                if algo == "BFS":
                    df_log = df_log[["Urutan", "Node", "Isi antrean"]]
                st.dataframe(df_log, hide_index=True)
            if hasil.ditemukan:
                with st.expander("Jalur akhir"):
                    st.write(" -> ".join(str(p) for p in hasil.jalur))
        else:
            st.info("Perbaiki peta di sebelah kiri untuk menampilkan hasil.")

# ---------------------------------------------------------------- perbandingan
with tab_banding:
    if not peta_ok:
        st.info("Perbaiki peta pada tab Simulasi terlebih dahulu.")
    else:
        semua = jalankan_semua(grid, start, goal, diagonal)
        st.subheader("Perbandingan empat algoritma pada peta yang sama")
        df = pd.DataFrame([{
            "Algoritma": h.algoritma, "Ditemukan": "Ya" if h.ditemukan else "Tidak",
            "Langkah": h.langkah if h.ditemukan else None,
            "Biaya": round(h.biaya, 2) if h.ditemukan else None,
            "Node diperluas": h.node_diperluas, "Frontier maks": h.frontier_maks,
            "Waktu (ms)": round(h.waktu_ms, 3)} for h in semua])
        st.dataframe(df, hide_index=True)

        ditemukan = [h for h in semua if h.ditemukan]
        if ditemukan:
            biaya_min = min(h.biaya for h in ditemukan)
            optimal = [h.algoritma for h in ditemukan if abs(h.biaya - biaya_min) < 1e-6]
            paling_hemat = min(ditemukan, key=lambda h: h.node_diperluas)
            tidak_optimal = [h.algoritma for h in ditemukan if abs(h.biaya - biaya_min) >= 1e-6]
            st.markdown(
                f"- Biaya terkecil **{biaya_min:.2f}** dicapai oleh: {', '.join(optimal)}.\n"
                f"- Algoritma dengan node diperluas paling sedikit: **{paling_hemat.algoritma}** "
                f"({paling_hemat.node_diperluas} node).\n"
                + (f"- Tidak optimal pada peta ini: {', '.join(tidak_optimal)}." if tidak_optimal
                   else "- Semua algoritma menghasilkan biaya yang sama pada peta ini."))
        else:
            st.warning("Tidak ada algoritma yang menemukan jalur pada peta ini.")

        c1, c2 = st.columns(2)
        c1.caption("Node diperluas (lebih kecil = lebih efisien)")
        c1.bar_chart(df.set_index("Algoritma")[["Node diperluas"]])
        c2.caption("Biaya jalur (lebih kecil = lebih baik)")
        c2.bar_chart(df.set_index("Algoritma")[["Biaya"]])

        kolom = st.columns(4)
        for kol, h in zip(kolom, semua):
            with kol:
                st.caption(h.algoritma)
                tampilkan(gambar(grid, start, goal, h, len(h.urutan_kunjungan), ukuran=3.4))

# ---------------------------------------------------------------- pengujian
with tab_uji:
    st.subheader("Skenario pengujian")
    evaluasi = [evaluasi_skenario(s) for s in SKENARIO]
    lulus = sum(e.sesuai for e in evaluasi)
    st.write(f"**{lulus} dari {len(evaluasi)}** skenario sesuai dengan hasil yang diharapkan (dihitung manual).")
    st.dataframe(pd.DataFrame([{
        "Kode": e.skenario.kode, "Skenario": e.skenario.nama, "Input": e.input_teks,
        "Hasil diharapkan": e.diharapkan, "Hasil aktual (A*)": e.aktual,
        "Status": "Sesuai" if e.sesuai else "TIDAK sesuai", "Analisis": e.analisis} for e in evaluasi]),
        hide_index=True)

    for e in evaluasi:
        s = e.skenario
        with st.expander(f"{s.kode} - {s.nama}"):
            st.write(f"**Tujuan uji:** {s.tujuan}")
            st.write(f"**Perhitungan manual:** {s.perhitungan}")
            st.code(s.peta.strip(), language=None)
            st.dataframe(pd.DataFrame([{
                "Algoritma": h.algoritma, "Ditemukan": "Ya" if h.ditemukan else "Tidak",
                "Langkah": h.langkah if h.ditemukan else None,
                "Biaya": round(h.biaya, 2) if h.ditemukan else None,
                "Node diperluas": h.node_diperluas} for h in e.hasil]), hide_index=True)
            st.button("Muat ke simulasi", key=f"muat_{s.kode}", on_click=muat_skenario, args=(s.kode,))
