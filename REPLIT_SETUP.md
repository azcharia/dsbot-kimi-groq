# Setup Bot di Replit (100% Gratis)

## Step 1: Upload ke Replit

1. Buka https://replit.com dan login/daftar
2. Klik **"Create Repl"**
3. Pilih **"Import from GitHub"** atau **"Upload files"**
4. Kalau upload manual:
   - Upload semua file kecuali `.env`
   - Atau drag & drop folder project

## Step 2: Setup Environment Variables

1. Di Replit, klik **"Tools"** (sidebar kiri) → **"Secrets"**
2. Tambahkan 2 secrets:
   - Key: `DISCORD_TOKEN` → Value: token Discord bot kamu
   - Key: `GROQ_API_KEY` → Value: API key Groq kamu
3. Secrets ini otomatis jadi environment variables

## Step 3: Install Dependencies

Di Replit Shell (tab bawah), jalankan:
```bash
pip install -r requirements.txt
```

Atau Replit biasanya auto-detect dan install sendiri.

## Step 4: Run Bot

1. Klik tombol **"Run"** di atas
2. Bot akan jalan dan web server akan aktif di port 8080
3. Kamu akan lihat URL replit kamu (contoh: `https://akane-bot.username.repl.co`)

## Step 5: Keep Alive (Agar Bot Jalan 24/7)

Replit free tier akan sleep kalau tidak ada aktivitas. Untuk keep alive:

### Opsi A: UptimeRobot (Recommended - Gratis)
1. Daftar di https://uptimerobot.com (gratis)
2. Add New Monitor:
   - Monitor Type: **HTTP(s)**
   - Friendly Name: **Akane Bot**
   - URL: URL replit kamu (dari step 4)
   - Monitoring Interval: **5 minutes**
3. Save - UptimeRobot akan ping bot tiap 5 menit, jadi bot tidak sleep

### Opsi B: Cron-job.org (Alternatif Gratis)
1. Daftar di https://cron-job.org
2. Create cronjob:
   - URL: URL replit kamu
   - Interval: Every 5 minutes
3. Save

### Opsi C: Manual Ping
Buka URL replit kamu di browser setiap beberapa jam untuk "bangunin" bot.

## Troubleshooting

**Bot tidak respond:**
- Cek Secrets sudah benar
- Cek logs di Replit console
- Pastikan bot sudah di-invite ke server Discord

**Bot sleep terus:**
- Pastikan UptimeRobot atau Cron-job sudah setup
- Cek URL replit bisa diakses

**Error saat run:**
- Cek dependencies sudah terinstall
- Restart Repl

## Notes

- Replit free tier kadang ada downtime, tapi untuk personal use cukup oke
- Bot akan restart otomatis kalau ada error
- Logs bisa dilihat di console Replit