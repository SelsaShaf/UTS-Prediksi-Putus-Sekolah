"""
labels.py - metadata tiap fitur untuk formulir web.

Isi: label berbahasa Indonesia, penjelasan, kelompok langkah, jenis input,
dan peta kode angka -> nama yang mudah dibaca.
Nama kunci HARUS sama persis dengan nama kolom di dataset (setelah di-strip).
"""

# Kelompok langkah pada formulir: (kode, judul, deskripsi)
GROUPS = [
    ("daftar", "Data Pendaftaran dan Biaya Kuliah",
     "Informasi yang sudah diketahui sejak mahasiswa mendaftar dan kondisi biaya kuliahnya."),
    ("sem1", "Hasil Semester 1",
     "Capaian akademik pada semester pertama. Lihat KHS (Kartu Hasil Studi) atau portal akademik."),
    ("sem2", "Hasil Semester 2",
     "Capaian akademik pada semester kedua. Jika belum ada, isi dengan perkiraan terbaik Anda."),
]

YA_TIDAK = {1: "Ya", 0: "Tidak"}

# Nama program studi (kode asli dataset -> nama Indonesia)
PRODI = {
    33: "Teknologi Produksi Biofuel",
    171: "Desain Animasi dan Multimedia",
    8014: "Pelayanan Sosial (kelas malam)",
    9003: "Agronomi",
    9070: "Desain Komunikasi",
    9085: "Keperawatan Hewan",
    9119: "Teknik Informatika",
    9130: "Peternakan Kuda (Equinculture)",
    9147: "Manajemen",
    9238: "Pelayanan Sosial",
    9254: "Pariwisata",
    9500: "Keperawatan",
    9556: "Kebersihan Mulut (Oral Hygiene)",
    9670: "Manajemen Periklanan dan Pemasaran",
    9773: "Jurnalistik dan Komunikasi",
    9853: "Pendidikan Dasar",
    9991: "Manajemen (kelas malam)",
}

JALUR_MASUK = {
    1: "Tahap 1 - kontingen umum (jalur paling umum)",
    2: "Peraturan No. 612/93",
    5: "Tahap 1 - kontingen khusus (Kepulauan Azores)",
    7: "Pemegang gelar pendidikan tinggi lain",
    10: "Peraturan No. 854-B/99",
    15: "Mahasiswa internasional (sarjana)",
    16: "Tahap 1 - kontingen khusus (Kepulauan Madeira)",
    17: "Tahap 2 - kontingen umum",
    18: "Tahap 3 - kontingen umum",
    26: "Peraturan No. 533-A/99 butir b2 (rencana studi berbeda)",
    27: "Peraturan No. 533-A/99 butir b3 (institusi lain)",
    39: "Usia di atas 23 tahun",
    42: "Pindahan (transfer)",
    43: "Pindah program studi",
    44: "Pemegang diploma spesialisasi teknologi",
    51: "Pindah institusi / program studi",
    53: "Pemegang diploma siklus pendek",
    57: "Pindah institusi / program studi (internasional)",
}

PENDIDIKAN_SEBELUMNYA = {
    1: "Pendidikan menengah (setara SMA)",
    2: "Pendidikan tinggi - gelar bachelor",
    3: "Pendidikan tinggi - gelar sarjana (licenciatura)",
    4: "Pendidikan tinggi - magister",
    5: "Pendidikan tinggi - doktor",
    6: "Pernah menempuh pendidikan tinggi (belum selesai)",
    9: "Kelas 12 - belum tamat",
    10: "Kelas 11 - belum tamat",
    12: "Lainnya - kelas 11",
    14: "Kelas 10",
    15: "Kelas 10 - belum tamat",
    19: "Pendidikan dasar siklus 3 (kelas 9/10/11) atau setara",
    38: "Pendidikan dasar siklus 2 (kelas 6/7/8) atau setara",
    39: "Kursus spesialisasi teknologi",
    40: "Pendidikan tinggi - gelar sarjana (siklus 1)",
    42: "Kursus teknik tinggi profesional",
    43: "Pendidikan tinggi - magister (siklus 2)",
}


def _angka(label, help_, group, minimum, maksimum, step, contoh, satuan=""):
    return {"label": label, "help": help_, "group": group, "type": "number",
            "min": minimum, "max": maksimum, "step": step, "contoh": contoh, "satuan": satuan}


def _pilihan(label, help_, group, options, tipe="select"):
    return {"label": label, "help": help_, "group": group, "type": tipe, "options": options}


