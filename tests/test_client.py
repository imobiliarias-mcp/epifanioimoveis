"""Unit tests for EpifanioRentalClient with stubbed HTTP responses."""

import pytest
from epifanio_research.client import EpifanioRentalClient
from epifanio_research.collaborators import RentalNetworkGateway, RentalParserSuite
from epifanio_research.domain.criteria import SearchCriteria
from epifanio_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    PropertyNotFoundError,
)
from epifanio_research.infrastructure.url_builder import UrlBuilder
from tests.test_parsers import DETAIL_HTML_FIXTURE, SEARCH_HTML_FIXTURE


class StubHttpClient:
    """Stub HTTP client returning predefined responses."""

    def __init__(self, responses: dict[str, HttpResponse]) -> None:
        """Initialize with URL mapping."""
        self._responses = responses

    def get(self, url: str) -> HttpResponse:
        """Return stubbed response or 404 response."""
        for pattern, resp in self._responses.items():
            if pattern in url:
                return resp
        return HttpResponse(status_code=404, text="", final_url=url)


def test_client_search_with_stub():
    """Verify client search flows through gateway and parser."""
    stub = StubHttpClient({
        "/imovel/locacao": HttpResponse(200, SEARCH_HTML_FIXTURE, "https://www.epifanioimoveis.com/imovel/locacao"),
    })
    gateway = RentalNetworkGateway(http_client=stub, url_builder=UrlBuilder())
    client = EpifanioRentalClient(gateway=gateway, parsers=RentalParserSuite())

    results = client.search_rentals(city="timoteo")
    assert len(results) == 1
    assert results[0].identity.property_id == "4198561"


def test_client_details_with_stub():
    """Verify client retrieves property details correctly."""
    stub = StubHttpClient({
        "/imovel/4198561": HttpResponse(200, DETAIL_HTML_FIXTURE, "https://www.epifanioimoveis.com/imovel/4198561"),
    })
    gateway = RentalNetworkGateway(http_client=stub, url_builder=UrlBuilder())
    client = EpifanioRentalClient(gateway=gateway, parsers=RentalParserSuite())

    detail = client.get_details("4198561")
    assert detail.overview.property_id == "4198561"
    assert detail.pricing.amount == 2930.0


def test_client_property_not_found_raises_exception():
    """Verify client raises PropertyNotFoundError when response redirects home."""
    stub = StubHttpClient({
        "/imovel/999999": HttpResponse(200, "<html>Landing</html>", "https://www.epifanioimoveis.com/"),
    })
    gateway = RentalNetworkGateway(http_client=stub, url_builder=UrlBuilder())
    client = EpifanioRentalClient(gateway=gateway, parsers=RentalParserSuite())

    with pytest.raises(PropertyNotFoundError):
        client.get_details("999999")
