# Web Control Panel Guide

Proyek ini dilengkapi dengan Web Control Panel berbasis **FastAPI** + **Jinja2** yang berjalan dalam satu proses (event loop) yang sama dengan Telegram Userbot. Anda dapat memantau status bot, melihat grafik resource, mengelola grup dan template promo, melihat log, serta melakukan diagnostic dan backup secara visual.

---

## 1. Konfigurasi Environment (.env)

Pastikan variabel-variabel berikut diatur pada berkas `.env` Anda sebelum menjalankan aplikasi:

```env
# Mengaktifkan/menonaktifkan web panel (true/false)
ENABLE_WEB_PANEL=true

# Host binding (default 0.0.0.0 agar dapat diakses dari luar)
WEB_HOST=0.0.0.0

# Port yang digunakan oleh FastAPI
WEB_PORT=8000

# Kredensial Administrator Web Panel
WEB_ADMIN_USERNAME=admin
WEB_ADMIN_PASSWORD=isi_password_admin_yang_sangat_kuat

# Kunci acak untuk menandatangani session cookies
WEB_SESSION_SECRET=masukkan_random_string_panjang_di_sini
```

> [!WARNING]
> Jangan biarkan `WEB_ADMIN_PASSWORD` kosong jika `ENABLE_WEB_PANEL=true`. Sistem akan mendeteksi password kosong saat startup dan menghentikan proses (crash) demi alasan keamanan. Gunakan password yang panjang dan unik untuk melindungi sesi MTProto akun Telegram Anda.

---

## 2. Pengaturan Port & Akses Firewall

Untuk dapat mengakses Web Panel secara langsung melalui alamat IP publik server Anda:

1. Pastikan port yang Anda tetapkan pada `WEB_PORT` (default `8000`) telah dibuka di firewall sistem operasi server Anda (misalnya **UFW** pada Ubuntu/Debian):
   ```bash
   sudo ufw allow 8000/tcp
   ```
2. Jika Anda menggunakan layanan cloud (seperti AWS EC2, Google Cloud, DigitalOcean), pastikan Anda telah mengonfigurasi aturan keamanan jaringan (**Security Group** / **Firewall Rules**) untuk mengizinkan trafik masuk (Inbound Traffic) pada port tersebut.
3. Akses panel melalui peramban: `http://<IP_SERVER_ANDA>:8000`.

---

## 3. Deployment Menggunakan Cloudflare Tunnel (Alternatif NAT / Port Terblokir)

Jika server Anda berada di balik jaringan NAT, tidak memiliki IP publik statis, atau firewall memblokir semua port masuk, gunakan **Cloudflare Tunnel** (gratis) untuk mengekspos Web Panel ke internet secara aman tanpa port-forwarding:

### Langkah A: Buat Tunnel melalui Cloudflare Dashboard
1. Buka dashboard Cloudflare Anda dan masuk ke menu **Zero Trust** > **Networks** > **Tunnels**.
2. Klik **Create a Tunnel**, beri nama (misalnya `telegram-userbot`), lalu klik **Save**.
3. Cloudflare akan menyediakan perintah instalasi beserta **Token Tunnel** (string acak yang panjang).

### Langkah B: Jalankan Cloudflared di Server
1. Unduh dan pasang binary `cloudflared` pada server:
   ```bash
   curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared.deb
   ```
2. Jalankan tunnel sebagai proses latar belakang PM2:
   ```bash
   pm2 start cloudflared --name "cf-tunnel" -- tunnel run --token <MASUKKAN_TOKEN_CLOUDFLARE_DI_SINI>
   ```
3. Di Dashboard Cloudflare (menu **Public Hostname**), tambahkan entri:
   - **Subdomain/Domain**: `userbot.domainanda.com`
   - **Service Type**: `HTTP`
   - **URL**: `localhost:8000` (atau sesuaikan dengan port `WEB_PORT` Anda).
4. Klik **Save Hostname**. Selesai! Web panel kini aman diakses lewat `https://userbot.domainanda.com` dengan SSL otomatis.

---

## 4. Emergency Telegram Control

Meskipun Web Panel mempermudah manajemen visual sehari-hari, **Telegram Admin Commands** tetap aktif 24/7 dan berjalan secara paralel sebagai kontrol darurat (emergency control).

Jika Web Panel tidak dapat diakses akibat gangguan jaringan, kegagalan web server, atau saat proses bootstrapping OTP pertama kali:
- Kirim command chat biasa seperti `!status`, `!pause`, `!resume`, `!health`, atau `!backup` langsung dari akun Master Anda di aplikasi Telegram.
- Perubahan status dari Telegram (misalnya jeda scheduler dengan `!pause`) akan langsung ter-sinkronisasi dan terlihat pada halaman Dashboard Web Panel secara real-time.
