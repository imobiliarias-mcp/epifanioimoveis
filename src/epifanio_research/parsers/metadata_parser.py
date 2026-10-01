"""Parser for location metadata arrays embedded in the portal pages."""

import ast
import re
from bs4 import BeautifulSoup
from epifanio_research.domain.metadata import (
    City,
    LocationCatalog,
    Neighborhood,
    NeighborhoodGroup,
)


class MetadataParser:
    """Parses dgCidadesBairros JavaScript structures from page HTML."""

    REGEX_PATTERN = r"cidades\s*:\s*(\[.*?\])\s*,\s*bairros\s*:\s*(\[.*?\])\s*,\s*bairros_value\s*:\s*(\[.*?\])\s*\}"

    def parse(self, html: str) -> LocationCatalog:
        """Parse raw HTML and construct the LocationCatalog."""
        soup = BeautifulSoup(html, "html.parser")
        match = self._find_script_match(soup)
        if not match:
            return LocationCatalog()
        return self._build_catalog_from_match(match)

    def _find_script_match(self, soup: BeautifulSoup) -> re.Match | None:
        """Find the script tag containing the dgCidadesBairros data."""
        for script in soup.find_all("script"):
            content = script.string or ""
            if "dgCidadesBairros" not in content:
                continue
            match = re.search(self.REGEX_PATTERN, content, re.DOTALL)
            if match:
                return match
        return None

    def _build_catalog_from_match(self, match: re.Match) -> LocationCatalog:
        """Evaluate raw arrays and assemble domain City models."""
        cidades_list = ast.literal_eval(match.group(1).replace("\n", " "))
        bairros_list = ast.literal_eval(match.group(2).replace("\n", " "))
        values_list = ast.literal_eval(match.group(3).replace("\n", " "))
        cities: list[City] = []
        for (slug, name), b_names, b_vals in zip(cidades_list, bairros_list, values_list):
            if not slug:
                continue
            group = self._build_neighborhood_group(b_names, b_vals)
            cities.append(City(name=name, slug=slug, neighborhoods=group))
        return LocationCatalog(cities=tuple(cities))

    def _build_neighborhood_group(
        self, names: list[str], values: list[str]
    ) -> NeighborhoodGroup:
        """Assemble NeighborhoodGroup from names and slug-id pairs."""
        items: list[Neighborhood] = []
        for name, full_slug in zip(names, values):
            if not name or not full_slug or full_slug == "-":
                continue
            num_id = full_slug.split("-")[-1]
            items.append(Neighborhood(name=name, slug=full_slug, numeric_id=num_id))
        return NeighborhoodGroup(items=tuple(items))
