# Referensi Command Admin Userbot

Halaman ini berisi daftar lengkap command admin yang tersedia pada Python Telegram Userbot Promo Framework. Semua command dimulai dengan awalan (prefix) `!`.

> [!IMPORTANT]
> Command di bawah ini hanya dapat dieksekusi oleh akun Master yang ditentukan di dalam `.env` (via `MASTER_ID` atau `MASTER_USERNAME`). Pengguna lain yang mencoba menjalankan command ini akan ditolak secara otomatis.

---

## Daftar Command

### 1. Kontrol Sistem & Status

#### `!help` / `!menu`
Tampilkan pesan bantuan berisi semua daftar command dan format penggunaannya.

#### `!ping`
Memeriksa apakah userbot merespons dan masih hidup.
* **Respon**: `🏓 Pong! Bot promo aktif dan berjalan.`

#### `!status`
Menampilkan detail status runtime bot saat ini.
* **Detail yang Ditampilkan**:
  - Status scheduler (`RUNNING` atau `PAUSED`)
  - Waktu eksekusi wave terakhir
  - Estimasi waktu eksekusi wave berikutnya
  - Rentang delay saat ini (min/max menit)
  - Jumlah target grup aktif dan diskip
  - Jumlah template promo aktif di database

#### `!server`
Menampilkan metrik performa hosting/VPS tempat bot berjalan.
* **Detail yang Ditampilkan**:
  - Operating System dan versinya
  - Versi Python runtime
  - Uptime proses Bot
  - Uptime Server
  - Bar load CPU (%)
  - Bar load RAM (%) beserta kapasitas terpakai dan total
  - Bar load Disk (%) beserta kapasitas terpakai dan total

#### `!reload`
Memuat ulang variabel dari file `.env` dan menyinkronkan kembali status in-memory dengan pengaturan terbaru di database. Gunakan command ini setelah melakukan edit database secara manual atau mengubah `.env`.

---

### 2. Manajemen Pengiriman Promo (Wave)

#### `!pause`
Menunda (pause) eksekusi wave promo otomatis.
* **Efek**: Scheduler background akan berhenti men-trigger wave otomatis, namun handler command chat admin tetap aktif 24/7. Status `paused` akan disimpan ke database settings.

#### `!resume`
Mengaktifkan kembali (resume) eksekusi wave promo otomatis.
* **Efek**: Scheduler akan menghitung interval random baru dan menjadwalkan wave berikutnya. Status `paused` diperbarui ke `0` di database.

#### `!wave`
Memicu eksekusi 1 wave pengiriman pesan promo secara manual saat ini juga.
* **Keamanan**: Dilengkapi anti double-wave lock. Jika ada wave otomatis atau manual lain yang sedang berjalan, command ini akan dibatalkan agar tidak terjadi penumpukan/spam.

#### `!setdelay <min_menit> <max_menit>`
Mengubah rentang waktu tunda acak antar wave otomatis langsung dari chat Telegram.
* **Contoh**: `!setdelay 30 120` (mengatur delay acak antara 30 hingga 120 menit).
* **Efek**: Perubahan disimpan di database dan diterapkan mulai siklus scheduler berikutnya.

#### `!logs`
Menampilkan log ringkasan dari eksekusi wave terakhir yang tersimpan di database.
* **Detail**: ID Wave, Waktu mulai, Durasi pengiriman total, Jumlah sukses/gagal, dan rincian per target grup (Success atau Failure beserta pesan error).

---

### 3. Manajemen Target Grup

#### `!groups`
Menampilkan semua target grup yang terdaftar di database lengkap dengan database ID (DB ID) dan status keaktifannya (`[✅ AKTIF]` atau `[❌ SKIP]`).

#### `!addgroup <username_grup | link_grup>`
Mendaftarkan grup baru ke database target promo.
* **Format**:
  - Username: `@username_grup` atau `username_grup`
  - Link: `https://t.me/username_grup`
* **Cara Kerja**: Bot akan mencoba mencari entitas grup tersebut secara online. Jika ditemukan, bot akan menyimpan Judul asli, Username, dan input mentah ke database dengan status Aktif secara default.
* **Error**: Jika grup bersifat privat atau akun userbot Anda tidak memiliki akses, bot akan gagal melakukan resolve dan menampilkan pesan error detail.

#### `!delgroup <DB_ID | username>`
Menghapus grup target dari database promo secara permanen.
* **Contoh**: `!delgroup 3` atau `!delgroup @group_test`

#### `!skip <DB_ID | username>`
Menunda pengiriman promo ke grup tertentu tanpa menghapusnya dari database.
* **Contoh**: `!skip 2` atau `!skip @group_test`
* **Efek**: Status `is_skipped` diubah menjadi `1`. Grup akan dilewati saat wave otomatis maupun manual berjalan.

#### `!unskip <DB_ID | username>`
Mengaktifkan kembali pengiriman promo ke grup yang sebelumnya diskip.
* **Contoh**: `!unskip 2`

---

### 4. Manajemen Template Promo

#### `!templates`
Menampilkan semua template pesan promo yang terdaftar di database, lengkap dengan ID Template, status keaktifan, dan cuplikan singkat isi pesan.

#### `!addtemplate <isi_pesan>`
Menambahkan template pesan baru ke database. Mendukung baris baru (newline), emoji, dan format markdown bawaan Telegram.
* **Contoh**:
  ```text
  !addtemplate Promo Spesial Akhir Bulan! 🚀
  Dapatkan diskon 50% untuk semua layanan kami.
  Hubungi @admin sekarang juga!
  ```

#### `!deltemplate <ID_template>`
Menghapus template pesan dari database berdasarkan ID database-nya.
* **Contoh**: `!deltemplate 2`

#### `!preview`
Memilih secara acak salah satu template aktif di database dan mengirimkannya ke ruang chat admin sebagai contoh preview tampilan pesan.

#### `!test <DB_ID | username> [pesan_kustom]`
Mengirimkan pesan uji coba ke satu grup target tertentu saat ini juga untuk memastikan format dan koneksi aman.
* **Keterangan**: Jika `[pesan_kustom]` tidak diisi, bot secara acak akan mengirimkan salah satu template aktif di database.
* **Contoh**: `!test 5 Halo ini uji coba` atau `!test @group_test`

---

### 5. Cadangan Data (Backup)

#### `!backup`
Memicu pembuatan file backup cadangan instan.
* **Proses**:
  1. Mengompresi source code penting, database SQLite (`data/bot.db`), sesi Telegram (`sessions/`), dan dokumentasi ke format `.zip`.
  2. Melakukan enkripsi berkas `.zip` menggunakan GPG dengan standar keamanan **AES256** dan password `BACKUP_PASSWORD` yang diatur di `.env`.
  3. Mengirimkan berkas `.gpg` yang dihasilkan ke target `BACKUP_TARGET` di Telegram.
  4. Menghapus file `.zip` dan `.gpg` cadangan sementara dari server setelah pengiriman selesai untuk menjaga ruang penyimpanan disk.
* **Catatan**: Jika server tidak terinstall utilitas `gpg`, bot hanya akan mengirimkan file `.zip` biasa **hanya jika** `ALLOW_UNENCRYPTED_BACKUP` bernilai `true` di `.env`. Jika diset `false`, backup akan dibatalkan demi keamanan.
