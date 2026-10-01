# Epifânio Imóveis Rental Research MCP

Central rental research module and reverse-engineered API integration for **Epifânio Imóveis** (`epifanioimoveis.com`).

## Documentation
- **API Specification & Reverse Engineering**: [docs/api-research.md](docs/api-research.md)
- **Research Plan & Findings Report**: [scripts/research-plan.md](scripts/research-plan.md)

## Key Features
- **Rental & Sales Search Flow**: Full reproduction of rental and sale search with filters (bedrooms, suites, bathrooms, parking spaces, min/max price, area, order).
- **Canonical Routing & URL Construction**: Implements ImobiBrasil SEO paths and query parameter encoding.
- **Pagination**: 15 listings per page with robust termination detection.
- **Property Details & Microdata**: Extraction of structured metadata from `Schema.org` JSON-LD (`RentAction`, `BuyAction`, `Product`) and HTML elements.
- **Photo Gallery AJAX Extraction**: Direct high-resolution image retrieval via `/t27/lista_imoveis_fotos.php`.
- **Location Catalog Discovery**: Dynamic extraction of portal municipalities and neighborhood identifiers.
- **Design Principles**: Strict adherence to SOLID, Clean Code, and Object Calisthenics (0 `else` keywords, <= 2 instance variables per class, functions <= 15 lines, classes <= 100 lines, modules < 200 lines).

## Quick Start

### Installation
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Run Verification Script
```bash
python scripts/verify_research.py
```

### Run Automated Tests
```bash
pytest
```

## Python API Example

```python
from epifanio_research import EpifanioRentalClient, SearchCriteria, PropertyType

client = EpifanioRentalClient()

# Search rentals in Timóteo
rentals = client.search_rentals(city="timoteo")
for item in rentals:
    print(item.identity.property_id, item.title, item.price_text)

# Retrieve property details
detail = client.get_details("4198561")
print(detail.overview.title, detail.pricing.amount, detail.location.neighborhood)

# Retrieve photo gallery
photos = client.get_photos("4198561")
print(f"Loaded {len(photos)} photos. First: {photos.first_photo()}")
```
