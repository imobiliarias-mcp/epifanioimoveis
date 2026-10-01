"""Unit tests for UrlBuilder route and query generation."""

from epifanio_research.domain.criteria import (
    FeatureBundle,
    FilterBundle,
    LocationCriteria,
    RoomCriteria,
    SearchCriteria,
    SearchScope,
)
from epifanio_research.domain.enums import PropertyType, SortOrder, TransactionType
from epifanio_research.domain.values import PageNumber, PriceRange, RoomCount
from epifanio_research.infrastructure.url_builder import UrlBuilder


def test_url_builder_target_url():
    """Verify target prompt URL structure matches exact query requirement."""
    builder = UrlBuilder()
    criteria = SearchCriteria(
        scope=SearchScope(transaction=TransactionType.VENDA, property_type=PropertyType.TODOS),
        location=LocationCriteria(city_slug="timoteo"),
        filters=FilterBundle(price_range=PriceRange(maximum=1600000)),
        features=FeatureBundle(room_criteria=RoomCriteria(bedrooms=RoomCount(2, is_minimum=False))),
    )
    url = builder.build_search_url(criteria)
    assert url.startswith("https://www.epifanioimoveis.com/imovel/venda/todos/timoteo/?&")
    assert "vma=1600000" in url
    assert "dormitorios=2" in url


def test_url_builder_rental_defaults():
    """Verify rental default path without query parameters."""
    builder = UrlBuilder()
    criteria = SearchCriteria(
        scope=SearchScope(transaction=TransactionType.LOCACAO, property_type=PropertyType.TODOS),
        location=LocationCriteria(city_slug="timoteo"),
    )
    url = builder.build_search_url(criteria)
    assert url == "https://www.epifanioimoveis.com/imovel/locacao/todos/timoteo"


def test_url_builder_with_multi_bairros_and_sort():
    """Verify comma-separated neighborhood IDs and sort order."""
    builder = UrlBuilder()
    criteria = SearchCriteria(
        scope=SearchScope(transaction=TransactionType.LOCACAO, property_type=PropertyType.APARTAMENTO),
        location=LocationCriteria(city_slug="timoteo", neighborhood_ids=("479695", "479319")),
        sort_order=SortOrder.MENOR_VALOR,
        page=PageNumber(2),
    )
    url = builder.build_search_url(criteria)
    assert "bairros=479695%2C479319" in url
    assert "ord=menor_valor" in url
    assert "pag=2" in url


def test_url_builder_detail_and_photos():
    """Verify direct property detail and AJAX photos URLs."""
    builder = UrlBuilder()
    detail_url = builder.build_detail_url("4198561")
    photos_url = builder.build_photos_url("4198561")
    assert detail_url == "https://www.epifanioimoveis.com/imovel/4198561"
    assert photos_url == "https://www.epifanioimoveis.com/t27/lista_imoveis_fotos.php?imovel=4198561"
