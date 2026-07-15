# SILAKU - Sistem Layanan Administrasi Nikah KUA

Aplikasi desktop untuk sistem layanan administrasi nikah pada Kantor Urusan Agama (KUA), dibangun menggunakan Python dan CustomTkinter. Proyek ini dikembangkan untuk mata kuliah Interaksi Manusia dan Komputer (IMK).

## Fitur

- Login multi-role (Admin, Penghulu, Pengantin)
- Registrasi akun pengguna baru
- Dashboard khusus untuk masing-masing role:
  - **Admin**: kelola data pengguna, penghulu, dan pendaftaran
  - **Penghulu**: melihat jadwal dan status pendaftaran
  - **Pengantin**: mendaftar layanan pernikahan dan memantau status
- Informasi layanan KUA
- Penyimpanan data berbasis file teks (`.txt`) sebagai database sederhana

## Struktur Proyek

```
├── assets/         # Logo, gambar, komponen header & sidebar
├── dashboard/       # Dashboard untuk admin, penghulu, dan pengantin
├── database/         # Data pengguna, penghulu, dan pendaftaran (format .txt)
├── layanan/          # Modul informasi layanan
├── login.py          # Halaman login
├── register.py       # Halaman registrasi
└── main.py           # Entry point aplikasi
```

## Cara Menjalankan

1. Clone repository ini:
   ```bash
   git clone <URL_REPO_INI>
   cd Sistem_KUA_IMK
   ```

2. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```

3. Jalankan aplikasi:
   ```bash
   python main.py
   ```

## Catatan

Data pada folder `database/` merupakan data dummy/contoh untuk keperluan pengujian dan demonstrasi, bukan data pengguna nyata.

## Teknologi

- Python 3
- CustomTkinter
- Pillow (PIL)

## Mata Kuliah

Interaksi Manusia dan Komputer (IMK) — Teknik Informatika, Universitas Kuningan
