"""Unit tests for domain value objects, criteria, and first-class collections."""

import pytest
from epifanio_research.domain.criteria import (
    FeatureBundle,
    FilterBundle,
    LocationCriteria,
    RoomCriteria,
    SearchCriteria,
    SearchScope,
)
from epifanio_research.domain.enums import PropertyType, SortOrder, TransactionType
from epifanio_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingLocation,
    ListingSpecs,
    ListingSummary,
)
from epifanio_research.domain.metadata import City, LocationCatalog, Neighborhood, NeighborhoodGroup
from epifanio_research.domain.property import PhotoGallery
from epifanio_research.domain.values import AreaRange, PageNumber, PriceRange, RoomCount


def test_price_range_query_parameters():
    """Verify price range generates vmi and vma query parameters."""
    rng = PriceRange(minimum=1000, maximum=2500)
    params = rng.query_parameters()
    assert params == {"vmi": "1000", "vma": "2500"}


def test_room_count_exact_and_minimum():
    """Verify room count converts to exact count or ImobiBrasil minimum 20+N."""
    exact = RoomCount(count=2, is_minimum=False)
    assert exact.to_param_code() == "2"

    minimum = RoomCount(count=2, is_minimum=True)
    assert minimum.to_param_code() == "22"


def test_page_number_validation():
    """Verify page number rejects invalid non-positive integers."""
    valid = PageNumber(1)
    assert valid.to_param_code() == "1"

    with pytest.raises(ValueError):
        PageNumber(0)


def test_search_criteria_rental_factory():
    """Verify convenience factory builds complete rental criteria."""
    criteria = SearchCriteria.create_rental(
        city="timoteo",
        property_type=PropertyType.APARTAMENTO,
        bedrooms=2,
        min_bedrooms=False,
        max_price=2000,
        page=1,
    )
    assert criteria.scope.transaction == TransactionType.LOCACAO
    assert criteria.scope.property_type == PropertyType.APARTAMENTO
    assert criteria.location.city_slug == "timoteo"
    assert criteria.filters.price_range.maximum == 2000


def test_listing_collection_iteration_and_indexing():
    """Verify first-class collection behavior for listings."""
    item = ListingSummary(
        identity=ListingIdentity(property_id="123", url_path="/imovel/123/teste"),
        title="Apartamento Teste",
        location=ListingLocation(neighborhood="Centro", city="Timóteo"),
        price_text="R$ 1.500",
        specs=ListingSpecs(bedrooms=2),
    )
    col = ListingCollection(items=(item,), current_page=1, has_next_page=False)
    assert len(col) == 1
    assert not col.is_empty()
    assert col[0].identity.property_id == "123"
    assert list(col)[0].title == "Apartamento Teste"


def test_photo_gallery_behavior():
    """Verify PhotoGallery methods and indexing."""
    gallery = PhotoGallery(photo_urls=("http://example.com/1.png", "http://example.com/2.png"))
    assert len(gallery) == 2
    assert gallery[0] == "http://example.com/1.png"
    assert gallery.first_photo() == "http://example.com/1.png"


def test_location_catalog_lookup():
    """Verify finding city and neighborhood inside catalog."""
    nb = Neighborhood(name="Timirim", slug="timirim-479695", numeric_id="479695")
    group = NeighborhoodGroup(items=(nb,))
    city = City(name="Timóteo", slug="timoteo", neighborhoods=group)
    catalog = LocationCatalog(cities=(city,))

    found_city = catalog.find_city_by_slug("timoteo")
    assert found_city is not None
    assert found_city.name == "Timóteo"

    found_nb = found_city.neighborhoods.find_by_name("Timirim")
    assert found_nb is not None
    assert found_nb.numeric_id == "479695"
