"""
app.py - Aplikasi web Flask: Prediksi Risiko Putus Kuliah Mahasiswa (Random Forest).

Model dan semua artefak dibuat oleh notebook (folder model/ dan static/charts/).
Aplikasi ini hanya memuat dan memakainya; tidak ada data pengguna yang disimpan.
"""
import json
import os
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

from labels import GROUPS, META

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"

app = Flask(__name__)


# ---------------------------------------------------------------- memuat model
def muat_json(nama, default=None):
    path = MODEL_DIR / nama
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if not (MODEL_DIR / "rf_model.joblib").exists():
    raise SystemExit("File model/rf_model.joblib belum ada. Jalankan notebook terlebih dahulu.")

MODEL = joblib.load(MODEL_DIR / "rf_model.joblib")
FITUR_INFO = muat_json("fitur.json")
FITUR = FITUR_INFO["fitur"]
REFERENSI = FITUR_INFO["referensi"]
LABEL_MAP = {int(k): v for k, v in muat_json("label_map.json").items()}
METRIK = muat_json("metrik.json", {})
IMPORTANCE = muat_json("feature_importance.json", {})
CONTOH = muat_json("contoh.json", {})

tidak_ada = [f for f in FITUR if f not in META]
if tidak_ada:
    raise SystemExit(f"labels.py belum memuat fitur: {tidak_ada}")

KUNCI = {f: f"f{i}" for i, f in enumerate(FITUR)}          # nama input HTML yang aman
IDX_DROPOUT = list(MODEL.classes_).index(
    next(k for k, v in LABEL_MAP.items() if v == "Dropout"))

NAMA_KELAS = {
    "Dropout": "Putus kuliah (dropout)",
    "Enrolled": "Masih menempuh studi (enrolled)",
    "Graduate": "Lulus tepat waktu (graduate)",
}
TEKS_RISIKO = {
    "rendah": {
        "judul": "Risiko putus kuliah rendah",
        "ringkas": "Berdasarkan data yang dimasukkan, pola mahasiswa ini lebih mirip mahasiswa yang melanjutkan studi atau lulus.",
        "saran": [
            "Pertahankan ritme belajar dan jumlah mata kuliah yang lulus tiap semester.",
            "Tetap pantau nilai dan tagihan kuliah agar tidak ada kejutan di semester berikutnya.",
            "Manfaatkan dosen wali untuk merencanakan mata kuliah semester depan.",
        ],
    },
    "sedang": {
        "judul": "Risiko putus kuliah sedang",
        "ringkas": "Ada beberapa sinyal yang perlu diperhatikan. Dukungan tepat waktu bisa menurunkan risikonya.",
        "saran": [
            "Bicarakan kondisi studi dengan dosen wali atau bagian akademik.",
            "Periksa mata kuliah yang belum lulus dan susun rencana mengulangnya secara realistis.",
            "Jika ada kendala biaya, tanyakan opsi keringanan atau beasiswa kepada bagian kemahasiswaan.",
        ],
    },
    "tinggi": {
        "judul": "Risiko putus kuliah tinggi",
        "ringkas": "Pola data ini mirip dengan mahasiswa yang akhirnya putus kuliah. Hasil ini bukan vonis, tetapi sebaiknya segera ditindaklanjuti.",
        "saran": [
            "Segera temui dosen wali atau layanan konseling kampus untuk membahas kondisi dan kebutuhan Anda.",
            "Cari tahu bantuan yang tersedia: keringanan biaya, beasiswa, tutor sebaya, atau kelompok belajar.",
            "Susun rencana studi yang lebih ringan dan realistis untuk semester berikutnya.",
        ],
    },
}


# ------------------------------------------------------------------- bantuan
def persen(x, digit=1):
    x = min(max(x, 0.001), 0.999)          # hindari tampilan "0,0%" / "100%" yang terlalu pasti
    return f"{x * 100:.{digit}f}".replace(".", ",")


