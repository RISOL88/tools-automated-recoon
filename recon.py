# PRD — Mini Recon Automation Pipeline

## 1. Overview
ktop maupun web app — murni CLI.
- Bukan pengganti RustScan/httpx, melainkan wrapper/orchestrator di atasnya.
- Tidak melakukan exploitation — hanya recon & pengumpulan informasi.

## 2. Tech Stack

| Kebutuhan | Pilihan | Alasan |
|---|---|---|
| Port scanning | RustScan (external binary, dipanggil via `subprocess`) | Sudah dipakai, cepat |
| HTTP probing | `httpx` (Python library, async) | Modern, support async untuk concurrency |
| CLI argument parsing | `argparse` (built-in) | Standar di tools security, tidak perlu dependency tambahan |
| Output terminal | `rich` | Tabel & warna, UX mirip tools pentest profesional |
| Concurrency | `asyncio` + `httpx.AsyncClient` | Biar probing banyak host/port tidak lambat sekuensial |
| Output file | `csv`, `json` (built-in) | Portable, gampang diproses tools lain |

## 3. Struktur Proyek

```
mini-recon-automation/
├── venv/                  (sudah ada, jangan disentuh/di-commit)
├── recon.py                <- entrypoint utama (CLI)
├── core/
│   ├── __init__.py
│   ├── scanner.py          <- wrapper RustScan (subprocess + parsing)
│   ├── prober.py           <- HTTP probing pakai httpx (async)
│   └── output.py           <- formatting rich table + writer CSV/JSON
├── requirements.txt         (sudah ada)
├── README.MD                (sudah ada, isi nanti di step terakhir)
└── .gitignore               <- tambahkan venv/, __pycache__/, *.csv, *.json (hasil scan)
```

## 4. Alur Data (Pipeline)

```
[target input] 
   -> RustScan (subprocess, greppable output -g)
   -> parse jadi { ip: [ports] }
   -> bentuk list URL kandidat (http/https per ip:port)
   -> httpx async probe -> status_code, title, server header
   -> gabungkan hasil per host
   -> tampilkan rich table di terminal
   -> (opsional) simpan ke CSV/JSON
```

## 5. Spesifikasi Fungsional per Modul

### 5.1 `core/scanner.py`
- Fungsi `run_rustscan(target: str) -> str` — jalankan RustScan via `subprocess.run`, mode greppable (`-g`), `--ulimit 5000`, timeout 120 detik, tangani `FileNotFoundError` dan `TimeoutExpired`.
- Fungsi `parse_rustscan_output(raw_output: str) -> dict[str, list[int]]` — parse baris format `ip -> [port1,port2,...]` pakai regex.

### 5.2 `core/prober.py`
- Fungsi async `probe_host(client: httpx.AsyncClient, ip: str, port: int) -> dict` — coba `https://` dulu, fallback `http://` kalau gagal; ambil `status_code`, `title` (parse dari `<title>` di body, boleh regex sederhana, tidak perlu library HTML parser tambahan), `server` header. Timeout per-request 5 detik, gagal = catat status "unreachable", jangan crash seluruh pipeline.
- Fungsi async `probe_all(hosts: dict[str, list[int]], concurrency: int) -> list[dict]` — pakai `asyncio.Semaphore(concurrency)` untuk batasi jumlah request paralel, jalankan semua `probe_host` via `asyncio.gather`.

### 5.3 `core/output.py`
- Fungsi `print_table(results: list[dict])` — pakai `rich.table.Table`, kolom: IP, Port, Status, Title, Server.
- Fungsi `save_csv(results: list[dict], path: str)`.
- Fungsi `save_json(results: list[dict], path: str)`.

### 5.4 `recon.py` (entrypoint)
- `argparse` dengan argumen:
  - `target` (positional, wajib) — hostname/IP tunggal.
  - `-c / --concurrency` (default 20) — jumlah request paralel ke httpx.
  - `-o / --output` (optional) — path file output, ekstensi `.csv` atau `.json` menentukan formatnya.
  - `-v / --verbose` (flag) — tampilkan raw output RustScan untuk debug.
- Alur `main()`: panggil scanner → prober → output, sesuai pipeline di bagian 4.

## 6. Error Handling & Edge Cases (wajib ditangani)

