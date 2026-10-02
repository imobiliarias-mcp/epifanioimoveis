# Epifânio Imóveis — Rental API Reverse Engineering Documentation

Welcome to the reverse-engineering and architecture documentation for **Epifânio Imóveis** (`https://www.epifanioimoveis.com/`).

This repository contains the reverse-engineered API specifications, architectural decision records, and clean, modular Python components designed for integration into a **Central Rental Research MCP (Model Context Protocol)** server.

---

## Documentation Structure

- **[Single Source of Truth API Specification](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/sot/epifanio_imobibrasil_api_spec.md)** (`docs/sot/epifanio_imobibrasil_api_spec.md`):
  Comprehensive contract specification for all endpoints, headers, payload schemas, query matrices, and URL rewriting rules.

- **[Architecture Decision Record 0001](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/adr/0001-rental-search-mcp-module-design.md)** (`docs/adr/0001-rental-search-mcp-module-design.md`):
  Detailed rationale on Ports-and-Adapters (Hexagonal) architecture, SOLID principles, Design Patterns, and strict Object Calisthenics enforcement.

- **[API Reference & Quick Recipes](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/api_reference.md)** (`docs/api_reference.md`):
  Developer reference featuring ready-to-run `curl` commands, parameter dictionaries, and implementation recipes.

- **[Reverse Engineering Analysis](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/docs/api-research.md)** (`docs/api-research.md`):
  Primary research notes, routing mechanics, JSON-LD microdata structure, and ImobiBrasil SaaS analysis.

- **[Scripts & MCP Module Guide](file:///home/samuelcaldas/repos/imobiliarias/epifanioimoveis/scripts/README.md)** (`scripts/README.md`):
  Developer guide for running the Python modules, CLI utilities, and MCP tool handlers.

---

## Key Technical Discoveries Summary

| Dimension | Discovery |
| :--- | :--- |
| **Underlying Platform** | ImobiBrasil SaaS (Real estate CRM & portal platform) |
| **Backend Router** | `s0/funcoes_busca.php` |
| **Search Route** | `/imovel/{finalidade}/{tipo}/{cidade}/{bairro}/?&{params}` |
| **Room Parameter Encoding** | Exact: `1`..`5`; Minimum ($N+$): `20 + N` (`21` for 1+, `22` for 2+, etc.) |
| **Numeric Filters** | `vmi` (min price), `vma` (max price), `areaMinima`, `areaMaxima` |
| **Multi-Neighborhood Filter** | `?&bairros={id1},{id2}` (logical OR) |
| **Pagination Model** | 15 listings per page via `&pag={N}` |
| **Property Detail Endpoint** | Direct ID `/imovel/{id}` and canonical `/imovel/{id}/{slug}` |
| **Search Result Link** | Serialized listing `url` is absolute; original `url_path` and identifying queries are retained |
| **Microdata Extraction** | `Schema.org` JSON-LD (`Product`, `RentAction`, `BuyAction`) |
| **Photo Gallery AJAX** | `GET /t27/lista_imoveis_fotos.php?imovel={id}` returning JSON array |
| **Authentication Requirement** | **None** (Public search and detail views; desktop User-Agent required) |