def _semester(n, nama_grup):
    s = f"semester {n}"
    k = f"Curricular units {'1st' if n == 1 else '2nd'} sem"
    return {
        f"{k} (credited)": _angka(
            f"Mata kuliah yang diakui ({s})",
            "Mata kuliah yang nilainya diakui dari studi sebelumnya sehingga tidak perlu diambil lagi. Isi 0 jika tidak ada.",
            nama_grup, 0, 30, 1, 0, "mata kuliah"),
        f"{k} (enrolled)": _angka(
            f"Mata kuliah yang diambil ({s})",
            "Jumlah mata kuliah yang didaftarkan (di-KRS-kan) pada semester ini.",
            nama_grup, 0, 30, 1, 6, "mata kuliah"),
        f"{k} (evaluations)": _angka(
            f"Jumlah evaluasi/ujian ({s})",
            "Total ujian atau penilaian yang diikuti, termasuk ujian ulang. Bisa lebih besar dari jumlah mata kuliah.",
            nama_grup, 0, 50, 1, 8, "evaluasi"),
        f"{k} (approved)": _angka(
            f"Mata kuliah yang lulus ({s})",
            "Jumlah mata kuliah yang dinyatakan lulus pada semester ini.",
            nama_grup, 0, 30, 1, 5, "mata kuliah"),
        f"{k} (grade)": _angka(
            f"Rata-rata nilai ({s})",
            "Rata-rata nilai semester pada skala 0-20 (skala Portugal, umumnya nilai 10 ke atas dianggap lulus). Gunakan titik atau koma untuk desimal.",
            nama_grup, 0, 20, 0.01, 12.5, "skala 0-20"),
        f"{k} (without evaluations)": _angka(
            f"Mata kuliah tanpa evaluasi ({s})",
            "Mata kuliah yang diambil tetapi tidak diikuti satu pun evaluasi. Isi 0 jika semua diikuti.",
            nama_grup, 0, 20, 1, 0, "mata kuliah"),
    }


META = {
    "Application mode": _pilihan(
        "Jalur pendaftaran",
        "Cara mahasiswa diterima di kampus. Jika ragu, pilih jalur yang paling umum (Tahap 1 - kontingen umum).",
        "daftar", JALUR_MASUK),
    "Application order": _angka(
        "Urutan pilihan program studi",
        "0 berarti program studi ini adalah pilihan pertama, 1 pilihan kedua, dan seterusnya sampai 9 (pilihan terakhir).",
        "daftar", 0, 9, 1, 0, "urutan"),
    "Course": _pilihan(
        "Program studi",
        "Program studi yang sedang ditempuh. Daftar mengikuti dataset sumber (sebuah institusi pendidikan tinggi di Portugal).",
        "daftar", PRODI),
    "Daytime/evening attendance": _pilihan(
        "Waktu perkuliahan",
        "Apakah mahasiswa mengikuti kelas siang (reguler) atau malam.",
        "daftar", {1: "Siang (reguler)", 0: "Malam"}),
    "Previous qualification": _pilihan(
        "Pendidikan sebelum kuliah",
        "Jenjang pendidikan terakhir sebelum masuk program studi ini.",
        "daftar", PENDIDIKAN_SEBELUMNYA),
    "Previous qualification (grade)": _angka(
        "Nilai pendidikan sebelumnya",
        "Nilai kelulusan pendidikan sebelumnya pada skala 0-200 (skala Portugal). Pada data asli berkisar 95-190.",
        "daftar", 0, 200, 0.1, 130, "skala 0-200"),
    "Admission grade": _angka(
        "Nilai seleksi masuk",
        "Nilai akhir seleksi masuk pada skala 0-200. Pada data asli berkisar 95-190.",
        "daftar", 0, 200, 0.1, 125, "skala 0-200"),
    "Age at enrollment": _angka(
        "Usia saat mendaftar",
        "Usia mahasiswa (dalam tahun) pada saat pertama kali mendaftar.",
        "daftar", 15, 80, 1, 19, "tahun"),
    "Debtor": _pilihan(
        "Memiliki tunggakan (debitur)",
        "Apakah mahasiswa tercatat memiliki tunggakan pembayaran ke kampus.",
        "daftar", YA_TIDAK, "bool"),
    "Tuition fees up to date": _pilihan(
        "Biaya kuliah terbayar tepat waktu",
        "Apakah pembayaran biaya kuliah mahasiswa saat ini sudah lunas dan tidak menunggak.",
        "daftar", YA_TIDAK, "bool"),
    "Scholarship holder": _pilihan(
        "Penerima beasiswa",
        "Apakah mahasiswa sedang menerima beasiswa.",
        "daftar", YA_TIDAK, "bool"),
}
META.update(_semester(1, "sem1"))
META.update(_semester(2, "sem2"))