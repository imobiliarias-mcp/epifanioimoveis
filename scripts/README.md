# Central Rental Research MCP — Epifânio Imóveis Module

This package implements the **Epifânio Imóveis** rental search provider designed as a plug-and-play adapter for a **Central Rental Research MCP (Model Context Protocol)** server.

---

## 1. Architectural Highlights

- **SOLID Principles**: Single responsibility classes, interface segregation, dependency inversion.
- **Strict Object Calisthenics**:
  - One indent level per method.
  - Zero `else` keywords (guard clauses and early returns only).
  - Wrapped primitives (Value Objects for prices, coordinates, filters, codes).
  - First-class collections (`RentalListingCollection`, `FacetCollection`, `RentalSearchResult`).
  - One dot per line (intermediate assigned variables).
  - No abbreviations.
  - Entity size limits: functions ≤ 15 lines, classes ≤ 100 lines, modules < 200 lines.
  - ≤ 2 instance variables per class.
  - Tell, Don't Ask encapsulation.
- **Design Patterns**: Adapter, Strategy, Builder, Value Object, First-Class Collection, Factory.
- **Fail Fast**: Immediate boundary validation on inputs, raising descriptive typed domain exceptions.

---

## 2. Directory Layout

```
scripts/
├── README.md               # Package overview and developer instructions
├── ARCHITECTURE.md         # Calisthenics & SOLID design adherence documentation
├── USAGE.md                # Usage examples and MCP integration guide
├── research-plan.md        # Comprehensive reverse-engineering research plan & logs
├── verify_research.py      # Standalone verification runner
├── __init__.py
├── domain/                 # Pure domain layer
│   ├── __init__.py
│   ├── exceptions.py       # Domain exception hierarchy
│   ├── value_objects.py    # Immutable value objects (Price, Filter, Coordinates)
│   ├── entities.py         # Domain models (RentalListing, RentalPropertyDetail)
│   ├── criteria.py         # Search criteria and filter constraints
│   └── collections.py      # First-class collections (RentalListingCollection, etc.)
├── interfaces/             # Port contracts (MCP Provider Protocols)
│   ├── __init__.py
│   └── provider.py         # RentalProviderProtocol interface
├── client/                 # Infrastructure & ImobiBrasil HTTP client
│   ├── __init__.py
│   ├── configuration.py    # Epifânio portal configuration
│   ├── http_transport.py   # Desktop User-Agent HTTP transport
│   ├── query_builder.py    # Filter-to-query translator
│   └── parsers.py          # Response parsers
├── providers/              # Adapter layer
│   ├── __init__.py
│   └── epifanio.py         # EpifanioRentalProvider implementation
├── mcp/                    # MCP tool contracts & handlers
│   ├── __init__.py
│   └── tools.py            # Central Rental Research MCP tools
├── run_search.py           # CLI tool to run rental searches
├── run_property_detail.py  # CLI tool to fetch full property details
├── run_facets.py           # CLI tool to list search facets
└── run_tests.py            # Full test suite runner
```

---

## 3. Running the CLI Tools

### Search Rentals
```bash
# Basic rental search (defaults to Timóteo)
python3 scripts/run_search.py

# Filter by city, bedrooms, and maximum price
python3 scripts/run_search.py --city Timóteo --bedrooms 2 --max-price 3000
```

### Get Property Details
```bash
# Fetch complete detail for property code 4198561
python3 scripts/run_property_detail.py 4198561
```

### Inspect Search Facets
```bash
# Retrieve available cities and neighborhoods
python3 scripts/run_facets.py
```

### Run Automated Tests
```bash
# Execute unit and integration tests
python3 scripts/run_tests.py
```
