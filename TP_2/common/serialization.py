import json
from typing import Any


def to_json_bytes(obj: Any) -> bytes:
    """
    Serializa un objeto Python (por ejemplo un dict) a JSON en bytes UTF-8.
    """
    return json.dumps(obj).encode("utf-8")


def from_json_bytes(data: bytes) -> Any:
    """
    Deserializa bytes UTF-8 que contienen JSON a un objeto Python.
    """
    return json.loads(data.decode("utf-8"))
