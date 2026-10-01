"""Parser for property detail web pages combining HTML and JSON-LD."""

import json
import re
from bs4 import BeautifulSoup
from epifanio_research.domain.property import (
    PhotoGallery,
    PropertyDetail,
    PropertyLocation,
    PropertyOverview,
    PropertyPricing,
    PropertySpecs,
)


class PropertyDetailParser:
    """Extracts rich property details from detail page markup and microdata."""

    def parse(self, html: str, property_id: str, canonical_url: str = "") -> PropertyDetail:
        """Parse raw HTML and assemble PropertyDetail entity."""
        soup = BeautifulSoup(html, "html.parser")
        ld_data = self._extract_json_ld(soup)
        overview = self._parse_overview(soup, property_id)
        pricing = self._parse_pricing(soup, ld_data)
        location = self._parse_location(soup, ld_data)
        specs = self._parse_specs(soup)
        chars = self._parse_characteristics(soup)
        photos = self._extract_embedded_photos(soup)
        return PropertyDetail(
            overview=overview,
            pricing=pricing,
            location=location,
            specs=specs,
            characteristics=chars,
            photos=photos,
            canonical_url=canonical_url,
        )

    def _extract_json_ld(self, soup: BeautifulSoup) -> dict[str, any]:
        """Aggregate JSON-LD scripts by schema @type."""
        data: dict[str, any] = {}
        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string or ""
            if not content.strip():
                continue
            self._safe_load_json_ld(content, data)
        return data

    def _safe_load_json_ld(self, content: str, target: dict[str, any]) -> None:
        """Safely parse a single JSON-LD block."""
        try:
            parsed = json.loads(content)
            target[parsed.get("@type", "")] = parsed
        except json.JSONDecodeError:
            return

    def _parse_overview(self, soup: BeautifulSoup, property_id: str) -> PropertyOverview:
        """Extract title, reference code, and description."""
        h1 = soup.find("h1")
        title = ""
        if h1:
            title = h1.get_text(strip=True)
        ref_code = self._extract_reference_code(soup)
        desc = self._extract_description(soup)
        return PropertyOverview(
            property_id=property_id,
            title=title,
            reference_code=ref_code,
            description=desc,
        )

    def _extract_reference_code(self, soup: BeautifulSoup) -> str:
        """Extract property reference code from info text."""
        node = soup.select_one(".info__col")
        text = ""
        if node:
            text = node.get_text(strip=True)
        match = re.search(r"Ref:\s*([A-Za-z0-9_-]+)", text)
        if not match:
            return ""
        return match.group(1)

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract property description paragraph."""
        p_node = soup.select_one("#desc_descricao p, .descricao p")
        if not p_node:
            return ""
        return p_node.get_text("\n", strip=True)

    def _parse_pricing(self, soup: BeautifulSoup, ld: dict[str, any]) -> PropertyPricing:
        """Extract numeric price and formatted string."""
        action = ld.get("RentAction") or ld.get("BuyAction") or {}
        prod = ld.get("Product") or {}
        raw_price = action.get("price") or prod.get("offers", {}).get("price")
        amount = None
        if raw_price:
            amount = float(raw_price)
        node = soup.select_one(".info__valor, .imovelcard__valor__valor")
        formatted = ""
        if node:
            formatted = node.get_text(" ", strip=True)
        return PropertyPricing(amount=amount, formatted_text=formatted)

    def _parse_location(self, soup: BeautifulSoup, ld: dict[str, any]) -> PropertyLocation:
        """Extract address, neighborhood, city, and state."""
        action = ld.get("RentAction") or ld.get("BuyAction") or {}
        obj_addr = action.get("object", {}).get("address", {})
        city = obj_addr.get("addressLocality") or "Timóteo"
        state = obj_addr.get("addressRegion") or "MG"
        node = soup.select_one(".info__col")
        text = ""
        if node:
            text = node.get_text(strip=True)
        m_bairro = re.search(r"bairro\s+([^,]+)", text)
        bairro = ""
        if m_bairro:
            bairro = m_bairro.group(1).strip()
        return PropertyLocation(address="", neighborhood=bairro, city=city, state=state)

    def _parse_specs(self, soup: BeautifulSoup) -> PropertySpecs:
        """Parse room specifications from info tags."""
        tags = [t.get_text(" ", strip=True) for t in soup.select(".info__tag")]
        specs: dict[str, int] = {}
        for tag in tags:
            self._match_spec_tag(tag, specs)
        return PropertySpecs(
            bedrooms=specs.get("dorm"),
            suites=specs.get("suite"),
            bathrooms=specs.get("banh"),
            parking_spaces=specs.get("vaga"),
        )

    def _match_spec_tag(self, tag_text: str, specs: dict[str, int]) -> None:
        """Match and record a single room tag."""
        match = re.search(r"(\d+)\s*(Dormit[óo]rio|Su[íi]te|Banheiro|Vaga)", tag_text, re.IGNORECASE)
        if not match:
            return
        num = int(match.group(1))
        kind = match.group(2).lower()
        if "dorm" in kind:
            specs["dorm"] = num
        if "su" in kind:
            specs["suite"] = num
        if "banh" in kind:
            specs["banh"] = num
        if "vaga" in kind:
            specs["vaga"] = num

    def _parse_characteristics(self, soup: BeautifulSoup) -> tuple[str, ...]:
        """Extract grouped characteristics list."""
        boxes = soup.select(".imovel_cx_caracteristicas")
        items: list[str] = []
        for box in boxes:
            text = box.get_text(" ", strip=True)
            if text:
                items.append(text)
        return tuple(items)

    def _extract_embedded_photos(self, soup: BeautifulSoup) -> PhotoGallery:
        """Extract photo URLs present in the detail markup."""
        urls: list[str] = []
        for img in soup.find_all("img"):
            src = img.get("src") or ""
            if "/imagens/imoveis/" in src and "li5.php" not in src:
                urls.append(src)
        return PhotoGallery(photo_urls=tuple(dict.fromkeys(urls)))
