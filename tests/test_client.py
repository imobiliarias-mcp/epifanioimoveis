"""Unit tests for EpifanioRentalClient with stubbed HTTP responses."""

import httpx
import pytest

from epifanio_research.client import EpifanioRentalClient
from epifanio_research.collaborators import RentalNetworkGateway, RentalParserSuite
from epifanio_research.infrastructure import http_client as http_client_module
from epifanio_research.infrastructure.http_client import (
    HttpResponse,
    HttpxHttpClient,
    PortalConnectionError,
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


def _stub_httpx_response(monkeypatch, status_code: int) -> None:
    original_client = httpx.Client
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            status_code, text="upstream failure", request=request
        )
    )

    def create_client(**options):
        return original_client(transport=transport, **options)

    monkeypatch.setattr(http_client_module.httpx, "Client", create_client)


@pytest.mark.parametrize("status_code", [400, 404, 503])
def test_http_client_raises_connection_error_for_failed_response(
    monkeypatch, status_code: int
) -> None:
    _stub_httpx_response(monkeypatch, status_code)

    with pytest.raises(PortalConnectionError, match=str(status_code)):
        HttpxHttpClient().get("https://www.epifanioimoveis.com/search")


def test_client_public_base_override_reaches_core_search_parser():
    """Keep search transport and public listing URL bases independent."""
    class RecordingHttpClient:
        def __init__(self):
            self.requested_urls = []

        def get(self, url):
            self.requested_urls.append(url)
            return HttpResponse(200, SEARCH_HTML_FIXTURE, url)

    http_client = RecordingHttpClient()
    gateway = RentalNetworkGateway(
        http_client=http_client,
        url_builder=UrlBuilder(base_url="https://search.example"),
    )
    client = EpifanioRentalClient(gateway=gateway, public_base_url="https://public.example")
    results = client.search_rentals(city="timoteo")

    assert len(http_client.requested_urls) == 1
    assert http_client.requested_urls[0].startswith("https://search.example/")
    assert results[0].url == (
        "https://public.example/imovel/4198561/"
        "apartamento-locacao-timoteo-mg-timirim"
    )


def test_script_provider_public_base_override_reaches_parser():
    """Use configured public links independently from the search host."""
    from scripts.client.configuration import EpifanioConfiguration
    from scripts.client.query_builder import RentalQueryBuilder
    from scripts.domain.criteria import RentalFilter
    from scripts.providers.epifanio import EpifanioRentalProvider

    class RecordingTransport:
        def __init__(self):
            self.requested_urls = []

        def get_text(self, url):
            self.requested_urls.append(url)
            return SEARCH_HTML_FIXTURE

    transport = RecordingTransport()
    configuration = EpifanioConfiguration(
        base_hostname="public.example",
        base_url="https://search.example",
    )
    provider = EpifanioRentalProvider(
        transport=transport,
        query_builder=RentalQueryBuilder(configuration),
    )
    result = provider.search_rentals(RentalFilter())
    listing = result.to_dictionary()["listings"][0]

    assert len(transport.requested_urls) == 1
    assert transport.requested_urls[0].startswith("https://search.example/")
    assert listing["url"] == (
        "https://public.example/imovel/4198561/"
        "apartamento-locacao-timoteo-mg-timirim"
    )
