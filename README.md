# Download Foto Panen Script

Script Python sederhana untuk download foto panen dari server CMP Citra Borneo.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Buat file `.env` di root folder dan tambahkan konfigurasi:
```
BASE_URL=xxxx
BEARER_TOKEN=your_actual_bearer_token_here
DELAY_BETWEEN_PHOTOS=1.0
```

**Konfigurasi:**
- `BASE_URL`: URL base API (wajib)
- `BEARER_TOKEN`: Token autentikasi (wajib)
- `DELAY_BETWEEN_PHOTOS`: Delay antar download foto dalam detik (opsional, default: 1.0)

Atau copy dari `.env.example`:
```bash
copy .env.example .env
```
Kemudian edit file `.env` dan masukkan token Anda.

## Cara Menggunakan

Jalankan script:
```bash
python download_photos.py
```

Script akan:
1. Otomatis mengambil data panen dari tanggal kemarin
2. Download semua foto yang ada
3. Menyimpan foto ke folder `sawit/dd-mm-yyyy/`

## Struktur Folder

Foto akan disimpan dalam struktur:
```
sawit/
  └── dd-mm-yyyy/
      ├── PANEN_TPH_1_461_SCE_NOTPH_12_20251118_081701.jpg
      ├── PANEN_TPH_1_461_SCE_NOTPH_14_20251118_081731.jpg
      └── ...
```

## Fitur

- ✅ Otomatis menggunakan tanggal kemarin untuk query data
- ✅ Support multiple foto per data panen (dipisahkan titik koma `;`)
- ✅ Skip foto yang tidak ditemukan (Photo not found)
- ✅ Delay antar download untuk menghindari overload server
- ✅ Error handling yang robust - melanjutkan download meski ada error
- ✅ Progress tracking untuk setiap foto

## Catatan

- Foto akan di-download ke folder sesuai tanggal (format: dd-mm-yyyy)
- Jika ada error pada salah satu foto, script akan melanjutkan ke foto berikutnya
- Foto yang tidak ditemukan akan di-skip dengan pesan peringatan
- Delay default 1 detik antar foto (bisa diubah di `.env`)

