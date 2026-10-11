"""HTTP probing pakai httpx (async)."""

import re
import asyncio
import httpx


async def probe_host(client: httpx.AsyncClient, ip: str, port: int) -> dict:
    """Probe satu host:port, coba HTTPS dulu lalu fallback HTTP."""
    result = {
        "ip": ip,
        "port": port,
        "status": "unreachable",
        "title": "",
        "server": ""
    }

    for scheme in ("https", "http"):
        url = f"{scheme}://{ip}:{port}"
        try:
            resp = await client.get(url, timeout=5.0, follow_redirects=True)
            result["status"] = str(resp.status_code)
            result["server"] = resp.headers.get("server", "")
            # ambil title dari body pakai regex sederhana
            title_match = re.search(r"<title[^>]*>([^<]+)</title>", resp.text, re.IGNORECASE)
            if title_match:
                result["title"] = title_match.group(1).strip()
            return result
        except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError):
            continue

    # kalau bukan HTTP/HTTPS (misal SSH), cek apakah port terbuka via TCP
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=5.0
        )
        writer.close()
        await writer.wait_closed()
        result["status"] = "non-http"
    except Exception:
        pass

    return result


async def probe_all(hosts: dict[str, list[int]], concurrency: int) -> list[dict]:
    """Probe semua host:port dengan semaphore untuk batasi concurrency."""
    semaphore = asyncio.Semaphore(concurrency)
    results: list[dict] = []

    async with httpx.AsyncClient(verify=False) as client:
        async def probe_with_sem(ip: str, port: int):
            async with semaphore:
                return await probe_host(client, ip, port)

        tasks = [
            probe_with_sem(ip, port)
            for ip, ports in hosts.items()
            for port in ports
        ]
        results = await asyncio.gather(*tasks)

    return results