#!/usr/bin/env python3
import argparse
import json
from typing import Any, Dict

import requests


def parse_args() -> argparse.Namespace: 
    parser = argparse.ArgumentParser(
        description="Cliente de prueba para el TP2 (Servidor de Scraping)"
    )
    parser.add_argument(
        "-i", "--ip",
        default="127.0.0.1",
        help="IP del servidor de scraping (Servidor A)",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8000,
        help="Puerto del servidor de scraping (Servidor A)",
    )
    parser.add_argument(
        "url",
        help="URL a analizar (ej: https://example.com)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    base_url = f"http://{args.ip}:{args.port}"
    endpoint = f"{base_url}/scrape"

    params = {"url": args.url}

    print(f"[CLIENT] Enviando URL al servidor A: {args.url}")
    try:
        resp = requests.get(endpoint, params=params, timeout=60)
    except Exception as e:
        print(f"[CLIENT] Error de red al conectar con el servidor A: {e}")
        return

    print(f"[CLIENT] Código de respuesta HTTP: {resp.status_code}")

    try:
        data: Dict[str, Any] = resp.json()
    except json.JSONDecodeError:
        print("[CLIENT] La respuesta no es JSON:")
        print(resp.text)
        return

    # Mostrar un pequeño resumen de los resultados
    status = data.get("status")
    print(f"[CLIENT] Status general: {status}")

    scraping = data.get("scraping_data") or {}
    processing = data.get("processing_data") or {}

    print("\n=== SCRAPING DATA ===")
    print(f"Título: {scraping.get('title')}")
    print(f"Cantidad de links: {len(scraping.get('links') or [])}")
    print(f"Cantidad de imágenes: {scraping.get('images_count')}")
    structure = scraping.get("structure") or {}
    print(f"Estructura H1-H6: {structure}")

    print("\n=== PROCESSING DATA ===")
    perf = processing.get("performance") or {}
    print(f"Tiempo de carga (ms): {perf.get('load_time_ms')}")
    print(f"Tamaño total (KB): {perf.get('total_size_kb')}")
    print(f"Número de requests: {perf.get('num_requests')}")

    # Avisar si vino screenshot
    screenshot = processing.get("screenshot")
    if screenshot:
        print("\n[CLIENT] Se recibió un screenshot en base64 (no se muestra por consola).")
    else:
        print("\n[CLIENT] No se recibió screenshot.")


if __name__ == "__main__":
    main()


"""```bash
pip install aiohttp beautifulsoup4 lxml requests pillow
```


"""