import struct
from typing import Any

from asyncio import StreamReader, StreamWriter

from .serialization import to_json_bytes, from_json_bytes


# Estructura binaria: entero sin signo de 4 bytes big-endian
_HEADER_STRUCT = struct.Struct("!I")


# Versión asíncrona (asyncio)

async def send_message_async(writer: StreamWriter, obj: Any) -> None:
    """
    Envía un mensaje usando el protocolo:
      4 bytes de longitud + JSON en bytes.
    """
    body = to_json_bytes(obj)
    header = _HEADER_STRUCT.pack(len(body))
    writer.write(header + body)
    await writer.drain()


async def recv_message_async(reader: StreamReader) -> Any:
    """
    Recibe un mensaje usando el protocolo:
      4 bytes de longitud + JSON en bytes.
    Devuelve el objeto Python.
    """
    header_data = await reader.readexactly(_HEADER_STRUCT.size)
    (length,) = _HEADER_STRUCT.unpack(header_data)
    body = await reader.readexactly(length)
    return from_json_bytes(body)


# Versión síncrona (socketserver)

def _recvall(sock, n: int) -> bytes:
    """
    Lee exactamente n bytes desde el socket, a menos que se corte antes.
    """
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            break
        data += chunk
    return data


def send_message_sync(sock, obj: Any) -> None:
    """
    Envía un mensaje por un socket bloqueante.
    """
    body = to_json_bytes(obj)
    header = _HEADER_STRUCT.pack(len(body))
    sock.sendall(header + body)


def recv_message_sync(sock) -> Any:
    """
    Recibe un mensaje completo por un socket bloqueante
    y lo devuelve como objeto Python.
    """
    header_data = _recvall(sock, _HEADER_STRUCT.size)
    if not header_data:
        raise ConnectionError("No se pudo leer el header del mensaje")

    (length,) = _HEADER_STRUCT.unpack(header_data)

    body = _recvall(sock, length)
    if not body:
        raise ConnectionError("No se pudo leer el cuerpo del mensaje")

    return from_json_bytes(body)
