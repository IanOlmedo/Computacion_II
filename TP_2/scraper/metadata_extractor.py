from typing import Dict

from bs4 import BeautifulSoup


def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae meta tags relevantes:
      - description
      - keywords
      - Open Graph (og:*)
    Devuelve un dict { nombre: contenido }.
    """
    meta_tags: Dict[str, str] = {}

    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        content = meta.get("content")

        if not name or not content:
            continue

        lname = name.lower()
        if lname in ("description", "keywords") or lname.startswith("og:"):
            meta_tags[name] = content

    return meta_tags
