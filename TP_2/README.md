# TP2 - Sistema de Scraping y Análisis Web Distribuido

**Materia**: Computación II  
**Alumno**: Ian Olmedo  
**Fecha de entrega**: 14/11/2025

---

## Descripción General

El trabajo implementa un sistema distribuido compuesto por dos servidores:

- **Servidor A (server_scraping.py)**  
  - Servidor HTTP asíncrono construido con `aiohttp` y `asyncio`.
  - Recibe URLs desde clientes vía `/scrape`.
  - Realiza scraping de la página:
    - Título
    - Links
    - Meta tags (description, keywords, Open Graph)
    - Estructura de headers H1–H6
    - Cantidad de imágenes
  - Se comunica de forma transparente con el Servidor B para tareas de procesamiento pesado.
  - Devuelve un JSON consolidado al cliente.

- **Servidor B (server_processing.py)**  
  - Servidor TCP basado en `socketserver` y `multiprocessing` (pool de procesos).
  - Recibe peticiones desde el Servidor A mediante un protocolo binario (4 bytes de longitud + JSON).
  - Ejecuta, en procesos separados:
    - Generación de screenshot dummy (imagen PNG con la URL).
    - Análisis de rendimiento (tiempo de carga, tamaño total del contenido).
    - Generación de thumbnails a partir del screenshot.
  - Devuelve resultados al Servidor A por el mismo socket.

El cliente solo interactúa con el **Servidor A**, por lo que todo el sistema es transparente desde su punto de vista.

---

## Requerimientos

```bash
pip install aiohttp beautifulsoup4 lxml requests pillow
```

Opcionalmente, instalar jq para formatear respuestas JSON desde la terminal:
```bash
sudo apt install jq
```

## Ejecución del Sistema
* Iniciar el Servidor de Procesamiento (Servidor B)

```bash
cd TP2
python server_processing.py -i 127.0.0.1 -p 9000 -n 4
```

Ejemplo con IPv6
```bash
python server_processing.py -i ::1 -p 9000 -n 4
```
* Iniciar el Servidor de Scraping (Servidor A)

```bash
python server_scraping.py \
  -i 0.0.0.0 \
  -p 8000 \
  --processing-ip 127.0.0.1 \
  --processing-port 9000
```
Ejemplo con IPv6

```bash 
python server_scraping.py \
  -i :: \
  -p 8000 \
  --processing-ip ::1 \
  --processing-port 9000
```

* Cliente de Prueba

```bash
python client.py https://example.com
```
Opcional con parametros especificos

```bash
python client.py -i 127.0.0.1 -p 8000 https://www.python.org
```

* Formato de Respuesta JSON

Ejemplo de respuesta completa al hacer:
```bash 
curl "http://localhost:8000/scrape?url=https://example.com" | jq
```
Respuesta esperada:

```bash
{
  "url": "https://example.com",
  "timestamp": "2025-11-06T13:00:00Z",
  "scraping_data": {
    "title": "Example Domain",
    "links": ["https://www.iana.org/domains/example"],
    "meta_tags": {
      "description": "Example Domain"
    },
    "structure": {
      "h1": 1,
      "h2": 0,
      "h3": 0,
      "h4": 0,
      "h5": 0,
      "h6": 0
    },
    "images_count": 0
  },
  "processing_data": {
    "status": "success",
    "screenshot": "iVBORw0KGgoAAAANSUhEUgAA...",
    "performance": {
      "load_time_ms": 230,
      "total_size_kb": 12.34,
      "num_requests": 1
    },
    "thumbnails": ["iVBORw0K...", "iVBORw0K..."]
  },
  "status": "success",
  "extra_info": {
    "http_response": {
      "status": 200,
      "content_type": "text/html; charset=UTF-8",
      "final_url": "https://example.com/"
    }
  }
}

```

Funcionamiento Interno

El cliente envía la solicitud HTTP a /scrape con la URL.

El Servidor A:
Descarga el HTML con aiohttp (asíncrono). 
Analiza la estructura con BeautifulSoup. 
Extrae título, links, meta tags, headers e imágenes. 
Abre un socket TCP con el Servidor B y le envía la URL en formato binario (4 bytes de longitud + JSON).

El Servidor B:
Recibe la URL. 
Ejecuta process_task en un proceso del pool. 
Genera una imagen PNG con el texto de la URL (screenshot dummy). 
Calcula métricas de rendimiento descargando el contenido. 
Devuelve el resultado serializado a JSON. 
 
El Servidor A:
Espera de forma asíncrona la respuesta del Servidor B. 
Consolida todos los datos en un único JSON. 
Devuelve el resultado al cliente.