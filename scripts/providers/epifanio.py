"""Epifânio Imóveis rental search provider implementation."""

import httpx
from scripts.client.configuration import EpifanioConfiguration
from scripts.client.http_transport import EpifanioHttpTransport
from scripts.client.parsers import (
    FacetParser,
    PropertyDetailParser,
    SearchResultParser,
)
from scripts.client.query_builder import RentalQueryBuilder
from scripts.domain.collections import FacetCollection, RentalSearchResult
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import RentalPropertyDetail
from scripts.domain.exceptions import PropertyNotFoundException
from scripts.domain.value_objects import PropertyCode
from scripts.interfaces.provider import RentalProviderProtocol


class EpifanioRentalProvider(RentalProviderProtocol):
    """Adapter implementing RentalProviderProtocol for Epifânio Imóveis portal."""

    def __init__(
        self,
        transport: EpifanioHttpTransport,
        query_builder: RentalQueryBuilder,
    ) -> None:
        """Initialize provider with transport and query builder."""
        self._transport = transport
        self._builder = query_builder

    @classmethod
    def create_default(cls) -> "EpifanioRentalProvider":
        """Factory method constructing provider with default configurations."""
        config = EpifanioConfiguration()
        client = httpx.Client(timeout=20.0, follow_redirects=True)
        transport = EpifanioHttpTransport(configuration=config, http_client=client)
        builder = RentalQueryBuilder(configuration=config)
        return cls(transport=transport, query_builder=builder)

    def provider_name(self) -> str:
        """Return unique provider identifier for central MCP registry."""
        return "epifanio"

    def search_rentals(self, search_filter: RentalFilter) -> RentalSearchResult:
        """Search rental listings using criteria."""
        search_url = self._builder.build_search_url(search_filter)
        html_content = self._transport.get_text(search_url)
        parser = SearchResultParser()
        return parser.parse_search_response(html_content)

    def get_property_detail(self, code: PropertyCode) -> RentalPropertyDetail:
        """Retrieve full details for a single property by code."""
        code_str = code.value()
        url = f"https://www.epifanioimoveis.com/imovel/{code_str}"
        resp = self._transport.get_response(url)
        final_url = str(resp.url).rstrip("/")
        if final_url.endswith("epifanioimoveis.com"):
            raise PropertyNotFoundException(f"Property '{code_str}' was not found.")
        parser = PropertyDetailParser()
        return parser.parse_detail_response(resp.text)

    def get_facets(self) -> FacetCollection:
        """Retrieve available cities, neighborhoods, and filter options."""
        url = "https://www.epifanioimoveis.com/imovel/locacao"
        html_content = self._transport.get_text(url)
        parser = FacetParser()
        return parser.parse_facets_response(html_content)
