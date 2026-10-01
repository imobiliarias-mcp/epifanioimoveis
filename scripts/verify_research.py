#!/usr/bin/env python3
"""Verification runner demonstrating reverse-engineered endpoints and MCP client."""

import sys
from pathlib import Path

# Ensure src is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

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


def run_target_search(client: EpifanioRentalClient) -> None:
    """Execute reproduction of user prompt target search."""
    print("--- 1. Target URL Search (Venda / 2 dorms / <= R$ 1.600.000) ---")
    criteria = SearchCriteria(
        scope=SearchScope(transaction=TransactionType.VENDA, property_type=PropertyType.TODOS),
        location=LocationCriteria(city_slug="timoteo"),
        filters=FilterBundle(price_range=PriceRange(maximum=1600000)),
        features=FeatureBundle(room_criteria=RoomCriteria(bedrooms=RoomCount(2))),
    )
    results = client.search(criteria)
    print(f"Total matching listings: {len(results)}")
    for item in results:
        print(f"  [{item.identity.property_id}] {item.title[:45]} | {item.price_text} | {item.location.neighborhood}")


def run_rental_search(client: EpifanioRentalClient) -> None:
    """Execute standard rental search in Timóteo."""
    print("\n--- 2. Timóteo Rental Listings Search ---")
    results = client.search_rentals(city="timoteo")
    print(f"Total rental listings: {len(results)}")
    for item in results[:5]:
        print(f"  [{item.identity.property_id}] {item.title[:45]} | {item.price_text}")


def run_detail_retrieval(client: EpifanioRentalClient) -> None:
    """Retrieve details for sample rental property."""
    print("\n--- 3. Property Detail Retrieval (Apartment 4198561) ---")
    detail = client.get_details("4198561")
    print(f"Title: {detail.overview.title}")
    print(f"Reference: {detail.overview.reference_code}")
    print(f"Price: R$ {detail.pricing.amount:,.2f}")
    print(f"Location: {detail.location.neighborhood}, {detail.location.city} - {detail.location.state}")
    print(f"Rooms: {detail.specs.bedrooms} dorms, {detail.specs.suites} suíte, {detail.specs.bathrooms} banheiros")


def run_photos_retrieval(client: EpifanioRentalClient) -> None:
    """Retrieve gallery photos via AJAX endpoint."""
    print("\n--- 4. Property Photos AJAX Retrieval ---")
    gallery = client.get_photos("4198561")
    print(f"Total photos retrieved: {len(gallery)}")
    for idx, photo_url in enumerate(list(gallery)[:3]):
        print(f"  Photo {idx + 1}: {photo_url}")


def run_catalog_discovery(client: EpifanioRentalClient) -> None:
    """Discover portal cities and neighborhoods."""
    print("\n--- 5. Portal Location Catalog Discovery ---")
    catalog = client.get_locations()
    print(f"Total municipalities in portal: {len(catalog)}")
    city = catalog.find_city_by_slug("timoteo")
    if city:
        print(f"City '{city.name}' has {len(city.neighborhoods)} indexed neighborhoods.")


def main() -> None:
    """Run all verification steps."""
    print("=== Starting Epifanio Imóveis Research Verification ===")
    client = EpifanioRentalClient()
    run_target_search(client)
    run_rental_search(client)
    run_detail_retrieval(client)
    run_photos_retrieval(client)
    run_catalog_discovery(client)
    print("\n=== All Verification Steps Completed Successfully ===")


if __name__ == "__main__":
    main()
