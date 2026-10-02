"""HTML parser for search results page."""

import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup, Tag

from epifanio_research.domain.listing import (
    InvalidPublicPropertyUrlError,
    ListingCollection,
    ListingIdentity,
    ListingLocation,
    ListingSummary,
)
from epifanio_research.parsers.feature_extractor import CardFeatureExtractor


class SearchPageParser:
    """Transforms raw search result HTML into domain ListingCollection."""

    def __init__(
        self,
        feature_extractor: CardFeatureExtractor | None = None,
        public_base_url: str = "https://www.epifanioimoveis.com",
    ) -> None:
        """Initialize parser with extraction and public-page configuration."""
        self._features = feature_extractor or CardFeatureExtractor()
        self._public_base_url = public_base_url.rstrip("/")
        self._validate_public_base()

    def parse(self, html: str, page_number: int = 1) -> ListingCollection:
        """Parse raw HTML and construct the first-class listing collection."""
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".imovelcard")
        items = tuple(self._parse_card(card) for card in cards if self._is_listing_card(card))
        has_next = self._detect_next_page(soup)
        return ListingCollection(items=items, current_page=page_number, has_next_page=has_next)

    def _parse_card(self, card: Tag) -> ListingSummary:
        """Transform a single .imovelcard tag into a ListingSummary."""
        link = self._extract_card_link(card)
        prop_id = self._extract_property_id(link)
        public_url = self._resolve_public_url(link, prop_id)
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
            url=public_url,
        )

    def _extract_card_link(self, card: Tag) -> str:
        """Return the card's canonical path or its actual public anchor."""
        link = str(card.get("data-link", "")).strip()
        if link:
            return link
        anchor = card.select_one(".imovelcard__img")
        if anchor and anchor.get("href"):
            return str(anchor.get("href"))
        raise InvalidPublicPropertyUrlError("Listing card has no recoverable public URL.")

    def _extract_property_id(self, link: str) -> str:
        """Extract numeric property ID from URL path."""
        try:
            path = urlsplit(link).path
        except ValueError as error:
            raise InvalidPublicPropertyUrlError(
                f"Listing card has malformed public URL '{link}'."
            ) from error
        parts = [p for p in path.strip("/").split("/") if p]
        if len(parts) >= 2 and parts[0] == "imovel":
            return parts[1]
        return ""

    def _is_listing_card(self, card: Tag) -> bool:
        """Ignore pagination wrappers while including malformed listing cards."""
        return bool(card.get("data-link") or card.select_one(".imovelcard__info"))

    def _validate_public_base(self) -> None:
        """Reject a malformed public-page base before parsing responses."""
        base = urlsplit(self._public_base_url)
        if base.scheme not in {"http", "https"} or not base.hostname:
            raise InvalidPublicPropertyUrlError(
                f"Invalid public property URL base '{self._public_base_url}'."
            )

    def _resolve_public_url(self, link: str, property_id: str) -> str:
        """Resolve and validate one absolute public property URL."""
        target = urljoin(f"{self._public_base_url}/", link)
        parsed_target = urlsplit(target)
        self._validate_public_target(parsed_target, property_id, link)
        return target

    def _validate_public_target(self, target, property_id: str, link: str) -> None:
        """Reject non-web, cross-site, and non-property destinations."""
        host_matches = self._same_host(target.hostname)
        segments = [part for part in target.path.split("/") if part]
        is_property = len(segments) > 1 and segments[0] == "imovel" and segments[1].isdigit()
        if target.scheme not in {"http", "https"} or not target.hostname or not host_matches or not is_property:
            raise InvalidPublicPropertyUrlError(
                f"Property '{property_id}' has invalid public URL '{link}'."
            )

    def _same_host(self, hostname: str | None) -> bool:
        """Compare destination and configured portal hostnames."""
        base_hostname = urlsplit(self._public_base_url).hostname or ""
        target_hostname = hostname or ""
        return base_hostname.lower().removeprefix("www.") == target_hostname.lower().removeprefix("www.")

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
