from typing import Any, Dict, List

from bs4 import BeautifulSoup

from .metadata_extractor import extract_meta_tags


def extract_scraping_data(html: str) -> Dict[str, Any]:
    """
    Parsea el HTML con BeautifulSoup y extrae:
      - título
      - links
      - meta tags relevantes
      - estructura de headers
      - cantidad de imágenes
    """
    # Podés usar "lxml" si lo tenés instalado, sino "html.parser"
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

    # Meta tags
    meta_tags = extract_meta_tags(soup)

    return {
        "title": title,
        "links": links,
        "meta_tags": meta_tags,
        "structure": structure,
        "images_count": images_count,
    }
