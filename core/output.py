"""Formatting rich table + writer CSV/JSON."""

import csv
import json
from rich.console import Console
from rich.table import Table


def print_table(results: list[dict]) -> None:
    """Tampilkan hasil probe dalam bentuk rich table."""
    if not results:
        return

    table = Table(title="Recon Results")
    table.add_column("IP", style="cyan")
    table.add_column("Port", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Title", style="yellow")
    table.add_column("Server", style="blue")

    for row in results:
        table.add_row(
            row.get("ip", ""),
            str(row.get("port", "")),
            row.get("status", ""),
            row.get("title", ""),
            row.get("server", "")
        )

    console = Console()
    console.print(table)


def save_csv(results: list[dict], path: str) -> None:
    """Simpan hasil ke CSV."""
    if not results:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ip", "port", "status", "title", "server"])
        writer.writeheader()
        writer.writerows(results)


def save_json(results: list[dict], path: str) -> None:
    """Simpan hasil ke JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
