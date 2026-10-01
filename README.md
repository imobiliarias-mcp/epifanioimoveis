# Epifânio Imóveis — Central Rental Research MCP Provider

Reverse-engineered rental search engine and API client for **Epifânio Imóveis** (`https://www.epifanioimoveis.com/`).

Engineered as a pluggable adapter for the **Central Rental Research MCP (Model Context Protocol)** server following **SOLID**, **Clean Code**, **Object Calisthenics**, and **Design Patterns** in Python, operating as a sister provider to **Casa Linhares**.

---

## 📚 Documentation

- **[Documentation Index](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/README.md)** (`docs/README.md`): Overview of all project documentation.
- **[Single Source of Truth (SOT) API Spec](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/sot/epifanio_imobibrasil_api_spec.md)** (`docs/sot/epifanio_imobibrasil_api_spec.md`): Complete endpoint contracts, payload schemas, query parameters, and ImobiBrasil SaaS platform architecture.
- **[ADR 0001: MCP Architecture & Design](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/adr/0001-rental-search-mcp-module-design.md)** (`docs/adr/0001-rental-search-mcp-module-design.md`): Hexagonal architecture, Object Calisthenics enforcement, and design patterns.
- **[API Reference](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/api_reference.md)** (`docs/api_reference.md`): Ready-to-use cURL recipes and parameter matrices.
- **[Reverse Engineering Analysis](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/api-research.md)** (`docs/api-research.md`): Initial reverse-engineering investigation notes and DOM selectors.
- **[Scripts & MCP Module Guide](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/scripts/README.md)** (`scripts/README.md`): Package layout and CLI runner guide.
- **[Architecture Standards](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/scripts/ARCHITECTURE.md)** (`scripts/ARCHITECTURE.md`): Calisthenics and SOLID compliance breakdown.
- **[Usage & MCP Integration](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/scripts/USAGE.md)** (`scripts/USAGE.md`): How to use the Python modules and integrate into MCP servers.
- **[Research Plan & Findings Report](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/scripts/research-plan.md)** (`scripts/research-plan.md`): Reverse-engineering methodology and probing execution log.

---

## ⚡ Quickstart

### Run Automated Tests
```bash
python3 scripts/run_tests.py
```

### Search Rentals
```bash
# Search rentals in Timóteo
python3 scripts/run_search.py --city Timóteo --max-price 2500

# Search rentals with minimum 2 bedrooms
python3 scripts/run_search.py --city Timóteo --bedrooms 2
```

### View Listing Details
```bash
# View complete details for property code 4198561
python3 scripts/run_property_detail.py 4198561
```

### Inspect Available Localities & Facets
```bash
python3 scripts/run_facets.py
```

---

## 🏛️ Code Architecture & Standards Compliance

- **No `else` Keyword**: 100% eliminated using guard clauses, early returns, and polymorphic handlers.
- **Single Level of Indentation**: All methods adhere to at most 1 indent level.
- **Wrapped Primitives**: Domain concepts (`ListingPrice`, `PropertyCode`, `GeoCoordinate`, `RentalFilter`) are immutable Value Objects.
- **First-Class Collections**: `RentalListingCollection` and `FacetCollection` wrap items without leaking raw mutable collections.
- **Size Limits**: Functions ≤ 15 lines, Classes ≤ 100 lines, Modules < 200 lines.
- **Instance Variables**: All classes hold at most 2 instance variables.
- **One Dot per Line**: Method chaining is eliminated in favor of explicit intermediate assignments.
- **Zero Abbreviations**: Clear, descriptive domain naming across all modules.
