/* main.js - menu mobile, formulir bertahap, validasi, isi contoh, animasi bar, cetak */
(function () {
  "use strict";

  // ---- Menu mobile
  var tombolNav = document.querySelector(".nav-tombol");
  var menu = document.getElementById("menu-utama");
  if (tombolNav && menu) {
    tombolNav.addEventListener("click", function () {
      var buka = menu.classList.toggle("buka");
      tombolNav.setAttribute("aria-expanded", buka ? "true" : "false");
    });
  }

  // ---- Animasi bar (halaman hasil dan beranda): lebar naik dari 0 ke nilai akhir
  var batang = Array.prototype.slice.call(document.querySelectorAll(".bar span[style*='width']"));
  if (batang.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var akhir = batang.map(function (el) { return el.style.width; });
    batang.forEach(function (el) { el.style.width = "0"; });
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        batang.forEach(function (el, i) { el.style.width = akhir[i]; });
      });
    });
  }

  // ---- Tombol cetak di halaman hasil
  var cetak = document.getElementById("btn-cetak");
  if (cetak) cetak.addEventListener("click", function () { window.print(); });

  // ---- Formulir bertahap
  var form = document.getElementById("form-prediksi");
  if (!form) return;

  var langkah = Array.prototype.slice.call(form.querySelectorAll(".langkah"));
  var indikator = Array.prototype.slice.call(document.querySelectorAll(".indikator li"));
  var bar = document.getElementById("bar-progres");
  var progres = document.querySelector(".progres");
  var btnKembali = document.getElementById("btn-kembali");
  var btnLanjut = document.getElementById("btn-lanjut");
  var btnKirim = document.getElementById("btn-kirim");
  var sekarang = parseInt(form.getAttribute("data-awal"), 10) || 0;

  function pesan(el, teks) {
    var kotak = el.closest(".isian");
    var p = document.getElementById("e-" + el.id);
    if (p) p.textContent = teks || "";
    if (kotak) kotak.classList.toggle("ada-galat", !!teks);
    el.setAttribute("aria-invalid", teks ? "true" : "false");
  }

  function cekField(el) {
    var nilai = (el.value || "").trim();
    if (nilai === "") { pesan(el, "Bagian ini wajib diisi."); return false; }
    if (el.tagName === "INPUT") {
      var x = Number(nilai.replace(",", "."));
      if (!isFinite(x)) { pesan(el, "Isi dengan angka, misalnya 12,5."); return false; }
      var min = parseFloat(el.getAttribute("data-min")), max = parseFloat(el.getAttribute("data-max"));
      if (x < min || x > max) { pesan(el, "Nilai harus antara " + min + " dan " + max + "."); return false; }
    }
    pesan(el, "");
    return true;
  }

  function cekLangkah(i) {
    var salah = null;
    langkah[i].querySelectorAll("input, select").forEach(function (el) {
      if (!cekField(el) && !salah) salah = el;
    });
    if (salah) { salah.focus(); return false; }
    return true;
  }

  function tampil(i, gulir) {
    sekarang = Math.max(0, Math.min(langkah.length - 1, i));
    langkah.forEach(function (el, n) { el.hidden = n !== sekarang; });
    indikator.forEach(function (el, n) {
      el.classList.toggle("aktif", n === sekarang);
      el.classList.toggle("selesai", n < sekarang);
    });
    // Langkah 1 dari 3 = 33%, langkah terakhir = 100%
    var pct = Math.round(((sekarang + 1) / langkah.length) * 100);
    bar.style.width = pct + "%";
    progres.setAttribute("aria-valuenow", String(pct));
    btnKembali.disabled = sekarang === 0;
    var terakhir = sekarang === langkah.length - 1;
    btnLanjut.hidden = terakhir;
    btnKirim.hidden = !terakhir;
    if (gulir === false) return;               // pemuatan awal: jangan menggulir halaman
    var judul = langkah[sekarang].querySelector("legend");
    if (judul) { judul.setAttribute("tabindex", "-1"); judul.focus({ preventScroll: true }); }
    window.scrollTo({ top: form.getBoundingClientRect().top + window.scrollY - 140, behavior: "smooth" });
  }

  btnLanjut.addEventListener("click", function () { if (cekLangkah(sekarang)) tampil(sekarang + 1); });
  btnKembali.addEventListener("click", function () { tampil(sekarang - 1); });

  // Enter di kolom angka = lanjut (bukan kirim sebelum langkah terakhir)
  form.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && e.target.tagName === "INPUT") {
      e.preventDefault();
      if (sekarang < langkah.length - 1) btnLanjut.click(); else btnKirim.click();
    }
  });

  // Validasi saat meninggalkan kolom
  form.addEventListener("focusout", function (e) {
    var el = e.target;
    if ((el.tagName === "INPUT" || el.tagName === "SELECT") && el.value.trim() !== "") cekField(el);
  });

  // Validasi semua langkah sebelum kirim
  form.addEventListener("submit", function (e) {
    for (var i = 0; i < langkah.length; i++) {
      if (!cekLangkah(i)) { e.preventDefault(); tampil(i); return; }
    }
  });

  // Isi contoh dan reset
  var dataContoh = {};
  try { dataContoh = JSON.parse(document.getElementById("data-contoh").textContent); } catch (err) {}

  function isiKolom(el, nilai) {
    if (el.tagName === "SELECT") {
      // Pilihan memakai kode bulat ("1", "9119"); ubah "1.0" menjadi "1"
      var angka = Number(nilai);
      el.value = isFinite(angka) ? String(Math.round(angka)) : String(nilai);
    } else {
      el.value = String(nilai).replace(".", ",");
    }
    pesan(el, "");
  }

  document.querySelectorAll("[data-contoh]").forEach(function (tombol) {
    tombol.addEventListener("click", function () {
      var isi = dataContoh[tombol.getAttribute("data-contoh")] || {};
      Object.keys(isi).forEach(function (key) {
        var el = document.getElementById(key);
        if (el) isiKolom(el, isi[key]);
      });
      tampil(0);
    });
  });
  document.getElementById("btn-kosongkan").addEventListener("click", function () {
    form.querySelectorAll("input, select").forEach(function (el) { el.value = ""; pesan(el, ""); });
    tampil(0);
  });

  tampil(sekarang, false);
})();