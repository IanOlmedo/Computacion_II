import argparse
import json
import socket
import struct
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict

import socketserver

from processor.screenshot import generate_dummy_screenshot, image_to_base64
from processor.image_processor import create_thumbnails
from processor.performance import analyze_performance
from common.protocol import send_message_sync, recv_message_sync


# Pool de procesos (se inicializa en main)
PROCESS_POOL: ProcessPoolExecutor | None = None


# Lógica de procesamiento (worker)

def process_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función que corre en un proceso del pool.
    Recibe un dict con al menos 'url' y devuelve
    los datos de procesamiento.
    """
    url = payload.get("url")
    if not url:
        return {
            "status": "error",
            "error": "Falta campo 'url' en el payload",
        }

    # Screenshot dummy
    screenshot_img = generate_dummy_screenshot(url)
    screenshot_b64 = image_to_base64(screenshot_img)

    # Thumbnails
    thumbnails_b64 = create_thumbnails(screenshot_img)

    # Análisis de rendimiento
    performance_info = analyze_performance(url)

    return {
        "status": "success",
        "screenshot": screenshot_b64,
        "performance": performance_info,
        "thumbnails": thumbnails_b64,
    }


# Servidor TCP con socketserver
class ProcessingTCPHandler(socketserver.BaseRequestHandler):
    """
    Handler que:
      - recibe un mensaje (protocolo común)
      - ejecuta process_task en el pool de procesos
      - devuelve la respuesta con el mismo protocolo
    """

    def handle(self) -> None:
        global PROCESS_POOL
        if PROCESS_POOL is None:
            return

        try:
            # 1) Recibir payload desde el Servidor A
            payload = recv_message_sync(self.request)

            # 2) Enviar al pool de procesos
            future = PROCESS_POOL.submit(process_task, payload)
            result = future.result()

            # 3) Devolver respuesta
            send_message_sync(self.request, result)

        except Exception as e:
            # Enviar mensaje de error usando el mismo protocolo
            try:
                error_obj = {
                    "status": "error",
                    "error": str(e),
                }
                send_message_sync(self.request, error_obj)
            except Exception:
                # Si falla incluso el envío de error, no hay mucho más que hacer
                pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


# CLI y main

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Servidor de Procesamiento Distribuido"
    )
    parser.add_argument(
        "-i", "--ip",
        required=True,
        help="Dirección de escucha (IPv4 o IPv6)",
    )
    parser.add_argument(
        "-p", "--port",
        required=True,
        type=int,
        help="Puerto de escucha",
    )
    parser.add_argument(
        "-n", "--processes",
        type=int,
        default=None,
        help="Número de procesos en el pool (default: CPU count)",
    )
    return parser.parse_args()


def main() -> None:
    global PROCESS_POOL
    args = parse_args()

    PROCESS_POOL = ProcessPoolExecutor(max_workers=args.processes)

    # Elegir IPv4 o IPv6 según la IP
    server_cls = ThreadedTCPServer
    if ":" in args.ip:
        class ThreadedTCPServerV6(ThreadedTCPServer):
            address_family = socket.AF_INET6
        server_cls = ThreadedTCPServerV6

    with server_cls((args.ip, args.port), ProcessingTCPHandler) as server:
        print(f"[Servidor B] Escuchando en {args.ip}:{args.port} "
              f"con pool de procesos (max_workers={args.processes})")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[Servidor B] Apagando...")
        finally:
            PROCESS_POOL.shutdown(wait=True)


if __name__ == "__main__":
    main()

"""Comando de ejecucion para cualquier IP y puerto 9000:

Terminal 1: python server_processing.py -i ::1 -p 9000 -n 4

Terminal 2: python server_scraping.py \
            -i :: \
            -p 8000 \
            --processing-ip ::1 \
            --processing-port 9000

curl -g "http://[::1]:8000/scrape?url=https://example.com" | jq            
            """

