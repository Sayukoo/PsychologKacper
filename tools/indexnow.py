#!/usr/bin/env python3
"""Zgłasza wszystkie adresy z sitemap.xml do IndexNow (Bing i wyszukiwarki partnerskie).

Uruchom PO wdrożeniu zmian na produkcję (git push), z katalogu głównego:

    python tools/indexnow.py

Wymaga, żeby plik klucza <klucz>.txt był już dostępny pod https://psychologkacper.pl/.
"""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "psychologkacper.pl"


def main() -> None:
    keys = [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    if len(keys) != 1:
        raise SystemExit("Nie znaleziono jednoznacznego pliku klucza IndexNow (32 znaki hex + .txt).")
    key = keys[0].stem
    urls = re.findall(r"<loc>(.*?)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    payload = {"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls}
    request = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"IndexNow: HTTP {response.status}, zgłoszono {len(urls)} adresów")


if __name__ == "__main__":
    main()
