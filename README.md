# Discord AI Bot dengan Groq

Bot Discord yang menggunakan Groq AI untuk chat.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` ke `.env` dan isi dengan token:
```bash
cp .env.example .env
```

3. Isi `.env` dengan:
- `DISCORD_TOKEN`: Token bot Discord kamu
- `GROQ_API_KEY`: API key Groq kamu

4. Jalankan bot:
```bash
python bot.py
```

## Cara Pakai

- Mention bot di server: `@BotName halo`
- Atau kirim DM langsung ke bot
- Command: `!ping` untuk test koneksi

## Fitur

- Chat dengan AI menggunakan Groq
- Respond ke mention dan DM
- Character preferences (bisa dikustomisasi)
- Auto-split pesan panjang