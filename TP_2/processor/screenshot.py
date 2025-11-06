from io import BytesIO

from PIL import Image, ImageDraw
import base64


def generate_dummy_screenshot(url: str) -> Image.Image:
    """
    Genera una imagen PNG simple con el texto de la URL.
    """
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    text = f"Screenshot of:\n{url}"
    draw.text((20, 20), text, fill=(0, 0, 0))

    return img


def image_to_base64(img: Image.Image, format: str = "PNG") -> str:
    buf = BytesIO()
    img.save(buf, format=format)
    data = buf.getvalue()
    return base64.b64encode(data).decode("ascii")
