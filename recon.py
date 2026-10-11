#!/usr/bin/env python3
"""Mini Recon Automation Pipeline - CLI entrypoint."""

import argparse
import asyncio
import sys

from core.scanner import run_rustscan, parse_rustscan_output
from core.prober import probe_all
from core.output import print_table, save_csv, save_json


BANNER = r"""
 ____  ___  ____   ___  _     ____  _____  ____ 
|  _ \|_ _|/ ___| / _ \| |   / ___|| ____|/ ___|
| |_) || | \___ \| | | | |   \___ \|  _| | |    
|  _ < | |  ___) | |_| | |___ ___) | |___| |___ 
|_| \_\___||____/ \___/|_____|____/|_____|\____|
"""

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(
        description="Mini Recon Automation Pipeline - wrapper RustScan + HTTP probing"
    )
    parser.add_argument("target", help="Target hostname atau IP")
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=20,
        help="Jumlah request paralel (default: 20)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path file output (.csv atau .json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Tampilkan raw output RustScan untuk debug"
    )

    args = parser.parse_args()

    # Step 1: RustScan
    print(f"[*] Scanning {args.target} dengan risol...")
    raw_output = run_rustscan(args.target)

    if args.verbose:
        print("\n[DEBUG] Raw RustScan Output:")
        print(raw_output)

    # Step 2: Parse hasil
    hosts = parse_rustscan_output(raw_output)

    if not hosts:
        print(f"[!] Tidak ada port terbuka ditemukan di {args.target}")
        sys.exit(0)

    total_ports = sum(len(ports) for ports in hosts.values())
    print(f"[+] Ditemukan {len(hosts)} IP dengan {total_ports} port terbuka")

    # Step 3: HTTP Probing
    print(f"[*] Probing HTTP/HTTPS dengan concurrency {args.concurrency}...")
    results = asyncio.run(probe_all(hosts, args.concurrency))

    # Step 4: Output
    print_table(results)

    if args.output:
        if args.output.endswith(".json"):
            save_json(results, args.output)
        elif args.output.endswith(".csv"):
            save_csv(results, args.output)
        else:
            print(f"[!] Format output tidak dikenali: {args.output} (gunakan .csv atau .json)")
            sys.exit(1)
        print(f"[+] Hasil disimpan ke {args.output}")


if __name__ == "__main__":
    main()