def format_angka(x):
    x = float(x)
    return str(int(x)) if x.is_integer() else f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def tampil_nilai(fitur, nilai):
    """Ubah nilai mentah menjadi teks yang mudah dibaca (nama pilihan atau angka + satuan)."""
    m = META[fitur]
    if m["type"] in ("select", "bool"):
        return m["options"].get(int(nilai), str(int(nilai)))
    satuan = f" {m['satuan']}" if m.get("satuan") and m["satuan"] != "skala 0-20" and m["satuan"] != "skala 0-200" else ""
    return f"{format_angka(nilai)}{satuan}"


def bangun_langkah():
    langkah = []
    for kode, judul, deskripsi in GROUPS:
        isi = []
        for f in FITUR:
            if META[f]["group"] == kode:
                m = dict(META[f])
                m["nama"], m["key"] = f, KUNCI[f]
                isi.append(m)
        if isi:
            langkah.append({"kode": kode, "judul": judul, "deskripsi": deskripsi, "fields": isi})
    return langkah


LANGKAH = bangun_langkah()
CONTOH_FORM = {kelas: {KUNCI[f]: v for f, v in baris.items() if f in KUNCI}
               for kelas, baris in CONTOH.items()}
NAMA_CONTOH = {"Graduate": "Contoh: cenderung lulus",
               "Dropout": "Contoh: cenderung putus kuliah",
               "Enrolled": "Contoh: masih menempuh studi"}

FOTO_KREDIT = [
    # Ganti dengan sumber foto Anda sendiri, misalnya:
    # "Foto beranda: nama fotografer / Unsplash",
]


def baca_form(form):
    """Validasi isian formulir. Mengembalikan (nilai, galat, isian_mentah)."""
    nilai, galat, mentah = {}, {}, {}
    for f in FITUR:
        m, key = META[f], KUNCI[f]
        raw = (form.get(key) or "").strip()
        mentah[key] = raw
        if raw == "":
            galat[key] = "Bagian ini wajib diisi."
            continue
        try:
            x = float(raw.replace(",", "."))
        except ValueError:
            galat[key] = "Isi dengan angka, misalnya 12,5."
            continue
        if m["type"] in ("select", "bool"):
            if not x.is_integer() or int(x) not in m["options"]:
                galat[key] = "Pilih salah satu dari daftar."
                continue
        elif not (m["min"] <= x <= m["max"]):
            galat[key] = f"Nilai harus antara {format_angka(m['min'])} dan {format_angka(m['max'])}."
            continue
        nilai[f] = x
    return nilai, galat, mentah


def tingkat_risiko(p_dropout):
    if p_dropout < 0.25:
        return "rendah"
    if p_dropout < 0.50:
        return "sedang"
    return "tinggi"


def prediksi(nilai):
    X = pd.DataFrame([nilai], columns=FITUR)
    proba = MODEL.predict_proba(X)[0]
    peluang = {LABEL_MAP[int(c)]: float(p) for c, p in zip(MODEL.classes_, proba)}
    kelas_utama = max(peluang, key=peluang.get)
    p_drop = peluang["Dropout"]

    # Penjelasan faktor: ganti satu fitur dengan nilai "umum" (median/modus data latih),
    # lalu lihat seberapa berubah peluang dropout. Ini asosiasi model, bukan sebab-akibat.
    varian = []
    for f in FITUR:
        alt = dict(nilai)
        jenis = "modus" if META[f]["type"] in ("select", "bool") else "median"
        alt[f] = REFERENSI[f][jenis]
        varian.append(alt)
    p_alt = MODEL.predict_proba(pd.DataFrame(varian, columns=FITUR))[:, IDX_DROPOUT]
    efek = []
    for f, pa in zip(FITUR, p_alt):
        delta = p_drop - float(pa)
        if abs(delta) >= 0.01:
            jenis = "modus" if META[f]["type"] in ("select", "bool") else "median"
            efek.append({
                "label": META[f]["label"],
                "nilai": tampil_nilai(f, nilai[f]),
                "umum": tampil_nilai(f, REFERENSI[f][jenis]),
                "delta": persen(abs(delta)),
                "naik": delta > 0,
                "besar": abs(delta),
            })
    efek.sort(key=lambda e: -e["besar"])
    return {
        "peluang": [{"kelas": k, "nama": NAMA_KELAS.get(k, k), "persen": persen(v), "lebar": round(v * 100, 1)}
                    for k, v in sorted(peluang.items(), key=lambda kv: -kv[1])],
        "kelas_utama": kelas_utama,
        "nama_kelas_utama": NAMA_KELAS.get(kelas_utama, kelas_utama),
        "p_dropout": persen(p_drop),
        "lebar_dropout": round(p_drop * 100, 1),
        "tingkat": tingkat_risiko(p_drop),
        "faktor_naik": [e for e in efek if e["naik"]][:4],
        "faktor_turun": [e for e in efek if not e["naik"]][:4],
    }


