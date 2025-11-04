#!/usr/bin/env python3
import argparse
import asyncio
import datetime as dt
import json
from typing import Any, Dict, Optional, Tuple, List

import struct

from aiohttp import web, ClientSession, ClientError
from bs4 import BeautifulSoup

# comando para instalar las librerias:
# pip install aiohttp beautifulsoup4 lxml

#nombre para el comit sobre unicamente este archivo es "Implementación del Servidor A de Scraping Asíncrono y con un servidor B s"

# Funciones de scraping

async def fetch_html(url: str, session: ClientSession, timeout: int = 30) -> Tuple[str, Dict[str, Any]]: #la funcionalidad de esta linea es definir una funcion asincrona que recibe una url, una sesion de cliente y un timeout
    """
    Descarga el HTML de una URL usando aiohttp de forma asíncrona.
    Devuelve el texto y algunos datos básicos de la respuesta.
    """
    try:
        async with session.get(url, timeout=timeout) as resp: #realiza una solicitud GET asincrónica a la URL proporcionada con un tiempo de espera especificado
            resp.raise_for_status() # Si el status es 4xx o 5xx, lanza excepción
            text = await resp.text() 
            info = {
                "status": resp.status,
                "content_type": resp.headers.get("Content-Type"), 
                "final_url": str(resp.url), 
            }
            return text, info
    except Exception as e:
        # Re-lanzamos para que lo maneje el handler
        raise RuntimeError(f"Error al descargar la página: {e}") from e


def extract_scraping_data(html: str) -> Dict[str, Any]: #recibe el html y lo devuelve en un diccionario
    """
    Parsea el HTML con BeautifulSoup y extrae:
      - título
      - links
      - meta tags relevantes
      - estructura de headers
      - cantidad de imágenes
    """
    # Podés usar "lxml" si lo tenés instalado, sino "html.parser"
    #lo que es lxml es un parser de html, que prmite analizar el html de manera mas eficiente
    #comando para

    soup = BeautifulSoup(html, "lxml")

    # Título
    if soup.title and soup.title.string:
        title = soup.title.string.strip() 
    else:
        title = None

    # Links
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a.get("href") 
        if href:
            links.append(href) 

    # Imágenes
    images = soup.find_all("img")
    images_count = len(images)

    # Estructura de headers H1-H6
    structure: Dict[str, int] = {}
    for level in range(1, 7):
        tag = f"h{level}"
        structure[tag] = len(soup.find_all(tag))

    # Meta tags relevantes
    meta_tags: Dict[str, str] = {}
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        content = meta.get("content")

        if not name or not content:
            continue

        lname = name.lower()
        if lname in ("description", "keywords") or lname.startswith("og:"): 
            meta_tags[name] = content

    return {
        "title": title,
        "links": links,
        "meta_tags": meta_tags,
        "structure": structure,
        "images_count": images_count,
    }


# Comunicación con Servidor B


async def call_processing_server(
    url: str,
    processing_host: str,
    processing_port: int,
) -> Dict[str, Any]:
    """
    Se conecta al Servidor B via TCP (socket) usando un protocolo simple:
      - Enviar: 4 bytes (longitud) + JSON con {"url": ...}
      - Recibir: 4 bytes (longitud) + JSON con los resultados

    Se usa asyncio.open_connection para no bloquear el event loop.
    """
    reader, writer = await asyncio.open_connection(
        processing_host, processing_port
    )

    try:
        # 1) Armar payload
        payload = {"url": url}
        data = json.dumps(payload).encode("utf-8")

        # 2) Mandar longitud + datos
        header = struct.pack("!I", len(data))
        writer.write(header + data)
        await writer.drain()

        # 3) Leer longitud de respuesta
        raw_len = await reader.readexactly(4)
        msg_len = struct.unpack("!I", raw_len)[0]

        # 4) Leer el cuerpo completo
        body = await reader.readexactly(msg_len)
        resp_obj = json.loads(body.decode("utf-8"))

        return resp_obj
    finally:
        writer.close()
        await writer.wait_closed()


async def handle_scrape(request: web.Request) -> web.Response:
    """
    Handler principal:
      - recibe la URL
      - hace scraping asíncrono
      - pide procesamiento extra al servidor B
      - devuelve JSON consolidado
    """
    app = request.app

    # 1) Obtener URL desde query o JSON
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

    # 2) Scraping asíncrono (con límite de workers usando un semáforo)
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

    # 3) Llamar al servidor de procesamiento (por ahora, dummy)
    processing_host: str = app["processing_host"]
    processing_port: int = app["processing_port"]

    try:
        processing_data = await call_processing_server(
            url=url,
            processing_host=processing_host,
            processing_port=processing_port,
        )
    except Exception as e:
        # Si falla el servidor B, respondemos igual con lo que tenemos
        processing_data = None

    # 4) Armar respuesta final
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

    # Podrías agregar un healthcheck
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

    # Nota: si ponés -i :: suele aceptar IPv4 e IPv6 (dual stack) dependiendo del SO
    web.run_app(app, host=args.ip, port=args.port)


if __name__ == "__main__":
    main()


#para probar el servidor, correr en terminal:
# python server_scraping.py -i 0.0.0.0 -p 8000 

# o para IPv6 / dual stack en muchos SO:
# python server_scraping.py -i :: -p 8000

# Y en otra terminal ejecutar el cliente:
# curl "http://localhost:8000/scrape?url=https://example.com" | jq


