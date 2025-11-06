from scraper.html_parser import extract_scraping_data


def test_extract_scraping_data_basic():
    html = """
    <html>
      <head>
        <title>Pagina de Prueba</title>
        <meta name="description" content="Descripcion de prueba">
      </head>
      <body>
        <h1>Titulo principal</h1>
        <a href="https://example.com">Link 1</a>
        <a href="https://otra.com">Link 2</a>
        <img src="img1.png" />
      </body>
    </html>
    """

    data = extract_scraping_data(html)

    assert data["title"] == "Pagina de Prueba"
    assert data["images_count"] == 1
    assert data["structure"]["h1"] == 1
    assert len(data["links"]) == 2
    assert "description" in {k.lower() for k in data["meta_tags"].keys()}
