# Statistik Kunjungan Clarity

Widget kecil di bagian bawah halaman menampilkan **sesi kunjungan** dan **pengunjung unik**, dengan pilihan tanggal. Angka berasal dari Microsoft Clarity. Pengunjung unik dihitung per browser/perangkat, jadi satu orang yang memakai beberapa perangkat dapat tercatat lebih dari sekali.

## Pasang ke repositori GitHub Pages

Salin `iklan_revisi.html` ke lokasi halaman Anda. Jika halaman utama GitHub Pages bernama `index.html`, gunakan konten HTML ini sebagai `index.html`. Letakkan `traffic-stats.json` di direktori yang sama dengan HTML. Salin juga folder `.github` dari paket ini ke root repositori agar tersedia:

- `.github/workflows/clarity-traffic.yml`
- `.github/scripts/fetch_clarity_traffic.py`

## Simpan token dengan aman

Di Microsoft Clarity, buka proyek → **Settings → Data Export → Generate new API token**. Di GitHub, buka repositori → **Settings → Secrets and variables → Actions → New repository secret**. Buat secret dengan nama persis `CLARITY_API_TOKEN`, lalu masukkan nilai token di sana. Jangan memasukkan token ke HTML, JavaScript, atau file JSON.

Pastikan GitHub Actions diizinkan menulis ke repositori. Workflow ini meminta izin `contents: write`; jika GitHub menolaknya, buka **Settings → Actions → General → Workflow permissions** dan izinkan akses tulis.

## Cara kerja dan batasan

Workflow terjadwal berjalan sekitar **00.05 WIB** setiap hari. Ia meminta snapshot Clarity untuk 24 jam terakhir, memberi tanggal berdasarkan hari kalender Jakarta sebelumnya, lalu memperbarui `traffic-stats.json`. Pemilih tanggal hanya akan menampilkan tanggal yang sudah berhasil direkam. Riwayat mulai terkumpul setelah workflow berjalan; data lama tidak bisa diisi ulang lewat endpoint ini.

File `traffic-stats.json` dapat dibaca publik karena halaman GitHub Pages juga publik. Token Clarity tetap tersimpan sebagai GitHub Actions Secret dan tidak dikirim ke browser. Jika rahasia belum dibuat atau API belum berhasil dipanggil, widget menampilkan pesan bahwa statistik belum tersedia, bukan angka nol.

Dokumentasi resmi menyatakan Data Export API memerlukan token, hanya menyediakan rentang 1–3 hari terakhir, dan membatasi penggunaan hingga 10 permintaan per proyek per hari. Workflow ini hanya membuat satu permintaan per hari.

## Sumber resmi

- [Clarity Data Export API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api)
- [Definisi unique users di Clarity](https://learn.microsoft.com/en-us/clarity/faq)
