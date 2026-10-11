# Mini Recon Automation Pipeline

Tools recon otomatis berbasis CLI yang mengkombinasikan **RustScan** (port scanning ultra-cepat) dan **HTTP Probing** (async via `httpx`) ke dalam satu pipeline sederhana.

Output ditampilkan rapi dalam tabel bermotif CLI modern di terminal menggunakan `rich`, serta mendukung penyimpan hasil ke format CSV atau JSON.

---

## Prasyarat

- **Python 3.10+**
- **RustScan** (harus terpasang di system PATH)

---

## Cara Install

1. Clone repositori ini dan masuk ke direktori project:
```bash
git clone <repository_url>
cd mini-recon-automation
```

2. Buat dan aktifkan virtual environment (jika belum):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependency:
```bash
pip install -r requirements.txt
```

---

## Cara Pemakaian

### 1. Scan Dasar
Melakukan port scan dan HTTP probe ke target:
```bash
python recon.py scanme.nmap.org
```

### 2. Kustomisasi Concurrency
Mengatur jumlah request HTTP probing paralel (default: 20):
```bash
python recon.py scanme.nmap.org -c 50
```

### 3. Simpan Hasil ke JSON atau CSV
Menyimpan hasil probing ke file `.json` atau `.csv`:
```bash
python recon.py scanme.nmap.org -o hasil.json
python recon.py scanme.nmap.org -o hasil.csv
```

### 4. Mode Verbose (Debug)
Menampilkan raw output dari RustScan untuk keperluan debugging:
```bash
python recon.py scanme.nmap.org -v
```

---

## Struktur Modul

- `recon.py`: Entrypoint CLI parser & pengatur alur pipeline
- `core/scanner.py`: Modul wrapper & parser output RustScan
- `core/prober.py`: Modul HTTP probing (async)
- `core/output.py`: Modul pemformat tabel terminal (`rich`) & writer (CSV/JSON)

---

## Disclaimer

Tools ini dibuat untuk tujuan edukasi dan pengujian keamanan yang sah (authorized testing) saja. Gunakan hanya pada target yang sudah mendapat izin eksplisit. Penulis tidak bertanggung jawab atas penyalahgunaan tools ini.
