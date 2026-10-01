"""Extractor for property specifications from HTML feature elements."""

import re
from bs4 import Tag
from epifanio_research.domain.listing import ListingSpecs


class CardFeatureExtractor:
    """Parses room counts and dimensions from card feature nodes."""

    def extract(self, card: Tag) -> ListingSpecs:
        """Parse all specs from features within an imovelcard."""
        features = card.select(".imovelcard__info__feature")
        values = self._collect_feature_values(features)
        return ListingSpecs(
            bedrooms=values.get("bed"),
            suites=values.get("bath"),
            bathrooms=values.get("shower"),
            parking_spaces=values.get("car"),
            area_text=values.get("arrows"),
        )

    def _collect_feature_values(self, features: list[Tag]) -> dict[str, any]:
        """Aggregate spec values keyed by icon identifier."""
        results: dict[str, any] = {}
        for feature in features:
            key, val = self._parse_single_feature(feature)
            if key is not None:
                results[key] = val
        return results

    def _parse_single_feature(self, feature: Tag) -> tuple[str | None, any]:
        """Map feature icon to room count or area dimension."""
        icon = feature.find("i")
        classes = []
        if icon:
            classes = icon.get("class", [])
        text = feature.get_text(" ", strip=True)
        if "fa-bed" in classes:
            return "bed", self._parse_first_int(text)
        if "fa-bath" in classes:
            return "bath", self._parse_first_int(text)
        if "fa-shower" in classes:
            return "shower", self._parse_first_int(text)
        if "fa-car" in classes:
            return "car", self._parse_first_int(text)
        if "fa-arrows-h" in classes:
            return "arrows", text
        return None, None

    def _parse_first_int(self, text: str) -> int | None:
        """Extract first numeric sequence as integer."""
        match = re.search(r"\d+", text)
        if not match:
            return None
        return int(match.group(0))