- RustScan tidak ditemukan di PATH → pesan jelas, exit code 1, jangan traceback mentah ke user.
- Target tidak punya port terbuka sama sekali → tampilkan pesan informatif, bukan tabel kosong tanpa penjelasan.
- Host hidup di port tapi bukan HTTP/HTTPS (misal SSH port 22) → tetap dicatat dengan status "non-http", jangan bikin probe gagal/crash.
- Timeout per individual probe tidak boleh menghentikan keseluruhan pipeline (satu host lambat tidak boleh nge-block yang lain).

## 7. Kriteria Selesai (Definition of Done)

- `python recon.py scanme.nmap.org` berjalan end-to-end tanpa error, menghasilkan tabel rapi di terminal.
- `python recon.py scanme.nmap.org -o hasil.json` menghasilkan file JSON valid berisi semua hasil probe.
- Kode terbagi rapi sesuai struktur di bagian 3 (tidak semua logic numpuk di `recon.py`).
- Semua fungsi publik (bukan helper internal) punya docstring singkat.

---

## 8. Instruksi Eksekusi untuk AI Agent

**ATURAN WAJIB:**
- Kerjakan **satu step saja**, lalu **BERHENTI** dan tunggu konfirmasi/review dari user sebelum lanjut ke step berikutnya.
- Jangan menggabungkan dua step jadi satu commit/perubahan besar.
- Jangan mengubah file di luar scope step yang sedang dikerjakan.
- Jangan install dependency baru yang tidak disebut di PRD ini tanpa izin eksplisit.
- Setiap step selesai, laporkan singkat: apa yang dibuat/diubah, dan cara user mengetesnya sendiri.

### Step 1 — Setup struktur folder
Buat struktur folder `core/` dengan `__init__.py`, `scanner.py`, `prober.py`, `output.py` (boleh kosong/berisi docstring placeholder dulu). Tambahkan `.gitignore`. **Jangan isi logic apapun di step ini.** BERHENTI setelah struktur folder dibuat.

### Step 2 — Implementasi `core/scanner.py`
Implementasikan `run_rustscan()` dan `parse_rustscan_output()` sesuai spesifikasi bagian 5.1. Sertakan error handling dari bagian 6 yang relevan. BERHENTI setelah modul ini selesai — user akan test manual dulu sebelum lanjut.

### Step 3 — Implementasi `core/prober.py`
Implementasikan `probe_host()` dan `probe_all()` sesuai spesifikasi bagian 5.2, termasuk fallback https/http dan penanganan timeout per-host. BERHENTI setelah modul ini selesai.

### Step 4 — Implementasi `core/output.py`
Implementasikan `print_table()`, `save_csv()`, `save_json()` sesuai bagian 5.3. BERHENTI setelah modul ini selesai.

### Step 5 — Implementasi `recon.py` (entrypoint)
Gabungkan Step 2–4 menjadi pipeline utuh sesuai bagian 5.4 dan alur data di bagian 4. BERHENTI setelah entrypoint selesai — ini milestone penting, user akan test end-to-end.

### Step 6 — Verifikasi Definition of Done
Jalankan/cek ulang semua kriteria di bagian 7 satu per satu, laporkan status masing-masing (lulus/tidak). Jangan memperbaiki apapun di step ini kecuali diminta — cukup laporkan hasil cek. BERHENTI setelah laporan diberikan.

### Step 7 — Dokumentasi README.MD
Isi `README.MD` dengan: deskripsi singkat tools, cara install (`venv` + `pip install -r requirements.txt`), contoh pemakaian (beberapa variasi command dari bagian 5.4). BERHENTI setelah selesai — ini step terakhir.

---

## 9. Catatan Tambahan

- Project ini adalah **Tahap 1–4** dari rencana pengembangan yang lebih besar (lihat roadmap terpisah untuk Tahap 5 concurrency lanjutan, Tahap 6 CLI argumen lanjutan, Tahap 7 diff/tracking). PRD ini **tidak mencakup** tahap 5–7 — jangan dikerjakan kecuali ada PRD/instruksi tambahan.
- Kode wajib bisa dibaca dan dipahami oleh pemula Python (penulis PRD ini masih belajar dasar Python) — hindari pattern yang terlalu advanced/magic tanpa penjelasan di komentar.
