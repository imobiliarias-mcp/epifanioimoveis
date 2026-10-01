import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.value_objects import ListingPrice, PropertyCode, GeoCoordinate
from scripts.domain.criteria import PriceRange, RentalFilter
from scripts.domain.exceptions import InvalidPriceException, InvalidFilterException
from scripts.client.query_builder import RentalQueryBuilder
from scripts.providers.epifanio import EpifanioRentalProvider
from scripts.mcp.tools import EpifanioMcpAdapter


def test_listing_price_validation() -> None:
    """Verify ListingPrice rejects negative amounts and formats BRL."""
    price = ListingPrice(1500.50)
    assert price.format_brl() == "R$ 1.500,50"
    assert not price.is_zero()
    try:
        ListingPrice(-10.0)
        assert False, "Should have raised InvalidPriceException"
    except InvalidPriceException:
        pass


def test_price_range_validation() -> None:
    """Verify PriceRange raises error when minimum exceeds maximum."""
    min_price = ListingPrice(3000.0)
    max_price = ListingPrice(1000.0)
    try:
        PriceRange(minimum_price=min_price, maximum_price=max_price)
        assert False, "Should have raised InvalidFilterException"
    except InvalidFilterException:
        pass


def test_query_builder() -> None:
    """Verify RentalQueryBuilder converts domain filter to query dictionary."""
    filter_obj = RentalFilter().with_city("Timóteo").with_bedrooms(2)
    builder = RentalQueryBuilder()
    query_params = builder.build_parameters(filter_obj)
    assert query_params.get("dormitorios") == "22"
    url = builder.build_search_url(filter_obj)
    assert "/imovel/locacao/todos/timoteo" in url
    assert "dormitorios=22" in url


def test_provider_live_search() -> None:
    """Test live search execution against Epifânio Imóveis portal."""
    provider = EpifanioRentalProvider.create_default()
    criteria = RentalFilter().with_city("Timóteo")
    result = provider.search_rentals(criteria)
    assert result.total_count() > 0
    assert result.returned_count() > 0
    first_listing = list(result.listings())[0]
    assert len(first_listing.code()) > 0


def test_provider_live_detail() -> None:
    """Test live detail retrieval for a known property."""
    provider = EpifanioRentalProvider.create_default()
    code = PropertyCode("4198561")
    detail = provider.get_property_detail(code)
    assert detail.listing.code() == "4198561"
    assert "Timirim" in detail.listing.details.location_summary


def test_provider_live_facets() -> None:
    """Test live facets retrieval."""
    provider = EpifanioRentalProvider.create_default()
    facets = provider.get_facets()
    cities = facets.city_names()
    assert len(cities) > 0


def test_mcp_adapter() -> None:
    """Test MCP tool adapter returns serializable dictionaries."""
    adapter = EpifanioMcpAdapter.create_default()
    info = adapter.get_provider_info()
    assert info.get("provider_name") == "epifanio"
    search_payload = adapter.search_rentals(city="Timóteo", page=1)
    assert "listings" in search_payload
    assert "total_count" in search_payload


def _run_unit() -> None:
    """Run pure unit tests."""
    test_listing_price_validation()
    test_price_range_validation()
    test_query_builder()
    print("✔ Testes unitários de domínio e builder: OK")


def _run_integration() -> None:
    """Run live API integration tests."""
    test_provider_live_search()
    test_provider_live_detail()
    test_provider_live_facets()
    print("✔ Testes de integração de API: OK")


def main() -> None:
    """Execute all test suites."""
    print("Executando bateria de testes...")
    _run_unit()
    _run_integration()
    test_mcp_adapter()
    print("✔ Testes do adaptador MCP: OK")
    print("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!\n")


if __name__ == "__main__":
    main()
