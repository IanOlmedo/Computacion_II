import asyncio
from typing import Any, Dict, Tuple

from aiohttp import ClientSession


async def fetch_html(
    url: str,
    session: ClientSession,
    timeout: int = 30
) -> Tuple[str, Dict[str, Any]]:
    """
    Descarga el HTML de una URL usando aiohttp de forma asíncrona.
    Devuelve el texto y algunos datos básicos de la respuesta.
    """
    try:
        async with session.get(url, timeout=timeout) as resp:
            resp.raise_for_status()
            text = await resp.text()
            info = {
                "status": resp.status,
                "content_type": resp.headers.get("Content-Type"),
                "final_url": str(resp.url),
            }
            return text, info
    except Exception as e:
        # Re-lanzamos para que lo maneje quien llama
        raise RuntimeError(f"Error al descargar la página: {e}") from e
