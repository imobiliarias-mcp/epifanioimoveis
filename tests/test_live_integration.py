"""Live integration tests hitting epifanioimoveis.com endpoints."""

import pytest
from epifanio_research import (
    EpifanioRentalClient,
    FeatureBundle,
    FilterBundle,
    LocationCriteria,
    PriceRange,
    PropertyType,
    RoomCount,
    RoomCriteria,
    SearchCriteria,
    SearchScope,
    TransactionType,
)


@pytest.fixture
def client() -> EpifanioRentalClient:
    """Fixture providing configured live EpifanioRentalClient."""
    return EpifanioRentalClient()


def test_live_target_prompt_url_search(client: EpifanioRentalClient):
    """Verify live search with exact target URL parameters from prompt:

    Target: https://www.epifanioimoveis.com/imovel/venda/todos/timoteo/?&dormitorios=2&vma=1600000
    """
    criteria = SearchCriteria(
        scope=SearchScope(transaction=TransactionType.VENDA, property_type=PropertyType.TODOS),
        location=LocationCriteria(city_slug="timoteo"),
        filters=FilterBundle(price_range=PriceRange(maximum=1600000)),
        features=FeatureBundle(room_criteria=RoomCriteria(bedrooms=RoomCount(2, is_minimum=False))),
    )
    results = client.search(criteria)
    assert len(results) > 0
    first = results[0]
    assert first.identity.property_id != ""
    assert first.specs.bedrooms == 2
    assert "Timóteo" in first.location.city


def test_live_rental_search(client: EpifanioRentalClient):
    """Verify live rental search in Timóteo."""
    results = client.search_rentals(city="timoteo")
    assert len(results) > 0
    first = results[0]
    assert first.identity.property_id != ""
    assert first.price_text != ""


def test_live_rental_property_details(client: EpifanioRentalClient):
    """Verify live retrieval of apartment 4198561 in Timirim, Timóteo."""
    detail = client.get_details("4198561")
    assert detail.overview.property_id == "4198561"
    assert "Apartamento" in detail.overview.title
    assert detail.overview.reference_code == "0423"
    assert detail.location.neighborhood == "Timirim"
    assert detail.pricing.amount > 0
    assert detail.specs.bedrooms == 3


def test_live_photo_gallery_endpoint(client: EpifanioRentalClient):
    """Verify live retrieval of photos from /t27/lista_imoveis_fotos.php."""
    gallery = client.get_photos("4198561")
    assert len(gallery) > 0
    assert gallery.first_photo().startswith("https://www.epifanioimoveis.com/imagens/imoveis/")
