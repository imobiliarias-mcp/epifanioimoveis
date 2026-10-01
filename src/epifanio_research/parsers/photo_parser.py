"""Parser for property photo gallery endpoints and fallback HTML."""

import json
from bs4 import BeautifulSoup
from epifanio_research.domain.property import PhotoGallery


class PhotoGalleryParser:
    """Parses AJAX photo gallery JSON responses and HTML gallery fallbacks."""

    IMAGE_BASE_URL = "https://www.epifanioimoveis.com/imagens/imoveis"

    def parse_ajax_json(self, raw_json: str) -> PhotoGallery:
        """Parse JSON response from /t27/lista_imoveis_fotos.php."""
        if not raw_json.strip():
            return PhotoGallery()
        try:
            data = json.loads(raw_json)
            return self._build_gallery_from_dict(data)
        except json.JSONDecodeError:
            return PhotoGallery()

    def parse_html_fallback(self, html: str) -> PhotoGallery:
        """Fallback parser extracting images from page markup."""
        soup = BeautifulSoup(html, "html.parser")
        images: list[str] = []
        for img in soup.find_all("img"):
            src = img.get("src") or ""
            if "/imagens/imoveis/" in src and "li5.php" not in src:
                images.append(src)
        return PhotoGallery(photo_urls=tuple(dict.fromkeys(images)))

    def _build_gallery_from_dict(self, data: dict[str, any]) -> PhotoGallery:
        """Convert parsed photo dictionary to PhotoGallery."""
        urls: list[str] = []
        for item in data.values():
            if isinstance(item, dict) and "arquivo_imm" in item:
                file_name = item["arquivo_imm"]
                urls.append(f"{self.IMAGE_BASE_URL}/{file_name}")
        return PhotoGallery(photo_urls=tuple(urls))
