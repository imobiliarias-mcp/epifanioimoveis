# ADR 0001: Architecture & Design of Central Rental Research MCP Modules (Epifânio Imóveis)

## Status
Accepted

## Context

The system requires reverse-engineering the rental property search API of **Epifânio Imóveis** (`https://www.epifanioimoveis.com/`) and architecting modular Python components intended for integration into a **Central Rental Research MCP (Model Context Protocol)** server.

A central MCP server allows AI assistants and client applications to query multiple real estate platforms (e.g. Casa Linhares, Epifânio Imóveis, Netimóveis, QuintoAndar) through a unified tool contract. To achieve this, the integration must not be a monolithic scraping script, but rather a decoupled, highly cohesive, modular architecture.

Furthermore, the implementation must strictly satisfy:
- **SOLID Principles**
- **Clean Code**
- **Object Calisthenics** (9 strict rules)
- **Design Patterns** (Adapter, Strategy, Value Object, First-Class Collection, Factory)
- **Fail-Fast input validation**
- **Defensive error handling**

---

## Decision

We adopt a **Hexagonal / Ports-and-Adapters Architecture** partitioned into four explicit layers:

```
┌────────────────────────────────────────────────────────┐
│               Central Rental Research MCP              │
│               (Model Context Protocol Tools)           │
└──────────────────────────┬─────────────────────────────┘
                           │ uses Port (Protocol)
                           ▼
┌────────────────────────────────────────────────────────┐
│                   Domain Layer                         │
│  - Value Objects (Price, Coordinates, Filter, Codes)   │
│  - First-Class Collections (Listings, Facets)          │
│  - Domain Exceptions                                   │
│  - Provider Port Interface (RentalProviderProtocol)    │
└──────────────────────────▲─────────────────────────────┘
                           │ implements Port
┌──────────────────────────┴─────────────────────────────┐
│                 Adapter / Provider Layer               │
│  - EpifanioRentalProvider                              │
│  - Adapts ImobiBrasil HTML/JSON to Domain Entities     │
└──────────────────────────┬─────────────────────────────┘
                           │ coordinates
┌──────────────────────────▼─────────────────────────────┐
│                  Infrastructure Layer                  │
│  - EpifanioConfiguration (Portal URLs & defaults)      │
│  - EpifanioHttpTransport (Desktop User-Agent, Latin1)  │
│  - RentalQueryBuilder (Canonical path & params)        │
│  - Parsers (SearchResultParser, DetailParser, etc.)    │
└────────────────────────────────────────────────────────┘
```

---

## Object Calisthenics Enforcement Matrix

| Calisthenics Rule | Implementation Strategy in Python |
| :--- | :--- |
| **1. One level of indentation per method** | Deep loops and branching are decomposed into named single-purpose private helper methods. |
| **2. Don't use the `else` keyword** | Guard clauses, early returns, polymorphic strategies, or dictionary dispatch tables are used exclusively. Zero `else` keywords across the codebase. |
| **3. Wrap all primitives and strings** | Raw primitives are wrapped in domain value objects: `ListingPrice`, `PropertyCode`, `GeoCoordinate`, `RentalFilter`, `SearchPagination`. |
| **4. First-class collections** | Any class containing a collection contains no other member fields, exposing only domain collection operations: `RentalListingCollection`, `FacetCollection`, `RentalSearchResult`. |
| **5. One dot per line** | No deep chaining (`a.b().c()`). Every intermediate object is assigned to an explicitly named local variable. |
| **6. Don't abbreviate** | Descriptive domain naming throughout (`response`, `request`, `listing`, `property_entity`, `search_filter`, `neighborhood`). |
| **7. Keep all entities small** | Functions ≤ 15 lines, classes ≤ 100 lines, modules < 200 lines. |
| **8. No classes with more than 2 instance variables** | Classes declare at most 2 member attributes. Larger state is factored into value objects or collaborator objects. |
| **9. No getters/setters (Tell, Don't Ask)** | Domain objects encapsulate their state and expose behaviors or representations (`format_brl()`, `format_summary()`, `to_dictionary()`), not mutable getters/setters. |

---

## SOLID Principles Application

### Single Responsibility Principle (SRP)
- `EpifanioHttpTransport`: Strictly responsible for low-level HTTP transport and User-Agent headers.
- `RentalQueryBuilder`: Strictly responsible for converting high-level `RentalFilter` to URL path and query parameters.
- `SearchResultParser`: Strictly responsible for validating and parsing raw HTML into `RentalSearchResult`.
- `PropertyDetailParser`: Strictly responsible for parsing detail HTML and JSON-LD microdata.
- `FacetParser`: Strictly responsible for extracting city and neighborhood metadata.
- `EpifanioRentalProvider`: Strictly responsible for orchestrating the client components to fulfill `RentalProviderProtocol`.

### Open/Closed Principle (OCP)
The central MCP server interacts exclusively with `RentalProviderProtocol`. New real estate platforms (e.g. Casa Linhares, Netimóveis) integrate as peer providers without modifying existing tool handlers.

### Liskov Substitution Principle (LSP)
`EpifanioRentalProvider` satisfies all invariants of `RentalProviderProtocol`. Substituting it with `CasaLinharesRentalProvider` or any other provider yields predictable, equivalent behavioral contracts.

### Interface Segregation Principle (ISP)
The provider capabilities are split into focused sub-protocols:
- `RentalSearchCapability` (`search_rentals`)
- `RentalDetailCapability` (`get_property_detail`)
- `RentalFacetsCapability` (`get_facets`)

### Dependency Inversion Principle (DIP)
High-level MCP tools depend entirely on the abstraction (`RentalProviderProtocol`), which is injected via constructors or factory methods.

---

## Design Patterns

1. **Adapter Pattern**: Translates ImobiBrasil-specific HTML and JSON schemas into standardized MCP domain entities (`ListingPrice`, `RentalListing`, `RentalPropertyDetail`).
2. **Strategy Pattern**: The MCP server selects and executes search strategies across registered real estate providers.
3. **Value Object Pattern**: `ListingPrice`, `PropertyCode`, `GeoCoordinate`, and `RentalFilter` are immutable (`frozen=True`) value objects with built-in validation.
4. **First-Class Collection Pattern**: `RentalListingCollection` and `FacetCollection` manage items without exposing raw collections to external tampering.
5. **Builder Pattern**: `RentalQueryBuilder` cleanly constructs complex query parameter dictionaries and canonical paths step-by-step.
6. **Factory Pattern**: Default provider constructors encapsulate initialization of transport, query builder, and parsers.

---

## Consequences & Benefits

- **High Modularity**: Can be imported as an isolated Python package directly into any central MCP repository alongside Casa Linhares.
- **Unified Contracts**: Tool calls in MCP servers execute identically regardless of whether querying Casa Linhares or Epifânio Imóveis.
- **Zero Monolithic Bloat**: Strict adherence to size and calisthenics limits guarantees clean, readable, easily maintainable and testable code.
