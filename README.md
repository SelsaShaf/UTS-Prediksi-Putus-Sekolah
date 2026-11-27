# Prediksi Risiko Putus Kuliah Mahasiswa (Random Forest)

Aplikasi web Flask untuk memperkirakan risiko putus kuliah berdasarkan dataset
"Predict Students' Dropout and Academic Success" (UCI, ID 697, CC BY 4.0).

## Menjalankan secara lokal
1. `python -m venv .venv` lalu aktifkan (Windows: `.venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. Jalankan notebook `notebook/Prediksi_Putus_Kuliah_RF.ipynb` sampai selesai
   (menghasilkan folder `model/` dan `static/charts/`)
4. `python app.py`, lalu buka http://127.0.0.1:5000

## Struktur
- `app.py`, `labels.py`: aplikasi dan metadata formulir
- `notebook/`: eksperimen dan pelatihan model
- `model/`: model dan berkas JSON hasil notebook
- `templates/`, `static/`: tampilan web

## Deploy
Untuk layanan hosting Python (mis. Render atau PythonAnywhere): perintah start `gunicorn app:app`.
Pastikan `model/` ikut ter-upload dan versi scikit-learn di `requirements.txt` sama dengan yang dipakai notebook.

## Catatan etika
Atribut sensitif (jenis kelamin, status pernikahan, dll.) tidak dipakai. Hasil adalah
perkiraan statistik dan bukan keputusan akademik. Data pengguna tidak disimpan.