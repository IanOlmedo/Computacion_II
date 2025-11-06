
import argparse
import asyncio
import datetime as dt
import json
import struct
from typing import Any, Dict, Optional

from aiohttp import web, ClientSession

from scraper.async_http import fetch_html
from scraper.html_parser import extract_scraping_data
from common.protocol import send_message_async, recv_message_async


# Comunicación con Servidor B

async def call_processing_server(
    url: str,
    processing_host: str,
    processing_port: int,
) -> Dict[str, Any]:
    """
    Se conecta al Servidor B via TCP (socket) usando el protocolo común:
      - 4 bytes de longitud + JSON serializado.
    """
    reader, writer = await asyncio.open_connection(
        processing_host, processing_port
    )

    try:
        payload = {"url": url}
        # Enviar mensaje usando protocolo común
        await send_message_async(writer, payload)

        # Recibir respuesta
        resp_obj = await recv_message_async(reader)
        return resp_obj
    finally:
        writer.close()
        await writer.wait_closed()

# Handler HTTP

async def handle_scrape(request: web.Request) -> web.Response:
    """
    Handler principal:
      - recibe la URL
      - hace scraping asíncrono
      - pide procesamiento extra al servidor B
      - devuelve JSON consolidado
    """
    app = request.app

    #  Obtener URL desde query o JSON
    url: Optional[str] = request.rel_url.query.get("url")

    if not url and request.method in ("POST", "PUT"):
        try:
            data = await request.json()
            url = data.get("url")
        except json.JSONDecodeError:
            url = None

    if not url:
        return web.json_response(
            {
                "status": "error",
                "error": "Falta parámetro 'url' (query ?url=... o JSON {'url': ...})"
            },
            status=400,
        )

    #  Scraping asíncrono (con límite de workers usando un semáforo)
    session: ClientSession = app["http_session"]
    semaphore: asyncio.Semaphore = app["semaphore"]

    try:
        async with semaphore:
            html, resp_info = await fetch_html(url, session=session)
            scraping_data = extract_scraping_data(html)
    except RuntimeError as e:
        return web.json_response(
            {
                "status": "error",
                "error": str(e),
            },
            status=502,
        )

    #  Llamar al servidor de procesamiento
    processing_host: str = app["processing_host"]
    processing_port: int = app["processing_port"]

    try:
        processing_data = await call_processing_server(
            url=url,
            processing_host=processing_host,
            processing_port=processing_port,
        )
    except Exception:
        # Si falla el servidor B, respondemos igual con lo que tenemos
        processing_data = None

    #  Armar respuesta final
    now_utc = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    result: Dict[str, Any] = {
        "url": url,
        "timestamp": now_utc,
        "scraping_data": scraping_data,
        "processing_data": processing_data,
        "status": "success",
        "extra_info": {
            "http_response": resp_info,
        },
    }

    return web.json_response(result, status=200)


# Creación de la app y CLI

def create_app(
    workers: int,
    processing_host: str,
    processing_port: int,
) -> web.Application:
    """
    Crea la aplicación aiohttp, registra rutas y maneja recursos compartidos.
    """
    app = web.Application()

    # Config global
    app["workers"] = workers
    app["processing_host"] = processing_host
    app["processing_port"] = processing_port
    app["semaphore"] = asyncio.Semaphore(workers)

    async def on_startup(app: web.Application) -> None:
        app["http_session"] = ClientSession()

    async def on_cleanup(app: web.Application) -> None:
        session: ClientSession = app["http_session"]
        await session.close()

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # Rutas
    app.router.add_get("/scrape", handle_scrape)
    app.router.add_post("/scrape", handle_scrape)

    async def health(request: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "service": "server_scraping"})

    app.router.add_get("/health", health)

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Servidor de Scraping Web Asíncrono"
    )
    parser.add_argument(
        "-i", "--ip",
        required=True,
        help="Dirección de escucha (IPv4 o IPv6, ej: 0.0.0.0 o ::)",
    )
    parser.add_argument(
        "-p", "--port",
        required=True,
        type=int,
        help="Puerto de escucha",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=4,
        help="Número máximo de tareas de scraping concurrentes (default: 4)",
    )
    parser.add_argument(
        "--processing-ip",
        default="127.0.0.1",
        help="IP del servidor de procesamiento (Servidor B)",
    )
    parser.add_argument(
        "--processing-port",
        type=int,
        default=9000,
        help="Puerto del servidor de procesamiento (Servidor B)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    app = create_app(
        workers=args.workers,
        processing_host=args.processing_ip,
        processing_port=args.processing_port,
    )

    web.run_app(app, host=args.ip, port=args.port)


if __name__ == "__main__":
    main()


#para probar el servidor, correr en terminal:
# python server_scraping.py -i 0.0.0.0 -p 8000 

# o para IPv6 / dual stack en muchos SO:
# python server_scraping.py -i :: -p 8000

# Y en otra terminal ejecutar el cliente:
# curl "http://localhost:8000/scrape?url=https://example.com" | jq
