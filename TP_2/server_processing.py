import argparse
import base64
import json
import struct
import time
from concurrent.futures import ProcessPoolExecutor 
from io import BytesIO
from typing import Any, Dict

import socket

import requests
import socketserver
from PIL import Image, ImageDraw


# Pool de procesos (se inicializa en main)
PROCESS_POOL: ProcessPoolExecutor | None = None


# Lógica de procesamiento (worker)

def generate_dummy_screenshot(url: str) -> Image.Image:
    
   # Genera una imagen PNG simple con el texto de la URL.

    width, height = 800, 600
    img = Image.new("RGB", (width, height), color=(255, 255, 255)) 
    draw = ImageDraw.Draw(img) 

    text = f"Screenshot of:\n{url}"
    draw.text((20, 20), text, fill=(0, 0, 0))

    return img


def image_to_base64(img: Image.Image, format: str = "PNG") -> str: # Convierte una imagen PIL a base64. 
    buf = BytesIO() 
    img.save(buf, format=format)
    data = buf.getvalue() 
    return base64.b64encode(data).decode("ascii") # Devuelve string base64


def create_thumbnails(img: Image.Image) -> list[str]:
 
    #Crea un par de thumbnails a partir del screenshot.
    #un thumbnail es una version reducida de una imagen 

    sizes = [(400, 300), (200, 150)] 
    thumbs_b64: list[str] = []

    for size in sizes:
        thumb = img.copy()
        thumb.thumbnail(size) 
        thumbs_b64.append(image_to_base64(thumb, format="PNG"))

    return thumbs_b64


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
        # Si falla, devolvemos info mínima
        return {
            "load_time_ms": None,
            "total_size_kb": None,
            "num_requests": num_requests,
            "error": str(e),
        }


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
      - lee un mensaje (longitud + JSON)
      - ejecuta process_task en el pool de procesos
      - devuelve (longitud + JSON) con los resultados
    """

    def handle(self) -> None:
        global PROCESS_POOL
        if PROCESS_POOL is None:
            # Esto no debería pasar si se inicializa bien en main
            return

        try:
            # 1) Leer longitud (4 bytes, entero sin signo big-endian)
            raw_len = self._recvall(4) 
            if not raw_len:
                return
            msg_len = struct.unpack("!I", raw_len)[0] # longitud del mensaje

            # 2) Leer el mensaje completo
            data = self._recvall(msg_len)
            if not data:
                return

            payload = json.loads(data.decode("utf-8"))

            # 3) Enviar al pool de procesos
            future = PROCESS_POOL.submit(process_task, payload) 
            result = future.result()

            # 4) Serializar respuesta
            response_bytes = json.dumps(result).encode("utf-8")
            response_len = struct.pack("!I", len(response_bytes))

            # 5) Enviar longitud + mensaje
            self.request.sendall(response_len + response_bytes)

        except Exception as e:
            # Ante error, intentamos enviar un mensaje de error
            try:
                error_obj = {
                    "status": "error",
                    "error": str(e),
                }
                resp = json.dumps(error_obj).encode("utf-8")
                self.request.sendall(struct.pack("!I", len(resp)) + resp)
            except Exception:
                # Si también falla, ya no podemos hacer mucho más
                pass

    def _recvall(self, n: int) -> bytes:
        """
        Lee exactamente n bytes desde el socket, a menos que se corte antes.
        """
        data = b"" 
        while len(data) < n:
            chunk = self.request.recv(n - len(data))
            if not chunk:
                break
            data += chunk
        return data


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # Permite reusar dirección rápidamente al reiniciar el server
    allow_reuse_address = True


# ==============================
# CLI y main
# ==============================

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

#main para direcciones IPv4
"""def main() -> None:
    global PROCESS_POOL
    args = parse_args()

    # Inicializar pool de procesos
    PROCESS_POOL = ProcessPoolExecutor(max_workers=args.processes)

    with ThreadedTCPServer((args.ip, args.port), ProcessingTCPHandler) as server:
        print(f"[Servidor B] Escuchando en {args.ip}:{args.port} "
              f"con pool de procesos (max_workers={args.processes})")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[Servidor B] Apagando...")
        finally:
            PROCESS_POOL.shutdown(wait=True)
"""


#main para direcciones IPv4 o IPv6
def main() -> None:
    global PROCESS_POOL
    args = parse_args()

    # Inicializar pool de procesos
    PROCESS_POOL = ProcessPoolExecutor(max_workers=args.processes)

    # Elegir IPv4 o IPv6 según la IP pasada
    server_cls = ThreadedTCPServer

    if ":" in args.ip:
        # IPv6
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