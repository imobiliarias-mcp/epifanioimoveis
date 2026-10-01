"""HTML and JSON parsers converting remote portal payloads into domain entities."""

import ast
import json
import re
from bs4 import BeautifulSoup, Tag
from scripts.domain.collections import (
    FacetCollection,
    RentalListingCollection,
    RentalSearchResult,
)
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingValuation,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.value_objects import ListingPrice, PropertyCode


class SearchResultParser:
    """Parses search results HTML into RentalSearchResult."""

    def parse_search_response(self, html_text: str) -> RentalSearchResult:
        """Extract rental listings and total count from search markup."""
        soup = BeautifulSoup(html_text, "html.parser")
        cards = soup.select(".imovelcard")
        parsed_items: list[RentalListing] = []
        for card in cards:
            if not card.get("data-link"):
                continue
            listing = self._parse_single_card(card)
            parsed_items.append(listing)
        collection = RentalListingCollection(listings=tuple(parsed_items))
        total_count = self._extract_total_count(soup, len(parsed_items))
        return RentalSearchResult(collection=collection, total_listings_count=total_count)

    def _parse_single_card(self, card: Tag) -> RentalListing:
        """Convert a single .imovelcard tag into RentalListing entity."""
        link = card.get("data-link", "")
        code_str = self._extract_code_from_link(link)
        title = self._extract_card_title(card)
        prop_type = self._extract_property_type(card)
        price_val = self._extract_card_price(card)
        location = self._extract_card_location(card)
        media_url = self._extract_card_thumbnail(card)

        identity = ListingIdentity(code=PropertyCode(code_str), title=title)
        valuation = ListingValuation(rental_price=ListingPrice(price_val), property_type=prop_type)
        core = ListingCore(identity=identity, valuation=valuation)
        details = ListingDetails(location_summary=location, media_url=media_url)
        return RentalListing(core=core, details=details)

    def _extract_code_from_link(self, link: str) -> str:
        """Extract numeric identifier from URL path."""
        parts = [p for p in link.strip("/").split("/") if p]
        if len(parts) >= 2:
            return parts[1]
        return "0"

    def _extract_card_title(self, card: Tag) -> str:
        """Extract headline title from card."""
        img_node = card.select_one(".imovelcard__img")
        if img_node and img_node.get("title"):
            return img_node["title"].strip()
        loc_node = card.select_one(".imovelcard__info__local")
        if loc_node:
            return loc_node.get_text(strip=True)
        return "Imóvel para Locação"

    def _extract_property_type(self, card: Tag) -> str:
        """Extract property type text from card reference."""
        ref_node = card.select_one(".imovelcard__info__ref")
        text = ref_node.get_text(strip=True) if ref_node else ""
        if "-" in text:
            return text.split("-")[-1].strip()
        return "Imóvel"

    def _extract_card_price(self, card: Tag) -> float:
        """Parse numeric price from card value node."""
        node = card.select_one(".imovelcard__valor__valor")
        text = node.get_text(" ", strip=True) if node else ""
        clean = re.sub(r"[^\d]", "", text)
        if not clean:
            return 0.0
        return float(clean)

    def _extract_card_location(self, card: Tag) -> str:
        """Parse neighborhood and municipality from card."""
        node = card.select_one(".imovelcard__info__local")
        if not node:
            return ""
        return node.get_text(strip=True)

    def _extract_card_thumbnail(self, card: Tag) -> str:
        """Extract thumbnail image URL from card."""
        img = card.select_one(".imovelcard__img img")
        if not img or not img.get("src"):
            return ""
        return img["src"]

    def _extract_total_count(self, soup: BeautifulSoup, page_count: int) -> int:
        """Infer total matching listing count."""
        text = soup.get_text(" ", strip=True)
        match = re.search(r"(\d+)\s+im[óo]veis\s+encontrados", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return page_count


class PropertyDetailParser:
    """Parses property detail HTML and microdata into RentalPropertyDetail."""

    def parse_detail_response(self, html_text: str) -> RentalPropertyDetail:
        """Parse property detail markup and return domain entity."""
        soup = BeautifulSoup(html_text, "html.parser")
        ld_data = self._extract_json_ld(soup)
        code_str = self._extract_code(soup, ld_data)
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
        details = ListingDetails(location_summary=location, media_url=media_url)
        listing = RentalListing(core=core, details=details)
        profile = DetailedProfile(description=description, amenities_summary=amenities)
        return RentalPropertyDetail(listing=listing, profile=profile)

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
