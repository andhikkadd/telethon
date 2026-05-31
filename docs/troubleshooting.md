# Panduan Troubleshooting (Pemecahan Masalah)

Dokumen ini berisi daftar masalah umum yang mungkin Anda temui saat menjalankan Telegram Userbot Promo Framework beserta solusi penyelesaiannya.

---

## 1. Error Lingkungan & Startup

### `ModuleNotFoundError: No module named 'telethon'`
* **Penyebab**: Dependency python belum terinstall di runtime Anda.
* **Solusi**:
  Jalankan perintah berikut di console/terminal Anda:
  ```bash
  pip3 install -r requirements.txt
  ```
  Jika menggunakan PM2 di server Anda, pastikan process manager Anda melakukan auto-install atau jalankan command instalasi secara manual melalui terminal.

### `ValueError: API_ID is required but missing in .env`
* **Penyebab**: Konfigurasi file `.env` belum dibuat atau variabel `API_ID` dan `API_HASH` belum diisi.
* **Solusi**:
  1. Salin `.env.example` menjadi `.env`:
     ```bash
     cp .env.example .env
     ```
  2. Edit file `.env` menggunakan text editor (seperti nano) dan isi dengan kredensial API Telegram Anda yang didapat dari [https://my.telegram.org](https://my.telegram.org).

---

## 2. Masalah Sesi & Login Telegram

### Akun Ter-logged Out / Sesi Tidak Valid
* **Penyebab**: Sesi Anda dideotorisasi dari perangkat aktif Telegram, atau file sesi di `sessions/` rusak/terhapus.
* **Solusi**:
  1. Hentikan proses bot (`pm2 stop main` atau hentikan via panel).
  2. Hapus file sesi lama di folder `sessions/`:
     ```bash
     rm sessions/promo_userbot.session*
     ```
  3. Jalankan bot secara interaktif di terminal agar Anda bisa memasukkan nomor HP dan OTP baru:
     ```bash
     python3 main.py
     ```
  4. Setelah sukses login, hentikan bot (`Ctrl+C`) lalu jalankan kembali lewat PM2 / systemd.

### `FloodWaitError` / Akun Dibatasi Sementara
* **Penyebab**: Telegram mendeteksi aktivitas pengiriman pesan atau login yang terlalu cepat dari akun Anda (rate limit).
* **Solusi**:
  - Jika FloodWait terjadi saat mengirim pesan, bot akan otomatis tidur selama detik yang diminta (jika kurang dari 90 detik) atau melewatkan grup tersebut.
  - Jika FloodWait terjadi saat login pertama, Anda harus menunggu waktu penangguhan yang ditentukan Telegram (biasanya tertera di log konsol dalam hitungan detik) sebelum mencoba login kembali.
  - **Pencegahan**: Jangan set `DELAY_BETWEEN_GROUPS_SECONDS` terlalu kecil. Batas aman minimal adalah 15-30 detik.

---

## 3. Masalah Database SQLite

### `sqlite3.OperationalError: database is locked`
* **Penyebab**: SQLite mengalami kebuntuan (deadlock) karena ada proses lain yang sedang menulis ke database secara bersamaan, atau koneksi sebelumnya tidak ditutup dengan benar saat bot crash.
* **Solusi**:
  - Hentikan seluruh instance bot yang berjalan. Pastikan tidak ada double process:
    ```bash
    ps aux | grep python3
    ```
    Gunakan `kill <PID>` untuk mematikan proses gantung.
  - Restart bot menggunakan PM2 untuk memastikan hanya ada satu koneksi aktif ke database.

---

## 4. Masalah Pengiriman Grup

### `ValueError: Could not find the input entity for...`
* **Penyebab**: Bot tidak dapat menemukan grup target. Ini biasanya terjadi ketika Anda menambahkan grup baru menggunakan username yang salah, grup tersebut privat dan akun Anda belum bergabung, atau akun Anda diblokir dari grup tersebut.
* **Solusi**:
  - Coba buka link grup menggunakan aplikasi Telegram biasa pada akun userbot untuk memastikan akun tersebut sudah terdaftar sebagai anggota grup.
  - Pastikan format username yang dimasukkan benar (contoh: `@nama_grup` atau link lengkap `t.me/nama_grup`).

---

## 5. Masalah Backup & Enkripsi

### `RuntimeError: GPG is not available and ALLOW_UNENCRYPTED_BACKUP=false`
* **Penyebab**: Perintah `!backup` dijalankan, tetapi server/hosting Anda tidak memiliki program `gpg` terinstal di sistemnya, sementara pengaturan keamanan melarang pengiriman zip tanpa sandi.
* **Solusi**:
  - **Opsi A (Direkomendasikan)**: Hubungi administrator server Anda atau instal `gnupg` secara manual:
    ```bash
    # Debian/Ubuntu
    sudo apt-get install gnupg
    ```
  - **Opsi B**: Jika Anda berada di lingkungan hosting terbatas dan tidak dapat menginstal package sistem, Anda dapat mengizinkan backup ZIP tanpa enkripsi dengan mengubah pengaturan di `.env`:
    ```env
    ALLOW_UNENCRYPTED_BACKUP=true
    ```