def ringkasan_isian(nilai):
    ringkas = []
    for kode, judul, _ in GROUPS:
        baris = [{"label": META[f]["label"], "nilai": tampil_nilai(f, nilai[f])}
                 for f in FITUR if META[f]["group"] == kode and f in nilai]
        if baris:
            ringkas.append({"judul": judul, "baris": baris})
    return ringkas


@app.context_processor
def konteks_umum():
    return {"tahun": datetime.now().year, "foto_kredit": FOTO_KREDIT}


# ------------------------------------------------------------------ halaman
@app.route("/")
def index():
    akhir = METRIK.get("model_akhir", {})
    return render_template(
        "index.html",
        jumlah_data=METRIK.get("dataset", {}).get("jumlah_data", 4424),
        distribusi=METRIK.get("dataset", {}).get("distribusi", {}),
        jumlah_fitur=len(FITUR),
        akurasi=persen(akhir["acc_test"]) if "acc_test" in akhir else None,
        f1=persen(akhir["f1_macro"]) if "f1_macro" in akhir else None,
    )


def tampilkan_form(nilai=None, galat=None, status=200):
    galat = galat or {}
    langkah_galat = 0
    for i, lk in enumerate(LANGKAH):
        if any(fld["key"] in galat for fld in lk["fields"]):
            langkah_galat = i
            break
    return render_template("prediksi.html", langkah=LANGKAH, nilai=nilai or {}, galat=galat,
                           langkah_awal=langkah_galat, contoh=CONTOH_FORM, nama_contoh=NAMA_CONTOH), status


@app.route("/prediksi", methods=["GET", "POST"])
def halaman_prediksi():
    # POST dari tombol "Ubah Data" di halaman hasil: isi ulang formulir tanpa validasi
    if request.method == "POST":
        return tampilkan_form(nilai={k: v for k, v in request.form.items() if k in KUNCI.values()})
    return tampilkan_form()


@app.route("/hasil", methods=["GET", "POST"])
def hasil():
    if request.method == "GET":
        return redirect(url_for("halaman_prediksi"))
    nilai, galat, mentah = baca_form(request.form)
    if galat:
        return tampilkan_form(nilai=mentah, galat=galat, status=400)
    return render_template("hasil.html", h=prediksi(nilai), teks=TEKS_RISIKO,
                           isian=ringkasan_isian(nilai), mentah=mentah)


@app.route("/tentang-model")
def tentang_model():
    return render_template(
        "tentang_model.html", m=METRIK,
        penting=IMPORTANCE.get("fitur_web", {}), meta=META, nama_kelas=NAMA_KELAS)


@app.route("/panduan")
def panduan():
    return render_template("panduan.html", nama_kelas=NAMA_KELAS)


@app.route("/health")
def health():
    return {"status": "ok"}


@app.errorhandler(404)
def tidak_ditemukan(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("FLASK_DEBUG") == "1")