"""HTML parser for search results page."""

import re
from bs4 import BeautifulSoup, Tag
from epifanio_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingLocation,
    ListingSummary,
)
from epifanio_research.parsers.feature_extractor import CardFeatureExtractor


class SearchPageParser:
    """Transforms raw search result HTML into domain ListingCollection."""

    def __init__(self, feature_extractor: CardFeatureExtractor | None = None) -> None:
        """Initialize parser with feature extractor collaborator."""
        self._features = feature_extractor or CardFeatureExtractor()

    def parse(self, html: str, page_number: int = 1) -> ListingCollection:
        """Parse raw HTML and construct the first-class listing collection."""
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".imovelcard")
        items = tuple(self._parse_card(card) for card in cards if card.get("data-link"))
        has_next = self._detect_next_page(soup)
        return ListingCollection(items=items, current_page=page_number, has_next_page=has_next)

    def _parse_card(self, card: Tag) -> ListingSummary:
        """Transform a single .imovelcard tag into a ListingSummary."""
        link = card.get("data-link", "")
        prop_id = self._extract_property_id(link)
        img_node = card.select_one(".imovelcard__img")
        title = ""
        if img_node:
            title = img_node.get("title", "")
        thumb = self._extract_thumbnail(card)
        location = self._parse_location(card)
        price_text = self._parse_price(card)
        specs = self._features.extract(card)
        ref_code = self._parse_reference(card)
        return ListingSummary(
            identity=ListingIdentity(property_id=prop_id, url_path=link),
            title=title,
            location=location,
            price_text=price_text,
            specs=specs,
            reference_code=ref_code,
            thumbnail_url=thumb,
        )

    def _extract_property_id(self, link: str) -> str:
        """Extract numeric property ID from URL path."""
        parts = [p for p in link.strip("/").split("/") if p]
        if len(parts) >= 2:
            return parts[1]
        return ""

    def _extract_thumbnail(self, card: Tag) -> str | None:
        """Extract thumbnail image source."""
        img = card.select_one(".imovelcard__img img")
        if not img:
            return None
        return img.get("src")

    def _parse_location(self, card: Tag) -> ListingLocation:
        """Parse neighborhood, city, and state from card local node."""
        node = card.select_one(".imovelcard__info__local")
        if not node:
            return ListingLocation(neighborhood="", city="")
        text = node.get_text(strip=True)
        return self._split_location_text(text)

    def _split_location_text(self, text: str) -> ListingLocation:
        """Split 'Bairro, Cidade / UF' formatted string."""
        parts = [p.strip() for p in text.split(",")]
        neighborhood = ""
        if parts:
            neighborhood = parts[0]
        if len(parts) < 2:
            return ListingLocation(neighborhood=neighborhood, city="")
        subparts = [p.strip() for p in parts[1].split("/")]
        city = ""
        if subparts:
            city = subparts[0]
        state = "MG"
        if len(subparts) > 1:
            state = subparts[1]
        return ListingLocation(neighborhood=neighborhood, city=city, state=state)

    def _parse_price(self, card: Tag) -> str:
        """Extract text price from card value node."""
        node = card.select_one(".imovelcard__valor__valor")
        if not node:
            return "Consulte"
        return node.get_text(" ", strip=True)

    def _parse_reference(self, card: Tag) -> str | None:
        """Extract reference code if present."""
        node = card.select_one(".imovelcard__info__ref")
        if not node:
            return None
        match = re.search(r"Ref:\s*(\S+)", node.get_text(strip=True))
        if not match:
            return None
        return match.group(1).rstrip("-")

    def _detect_next_page(self, soup: BeautifulSoup) -> bool:
        """Detect whether pagination has a next page arrow link."""
        pagination = soup.select_one(".lista_imoveis_paginacao")
        if not pagination:
            return False
        next_btn = pagination.find("a", title="Próxima Página")
        return next_btn is not None
