import time
from typing import Any, Dict

import requests


def analyze_performance(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Mide tiempo de carga y tamaño total descargando el contenido.
    Es una aproximación simple: una única request GET.
    """
    start = time.perf_counter()
    total_bytes = 0
    num_requests = 0

    try:
        resp = requests.get(url, stream=True, timeout=timeout)
        resp.raise_for_status()
        num_requests += 1

        for chunk in resp.iter_content(8192):
            if not chunk:
                continue
            total_bytes += len(chunk)

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        size_kb = round(total_bytes / 1024, 2)

        return {
            "load_time_ms": elapsed_ms,
            "total_size_kb": size_kb,
            "num_requests": num_requests,
        }
    except Exception as e:
        return {
            "load_time_ms": None,
            "total_size_kb": None,
            "num_requests": num_requests,
            "error": str(e),
        }
