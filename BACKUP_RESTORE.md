# Panduan Pencadangan & Pemulihan (Backup & Restore)

Dokumen ini menjelaskan cara menggunakan berkas cadangan (backup) yang dihasilkan oleh command `!backup` untuk memulihkan bot ke keadaan semula pada server baru maupun lokal.

---

## 1. Memahami File Backup

Saat Anda mengetik `!backup` di Telegram, bot akan mengirimkan berkas dengan salah satu nama berikut:
- **`backup_YYYYMMDD_HHMMSS.zip.gpg`** (Direkomendasikan/Enkripsi Aman): Berkas zip terkompresi yang dienkripsi secara aman dengan algoritma **AES256**.
- **`backup_YYYYMMDD_HHMMSS.zip`** (Unencrypted): Hanya dikirim jika GPG tidak terinstal di server asal dan opsi `ALLOW_UNENCRYPTED_BACKUP=true` diaktifkan di `.env`.

---

## 2. Cara Dekripsi Berkas Backup (.gpg)

Jika berkas backup Anda dienkripsi (.gpg), Anda harus mendekripsinya terlebih dahulu sebelum mengekstrak isinya.

### Menggunakan Linux / macOS (Terminal)
Jalankan perintah berikut:
```bash
gpg --decrypt -o restored_backup.zip backup_YYYYMMDD_HHMMSS.zip.gpg
```
Sistem akan meminta password dekripsi. Masukkan nilai **`BACKUP_PASSWORD`** yang Anda gunakan di dalam berkas `.env` server lama Anda.

### Menggunakan Windows
1. Unduh dan pasang perangkat lunak **Gpg4win** dari situs resminya [https://gpg4win.org](https://gpg4win.org).
2. Setelah terpasang, klik kanan berkas `.gpg`, pilih **Decrypt and verify** (atau gunakan aplikasi **Kleopatra** bawaan Gpg4win).
3. Masukkan password dekripsi Anda. File hasil dekripsi berupa `.zip` akan tersimpan di folder yang sama.

---

## 3. Langkah-Langkah Pemulihan (Restore)

Setelah Anda berhasil mendapatkan file `.zip` hasil dekripsi, ikuti langkah berikut untuk memulihkan aplikasi:

1. **Ekstrak Berkas ZIP**:
   Ekstrak file `restored_backup.zip` ke dalam direktori kerja baru Anda. Struktur direktori hasil ekstrak akan terlihat seperti ini:
   ```text
   ├── data/
   │   └── bot.db              # Database SQLite Anda (berisi grup, template, dll)
   ├── sessions/
   │   └── promo_userbot.session # File sesi Telegram Anda
   ├── docs/
   ├── main.py
   ├── requirements.txt
   └── ... (source code lainnya)
   ```
2. **Siapkan Konfigurasi Lingkungan**:
   Salin `.env.example` menjadi `.env` di folder baru tersebut:
   ```bash
   cp .env.example .env
   ```
   Isi file `.env` baru Anda dengan nilai yang sama seperti sebelumnya (terutama `API_ID`, `API_HASH`, dan `BACKUP_PASSWORD`).
3. **Instal Ulang Dependencies**:
   Jalankan perintah instalasi dependensi di server baru:
   ```bash
   pip3 install -r requirements.txt
   ```
4. **Jalankan Bot**:
   Jalankan bot Anda kembali:
   ```bash
   python3 main.py
   ```
   Karena file sesi (`sessions/promo_userbot.session`) dan database (`data/bot.db`) dipulihkan dengan benar, **bot Anda akan langsung berjalan tanpa meminta OTP masuk kembali**.
