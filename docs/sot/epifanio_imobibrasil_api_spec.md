# ImobiBrasil Real Estate Platform API Specification — Epifânio Imóveis

## 1. Overview & Architecture

This document serves as the **Single Source of Truth (SOT)** for the reverse-engineered rental search and property management APIs powering **Epifânio Imóveis** (`https://www.epifanioimoveis.com/`).

### 1.1 Platform Identification

- **SaaS Vendor**: [ImobiBrasil](https://www.imobibrasil.com.br/) (real estate CRM & portal SaaS engine)
- **Backend Architecture**: PHP engine with Apache mod_rewrite (`s0/funcoes_busca.php`, `s0/scripts.php`)
- **Frontend Template**: Template `t27` (`/t27/js/lista_imoveis.js`, `/t27/lista_imoveis_fotos.php`)
- **Character Encoding**: `text/html; charset=iso-8859-1` (Latin1)
- **Asset / Media CDN**:
  - `https://imgs2.cdn-imobibrasil.com.br/imagens/imoveis/`
  - `https://cdn-img-src.imobibrasil.app.br/`
  - Local proxy path: `https://www.epifanioimoveis.com/imagens/imoveis/`

### 1.2 Authentication & Access Control

The ImobiBrasil public site does not require session cookies, OAuth tokens, or static API keys for listing search, details, or photos. Access is granted freely, provided that a standard desktop `User-Agent` header is supplied:

- **Mandatory Headers**:
  - `User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ...`
- **Security Behavior**:
  - Requests with the default `python-httpx` User-Agent are blocked with `HTTP 403 Forbidden`.
  - Supplying a standard desktop browser User-Agent returns `HTTP 200 OK`.

---

## 2. Endpoints Catalog

### 2.1 Property Search & Listings

Searches properties with filtering, sorting, and pagination.

- **URL**: `GET https://www.epifanioimoveis.com/imovel/{finalidade}/{tipo}/{cidade}/{bairro}/?&{query_parameters}`
- **Headers**: `User-Agent`
- **Path Parameters**:

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :---: | :--- |
| `finalidade` | `string` | Yes | `locacao` | `locacao` (rental) or `venda` (sales) |
| `tipo` | `string` | Yes | `todos` | Category slug (`apartamento`, `casa`, `lote`, `sala-comercial`, etc.) |
| `cidade` | `string` | Yes | `todos` | Municipality slug (e.g. `timoteo`, `coronel-fabriciano`) |
| `bairro` | `string` | No | - | Optional single neighborhood slug-id (e.g. `timirim-479695`) |

- **Query Parameters**:

| Parameter | Type | Description | Format / Values |
| :--- | :--- | :--- | :--- |
| `dormitorios` | `integer` | Bedroom constraint | Exact: `1`..`5`; Minimum ($N+$): `20 + N` (`21`..`25`) |
| `suites` | `integer` | Suite constraint | Exact: `1`..`5`; Minimum ($N+$): `20 + N` (`21`..`25`) |
| `banheiros` | `integer` | Bathroom constraint | Exact: `1`..`5`; Minimum ($N+$): `20 + N` (`21`..`25`) |
| `vagas` | `integer` | Parking space constraint | Exact: `1`..`5`; Minimum ($N+$): `20 + N` (`21`..`25`) |
| `vmi` | `integer` | Minimum price in BRL | e.g. `1000` |
| `vma` | `integer` | Maximum price in BRL | e.g. `3000` |
| `areaMinima` | `integer` | Minimum area in m² | e.g. `50` |
| `areaMaxima` | `integer` | Maximum area in m² | e.g. `250` |
| `bairros` | `string` | Multi-neighborhood filtering | Comma-separated IDs (`479695,479319`) |
| `ord` | `string` | Ordering | `menor_valor`, `maior_valor`, `recentes` |
| `pag` | `integer` | Page index (1-based) | `1`, `2`, `3`... (15 items/page) |
| `ref` | `string` | Reference code | e.g. `0423` |
| `reftipo` | `string` | Match mode | `exata` |

---

### 2.2 Property Details Endpoint

Retrieves full property specifications and structured microdata.

- **Direct ID URL**: `GET https://www.epifanioimoveis.com/imovel/{property_id}`
- **SEO Canonical URL**: `GET https://www.epifanioimoveis.com/imovel/{property_id}/{slug}`
- **Parameters**:
  - `property_id` (numeric string): Internal property code (e.g. `4198561`)
- **Error Behavior**:
  - Requesting an invalid or unpublished property ID issues an `HTTP 302` redirect to `/` (home page).

---

### 2.3 Property Photo Gallery AJAX Endpoint

Retrieves high-resolution gallery image file names for a listing.

- **URL**: `GET https://www.epifanioimoveis.com/t27/lista_imoveis_fotos.php?imovel={property_id}`
- **Headers**: `User-Agent`, `Accept: application/json`
- **Parameters**:
  - `imovel` (numeric string): Internal property code (e.g. `4198561`)
- **Response Schema (`HTTP 200`)**:
```json
{
  "0": {
    "codigo_imo": "4198561",
    "arquivo_imm": "202604281705098957.png"
  },
  "1": {
    "codigo_imo": "4198561",
    "arquivo_imm": "202604281705127464.png"
  }
}
```

---

### 2.4 Location Metadata Discovery

Available municipalities and neighborhoods are embedded in the search page JavaScript as global arrays within `dgCidadesBairros`:

```javascript
cidades : [
  ['', '- todas as cidades -'],
  ['timoteo', 'Timóteo'],
  ['coronel-fabriciano', 'Coronel Fabriciano'],
  ['ipatinga', 'Ipatinga']
],
bairros : [
  [''],
  ['Timirim', 'Funcionários', 'Centro', ...],
  ['Professores', 'Centro', ...]
],
bairros_value : [
  [''],
  ['timirim-479695', 'funcionarios-479319', 'centro-479547', ...],
  ['professores-553908', 'centro-479547', ...]
]
```
The numeric suffix of each slug (e.g. `479695` in `timirim-479695`) represents the neighborhood ID passed to `?bairros=`.
