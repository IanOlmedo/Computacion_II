from typing import List

from PIL import Image

from .screenshot import image_to_base64


def create_thumbnails(img: Image.Image) -> List[str]:
    """
    Crea un par de thumbnails a partir del screenshot.
    Devuelve una lista de strings base64.
    """
    sizes = [(400, 300), (200, 150)]
    thumbs_b64: List[str] = []

    for size in sizes:
        thumb = img.copy()
        thumb.thumbnail(size)
        thumbs_b64.append(image_to_base64(thumb, format="PNG"))

    return thumbs_b64
