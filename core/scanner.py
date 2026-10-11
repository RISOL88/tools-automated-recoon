"""Wrapper RustScan: subprocess execution + parsing output greppable."""

import re
import subprocess
import sys


def run_rustscan(target: str) -> str:
    """Jalankan RustScan via subprocess dengan mode greppable (-g)."""
    command = ["rustscan", "-a", target, "-g", "--ulimit", "5000"]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=True
        )
        return result.stdout
    except FileNotFoundError:
        print("[!] Error: RustScan tidak ditemukan di PATH. Pastikan rustscan sudah terinstall.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("[!] Error: RustScan timeout (lebih dari 120 detik).", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: RustScan gagal berjalan: {e.stderr.strip() or e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[!] Dibatalkan oleh user.", file=sys.stderr)
        sys.exit(130)


def parse_rustscan_output(raw_output: str) -> dict[str, list[int]]:
    """Parse output greppable RustScan format 'IP -> [port1,port2]'."""
    results: dict[str, list[int]] = {}
    pattern = re.compile(r"([^\s]+)\s*->\s*\[([0-9,\s]+)\]")

    for line in raw_output.splitlines():
        match = pattern.search(line)
        if match:
            ip = match.group(1).strip()
            raw_ports = match.group(2).strip()
            if not raw_ports:
                continue
            ports = [int(p.strip()) for p in raw_ports.split(",") if p.strip().isdigit()]
            if ports:
                results[ip] = ports

    return results
