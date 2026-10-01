# Central Rental Research MCP Architecture & Design Standards — Epifânio Imóveis

## 1. Context: Central Rental Research MCP

The **Central Rental Research MCP** aims to unify rental search capabilities across diverse real estate sources (regional portals, agency systems, multi-listing services).

To achieve seamless pluggability, each real estate provider is developed as an isolated module exposing a uniform contract (`RentalProviderProtocol`). The **Epifânio Imóveis** module integrates with the underlying **ImobiBrasil SaaS Engine** while presenting a domain model completely agnostic of ImobiBrasil's internal quirks.

---

## 2. Object Calisthenics Compliance

Every file and class in this codebase adheres strictly to the 9 rules of Object Calisthenics:

### Rule 1: Only One Level of Indentation per Method
Methods never nest loops inside conditionals or conditionals inside loops. Complex logic is broken down into concise, single-purpose helper methods.

### Rule 2: Don't Use the `else` Keyword
The `else` keyword is strictly prohibited. Guard clauses with early returns and polymorphic handlers handle branching without `else` branches. Across the entire `scripts/` package, there are **0 occurrences** of the `else` keyword.

### Rule 3: Wrap All Primitives and Strings
Domain concepts are represented as strongly-typed Value Objects:
- `ListingPrice`: Validates non-negative currency amounts in BRL.
- `PropertyCode`: Validates non-empty string codes.
- `GeoCoordinate`: Validates latitude (-90 to +90) and longitude (-180 to +180).
- `RentalFilter`: Validates search criteria (e.g. `min_price <= max_price`).
- `PriceRange`, `LocationCriteria`, `SpecificationCriteria`, `SearchPagination`.

### Rule 4: First-Class Collections
Any class holding a collection contains no other instance variables. Collections are wrapped in dedicated domain classes:
- `RentalListingCollection`: Wraps `tuple[RentalListing, ...]`.
- `FacetCollection`: Wraps facet groups (`cities`, `neighborhoods`).
- `RentalSearchResult`: Encapsulates collection and total remote matching count.

### Rule 5: One Dot per Line
Chaining multiple method calls (e.g. `obj.a().b().c()`) violates the Law of Demeter. Intermediate variables are explicitly assigned on their own lines.

### Rule 6: Don't Abbreviate
All symbols use descriptive, clear names. Abbreviations such as `res`, `req`, `mgr`, `btn`, `val`, `cur` are avoided in favor of `response`, `request`, `manager`, `button`, `value`, `cursor`.

### Rule 7: Keep All Entities Small
Strict size ceilings:
- Functions and methods: **≤ 15 lines**.
- Classes: **≤ 100 lines**.
- Modules / files: **< 200 lines**.

### Rule 8: No Classes with More Than 2 Instance Variables
Classes declare at most 2 member attributes. Classes with richer state decompose into focused composite value objects or collaborators.

### Rule 9: No Getters / Setters / Properties Exposing Raw State (Tell, Don't Ask)
Objects expose behaviors and formatting methods (`format_brl()`, `format_summary()`, `to_dictionary()`), rather than acting as passive data bags.

---

## 3. SOLID Principles Compliance

1. **Single Responsibility (SRP)**:
   - `EpifanioHttpTransport`: HTTP client and header management.
   - `RentalQueryBuilder`: Query parameter and canonical route construction.
   - `SearchResultParser`: Search HTML deserialization and domain conversion.
   - `PropertyDetailParser`: Detail HTML + JSON-LD deserialization.
   - `FacetParser`: City and neighborhood metadata extraction.
   - `EpifanioRentalProvider`: Provider orchestration.

2. **Open / Closed (OCP)**:
   New real estate providers implement `RentalProviderProtocol` without modifying the MCP tools or core pipeline.

3. **Liskov Substitution (LSP)**:
   `EpifanioRentalProvider` satisfies all invariants of `RentalProviderProtocol`. Substituting it with any other provider yields predictable, equivalent behavioral contracts.

4. **Interface Segregation (ISP)**:
   Sub-interfaces (`RentalSearchCapability`, `RentalDetailCapability`, `RentalFacetsCapability`) ensure callers depend only on the methods they use.

5. **Dependency Inversion (DIP)**:
   High-level MCP tools depend on the abstract `RentalProviderProtocol`, injected at runtime.

---

## 4. Design Patterns Applied

- **Adapter Pattern**: Translates ImobiBrasil HTML / JSON-LD schemas into MCP standardized domain entities.
- **Strategy Pattern**: Pluggable provider strategy across multiple rental platforms.
- **Builder Pattern**: Fluent and clean parameter building via `RentalQueryBuilder`.
- **Value Object Pattern**: Immutable, self-validating primitives.
- **First-Class Collection Pattern**: Encapsulated collection behaviors.
- **Factory Pattern**: Default provider constructors encapsulate dependency graphs.
