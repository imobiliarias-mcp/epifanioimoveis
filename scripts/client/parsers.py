"""HTML and JSON parsers converting remote portal payloads into domain entities."""

import ast
import json
import re

from bs4 import BeautifulSoup

from scripts.client.search_parser import (
    DEFAULT_PUBLIC_BASE_URL,
    SearchResultParser,  # noqa: F401 - public compatibility re-export
    resolve_public_property_link,
)
from scripts.domain.collections import FacetCollection
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingMedia,
    ListingPublicLink,
    ListingValuation,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.exceptions import InvalidPublicPropertyUrlException
from scripts.domain.value_objects import ListingPrice, PropertyCode


class PropertyDetailParser:
    """Parses property detail HTML and microdata into RentalPropertyDetail."""

    def __init__(self, public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> None:
        """Configure a public-page base for the documented detail route."""
        self._public_base_url = public_base_url

    def parse_detail_response(self, html_text: str) -> RentalPropertyDetail:
        """Parse property detail markup and return domain entity."""
        soup = BeautifulSoup(html_text, "html.parser")
        ld_data = self._extract_json_ld(soup)
        code_str = self._extract_code(soup, ld_data)
        public_link = self._detail_public_link(code_str)
        title = self._extract_title(soup)
        price_val = self._extract_price(soup, ld_data)
        prop_type = self._extract_property_type(title)
        location = self._extract_location(soup)
        media_url = self._extract_lead_image(soup, ld_data)
        amenities = self._extract_amenities(soup)
        description = self._extract_description(soup)

        identity = ListingIdentity(code=PropertyCode(code_str), title=title)
        valuation = ListingValuation(rental_price=ListingPrice(price_val), property_type=prop_type)
        core = ListingCore(identity=identity, valuation=valuation)
        media = ListingMedia(media_url=media_url, public_link=public_link)
        details = ListingDetails(location_summary=location, media=media)
        listing = RentalListing(core=core, details=details)
        profile = DetailedProfile(description=description, amenities_summary=amenities)
        return RentalPropertyDetail(listing=listing, profile=profile)

    def _detail_public_link(self, property_code: str) -> ListingPublicLink:
        """Build the already-supported direct detail route from its code."""
        if not property_code.isdigit():
            raise InvalidPublicPropertyUrlException(
                f"Property '{property_code}' has no recoverable public URL."
            )
        url_path = f"/imovel/{property_code}"
        return resolve_public_property_link(url_path, self._public_base_url, property_code)

    def _extract_json_ld(self, soup: BeautifulSoup) -> dict[str, any]:
        """Aggregate JSON-LD scripts by @type."""
        data: dict[str, any] = {}
        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string or ""
            if not content.strip():
                continue
            try:
                parsed = json.loads(content)
                data[parsed.get("@type", "")] = parsed
            except json.JSONDecodeError:
                continue
        return data

    def _extract_code(self, soup: BeautifulSoup, ld: dict[str, any]) -> str:
        """Extract property reference code or numeric SKU."""
        prod = ld.get("Product") or {}
        sku = prod.get("sku") or prod.get("mpn")
        if sku:
            return str(sku)
        node = soup.select_one(".info__col")
        text = node.get_text(strip=True) if node else ""
        match = re.search(r"Ref:\s*([A-Za-z0-9_-]+)", text)
        if match:
            return match.group(1)
        return "0"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract headline title from h1."""
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return "Imóvel para Locação"

    def _extract_price(self, soup: BeautifulSoup, ld: dict[str, any]) -> float:
        """Extract numeric price from JSON-LD or DOM."""
        action = ld.get("RentAction") or ld.get("BuyAction") or {}
        prod = ld.get("Product") or {}
        raw = action.get("price") or prod.get("offers", {}).get("price")
        if raw:
            return float(raw)
        node = soup.select_one(".info__valor, .imovelcard__valor__valor")
        text = node.get_text(" ", strip=True) if node else ""
        clean = re.sub(r"[^\d]", "", text)
        if clean:
            return float(clean)
        return 0.0

    def _extract_property_type(self, title: str) -> str:
        """Extract property type word from title."""
        first_word = title.split(" ")[0] if title else "Imóvel"
        return first_word.strip()

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract location summary string."""
        node = soup.select_one(".info__col")
        if not node:
            return "Timóteo / MG"
        text = node.get_text(strip=True)
        m_bairro = re.search(r"bairro\s+([^,]+)", text)
        bairro = m_bairro.group(1).strip() if m_bairro else ""
        if bairro:
            return f"{bairro}, Timóteo / MG"
        return "Timóteo / MG"

    def _extract_lead_image(self, soup: BeautifulSoup, ld: dict[str, any]) -> str:
        """Extract primary photo URL."""
        action = ld.get("RentAction") or ld.get("BuyAction") or {}
        img_url = action.get("object", {}).get("image")
        if img_url:
            return str(img_url)
        img = soup.select_one(".galeria-v2 img, .imovelcard__img img")
        if img and img.get("src"):
            return img["src"]
        return ""

    def _extract_amenities(self, soup: BeautifulSoup) -> str:
        """Extract and format tags and characteristics."""
        tags = [t.get_text(" ", strip=True) for t in soup.select(".info__tag")]
        boxes = [b.get_text(" ", strip=True) for b in soup.select(".imovel_cx_caracteristicas")]
        combined = tags + boxes
        return " | ".join(combined)

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description text."""
        p_node = soup.select_one("#desc_descricao p, .descricao p")
        if p_node:
            return p_node.get_text("\n", strip=True)
        return ""


class FacetParser:
    """Parses dgCidadesBairros JavaScript structures into FacetCollection."""

    PATTERN = r"cidades\s*:\s*(\[.*?\])\s*,\s*bairros\s*:\s*(\[.*?\])\s*,\s*bairros_value\s*:\s*(\[.*?\])\s*\}"

    def parse_facets_response(self, html_text: str) -> FacetCollection:
        """Extract city names and neighborhood names from search HTML."""
        match = re.search(self.PATTERN, html_text, re.DOTALL)
        if not match:
            return FacetCollection(facet_map={"cities": (), "neighborhoods": ()})
        cidades_list = ast.literal_eval(match.group(1).replace("\n", " "))
        bairros_list = ast.literal_eval(match.group(2).replace("\n", " "))
        cities = [name for slug, name in cidades_list if slug and name]
        neighborhoods = self._collect_neighborhood_names(bairros_list)
        return FacetCollection(
            facet_map={"cities": tuple(cities), "neighborhoods": tuple(neighborhoods)}
        )

    def _collect_neighborhood_names(self, bairros_list: list[list[str]]) -> list[str]:
        """Aggregate unique neighborhood names."""
        names: list[str] = []
        for group in bairros_list:
            for item in group:
                if item and item != "-" and item not in names:
                    names.append(item)
        return names
