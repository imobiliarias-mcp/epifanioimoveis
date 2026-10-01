# Reverse-Engineered API Specification: Epifânio Imóveis

## 1. Overview & Architecture

Epifânio Imóveis (`https://www.epifanioimoveis.com`) is a real estate agency portal built on top of the **ImobiBrasil** SaaS real estate engine (`s0/funcoes_busca.php`, template `t27`).

The portal serves server-side rendered HTML (charset `ISO-8859-1` / Latin1) with structured microdata (`Schema.org` JSON-LD) and a dedicated JSON AJAX endpoint for property photo galleries.

### 1.1 Authentication & Security Requirements
- **Authentication**: **None required**. All listing searches, filter queries, pagination requests, property details, and gallery photos are publicly accessible without authentication, session cookies, API keys, or CSRF tokens.
- **Request Headers**: Standard desktop `User-Agent` is required to prevent anti-bot generic blocks. No proprietary headers or cookies are needed.
- **HTTP Methods**: All research operations (search, filter, pagination, detail retrieval, photos) utilize `GET`.

---

## 2. Rental & Sales Search Endpoints

The search engine maps high-level criteria into hierarchical SEO paths and query string parameters.

### 2.1 Canonical Search Routing Pattern

```http
GET /imovel/{finalidade}/{tipo}/{cidade}/{bairro}/?&{query_parameters} HTTP/1.1
Host: www.epifanioimoveis.com
```

#### Path Variables
| Segment | Type | Allowed Values | Description |
| :--- | :--- | :--- | :--- |
| `{finalidade}` | `string` | `locacao`, `venda` | Transaction purpose (`locacao` for rentals, `venda` for sales). |
| `{tipo}` | `string` | `todos`, `apartamento`, `casa`, `lote`, `sala-comercial`, `sitio-chacara`, `terreno`, `cobertura`, `chacara`, `ponto-comercial`, `duplex`, `casa-geminada`, `imovel-comercial`, `residencial-e-comercial`, `salao-de-festa`, `apartamento-terreo`, `loja-comercial` | Property category. Default is `todos`. |
| `{cidade}` | `string` | `todos`, `timoteo`, `coronel-fabriciano`, `ipatinga`, `antonio-dias`, `contagem`, etc. | City slug. Default is `todos` or specific municipality. |
| `{bairro}` *(Optional)* | `string` | e.g. `timirim-479695`, `funcionarios-479319` | Single neighborhood slug with numeric ID. (When filtering multiple neighborhoods, this segment is omitted and `?bairros=` is used instead). |

#### Routing & Normalization Rules
1. **Friendly URL Redirection**: Accessing `/imovel?finalidade=locacao&cidade=timoteo` triggers an HTTP 302 redirect to canonical `/imovel/locacao/todos/timoteo`.
2. **Single Neighborhood Redirection**: Passing `?&bairro=timirim-479695` redirects to the path `/imovel/locacao/todos/timoteo/timirim-479695`.
3. **Query Prefix**: The portal expects query parameters prefixed by `/?&` (e.g. `/imovel/venda/todos/timoteo/?&dormitorios=2&vma=1600000`).

---

## 3. Request Parameters & Filter Behavior

All search filters can be combined in the query string:

| Parameter | Type | Example Values | ImobiBrasil Internal Logic / Description |
| :--- | :--- | :--- | :--- |
| `dormitorios` | `integer` | `1`, `2`, `3`, `4`, `5`, `21`, `22`, `23`, `24`, `25` | **Bedrooms constraint**.<br>• Exact count: values `1` through `5`.<br>• Minimum ("N or more"): values `20 + N` (`21` for 1+, `22` for 2+, `23` for 3+, etc.). |
| `suites` | `integer` | `1`, `2`, `3`, `4`, `5`, `21`, `22`, `23`, `24`, `25` | **Suites constraint**.<br>• Exact count: `1`..`5`.<br>• Minimum: `21`..`25`. |
| `banheiros` | `integer` | `1`, `2`, `3`, `4`, `5`, `21`, `22`, `23`, `24`, `25` | **Bathrooms constraint**.<br>• Exact count: `1`..`5`.<br>• Minimum: `21`..`25`. |
| `vagas` | `integer` | `1`, `2`, `3`, `4`, `5`, `21`, `22`, `23`, `24`, `25` | **Parking spaces constraint**.<br>• Exact count: `1`..`5`.<br>• Minimum: `21`..`25`. |
| `vmi` | `integer` | `1000` | **Minimum value** (Valor Mínimo) in BRL. |
| `vma` | `integer` | `1600000` | **Maximum value** (Valor Máximo) in BRL. |
| `areaMinima` | `integer` | `50` | Minimum built/land area in m². |
| `areaMaxima` | `integer` | `300` | Maximum built/land area in m². |
| `bairros` | `string` | `479695,479319` | Comma-separated list of numeric neighborhood IDs for multi-neighborhood filtering. |
| `ord` | `string` | `menor_valor`, `maior_valor`, `recentes` | Listing sort order. |
| `pag` | `integer` | `1`, `2`, `3`... | 1-indexed page number. Default is 1. |
| `ref` | `string` | `0423` | Property reference code. |
| `reftipo` | `string` | `exata` | Match precision for reference search (`exata`). |

---

## 4. Pagination Behavior

- **Page Size**: **15 listings per page** across all search categories.
- **Query Parameter**: `&pag={N}` (e.g. `/?pag=2` or `/?&dormitorios=2&pag=2`).
- **DOM Pagination Block**:
  - Container class: `.lista_imoveis_paginacao`
  - Current active page element: `a.lipagina-btn-paginacao-atual`
  - Other page links: `a.lipagina-btn-paginacao`
  - Next page button: `a.lipagina-btn-paginacao[title="Próxima Página"]` containing text `>`.
- **Termination / Out-of-Bounds Behavior**:
  - Requesting an out-of-bounds page (e.g. `pag=999`) returns HTTP 200 with an empty listing card collection (`0` cards).
  - The client detects end-of-results when the returned list of cards is empty or when no next page link (`>`) is present.

---

## 5. Search Results Card Parsing

Search result cards are rendered with the class `.imovelcard` and carry structured data attributes:

### 5.1 Card Structure & Selectors
```html
<div class="imovelcard" data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim">
  <a class="col imovelcard__img" href="/imovel/4198561/..." title="Apartamento para Locação...">
    <img src="https://imgs2.cdn-imobibrasil.com.br/imagens/imoveis/thumb15-...png" />
  </a>
  <div class="col imovelcard__infocontainer">
    <h2 class="imovelcard__info__tag">Locação</h2>
    <h2 class="imovelcard__info__local">Timirim, Timóteo / MG</h2>
    <p class="imovelcard__info__ref"><strong>Ref: 0423</strong> - Apartamento</p>
    <div class="imovelcard__info__feature"><i class="fa fa-bed"></i><p><b>3</b><span>Dormitórios</span></p></div>
    <div class="imovelcard__info__feature"><i class="fa fa-shower"></i><p><b>2</b><span>Banheiros</span></p></div>
    <div class="imovelcard__info__feature"><i class="fa fa-bath"></i><p><b>1</b><span>Suíte</span></p></div>
    <div class="imovelcard__info__feature"><i class="fa fa-car"></i><p><b>2</b><span>Vagas</span></p></div>
  </div>
  <div class="col imovelcard__valor">
    <p class="imovelcard__valor__valor"><span>R$</span> 2.930</p>
  </div>
</div>
```

### 5.2 Field Extraction Matrix
| Domain Field | DOM Selector / Expression | Example Extracted Value |
| :--- | :--- | :--- |
| `property_id` | `card.get('data-link').split('/')[2]` | `4198561` |
| `url_path` | `card.get('data-link')` | `/imovel/4198561/apartamento-locacao-timoteo-mg-timirim` |
| `title` | `card.select_one('.imovelcard__img')['title']` | `Apartamento para Locação, Timóteo / MG...` |
| `thumbnail_url` | `card.select_one('.imovelcard__img img')['src']` | `https://imgs2.cdn-imobibrasil.com.br/...` |
| `neighborhood` | `.imovelcard__info__local` text before `,` | `Timirim` |
| `city` | `.imovelcard__info__local` text between `,` and `/` | `Timóteo` |
| `state` | `.imovelcard__info__local` text after `/` | `MG` |
| `reference_code` | `.imovelcard__info__ref` regex `Ref:\s*([A-Za-z0-9_-]+)` | `0423` |
| `price_text` | `.imovelcard__valor__valor` | `R$ 2.930` or `Consulte` |
| `bedrooms` | `.imovelcard__info__feature i.fa-bed` sibling text | `3` |
| `suites` | `.imovelcard__info__feature i.fa-bath` sibling text | `1` |
| `bathrooms` | `.imovelcard__info__feature i.fa-shower` sibling text | `2` |
| `parking_spaces` | `.imovelcard__info__feature i.fa-car` sibling text | `2` |
| `area_text` | `.imovelcard__info__feature i.fa-arrows-h` sibling text | `300 m² Terreno` |

---

## 6. Property Detail Retrieval

Full property details are available via canonical URL or direct ID lookup.

### 6.1 Detail Endpoints
- **Direct ID Endpoint**: `GET https://www.epifanioimoveis.com/imovel/{property_id}`
- **Full SEO Endpoint**: `GET https://www.epifanioimoveis.com/imovel/{property_id}/{slug}`
- **Non-Existent ID Handling**: Returns an HTTP 302 redirecting to `/` (home page).

### 6.2 Structured Data (Schema.org JSON-LD)
The detail page embeds rich microdata:
- `Product`:
  - `mpn`: Property ID (`4198561`).
  - `offers.price`: Numeric price (`2930`).
  - `offers.priceCurrency`: Currency (`BRL`).
- `RentAction` / `BuyAction`:
  - `price`: Exact float string (`"2930.00"`).
  - `object.address.addressLocality`: Municipality (`"Timóteo"`).
  - `object.address.addressRegion`: State (`"MG"`).
  - `object.image`: Primary image URL.
- `BreadcrumbList`:
  - Hierarchy links and categories.

### 6.3 HTML Markup Extraction
- Headline: `h1` (`Apartamento para Locação, Timóteo / MG`).
- Reference & Neighborhood: `.info__col` (`Ref: 0423, bairro Timirim`).
- Quick Specification Badges: `.info__tag` (`3 Dormitórios`, `1 Suíte`, `2 Banheiros`, `2 Vagas`).
- Feature Groups: `.imovel_cx_caracteristicas` (Cômodos, Proximidades, Características).
- Description Text: `#desc_descricao p` or `.descricao p`.

---

## 7. Property Photo Gallery AJAX Endpoint

While the detail page embeds thumbnail and lead images, all high-resolution images are retrieved via a dedicated internal AJAX endpoint.

### 7.1 AJAX Photos Request
```http
GET /t27/lista_imoveis_fotos.php?imovel={property_id} HTTP/1.1
Host: www.epifanioimoveis.com
Accept: application/json, text/javascript, */*; q=0.01
```

### 7.2 AJAX Response Payload
```json
{
  "0": {
    "codigo_imo": "4198561",
    "arquivo_imm": "202604281705098957.png"
  },
  "1": {
    "codigo_imo": "4198561",
    "arquivo_imm": "202604281705127464.png"
  },
  "2": {
    "codigo_imo": "4198561",
    "arquivo_imm": "202604281705144702.png"
  }
}
```

### 7.3 Photo URL Resolution
- **Full Image URL**: `https://www.epifanioimoveis.com/imagens/imoveis/{arquivo_imm}`
- **CDN Direct URL**: `https://imgs2.cdn-imobibrasil.com.br/imagens/imoveis/{arquivo_imm}`
- **Thumbnail URL**: `https://www.epifanioimoveis.com/imagens/imoveis/li5.php?{arquivo_imm}`

---

## 8. Target URL Reproduction Analysis

### Target URL from Prompt
`https://www.epifanioimoveis.com/imovel/venda/todos/timoteo/?&dormitorios=2&vma=1600000`

### Breakdown
1. **Transaction (`finalidade`)**: `venda`
2. **Property Type (`tipo`)**: `todos`
3. **Location (`cidade`)**: `timoteo`
4. **Bedrooms (`dormitorios`)**: `2` (exact match)
5. **Maximum Price (`vma`)**: `1600000` (R$ 1.600.000,00)

### Equivalent Rental Query
`https://www.epifanioimoveis.com/imovel/locacao/todos/timoteo/?&dormitorios=2&vma=1600000`
- Maps to rental transaction (`finalidade=locacao`).
- Can also be queried for minimum 2 bedrooms using `dormitorios=22` (`20 + 2 = 22`).

---

## 9. Python MCP Client Integration Summary

The reverse-engineered endpoints are encapsulated inside `epifanio_research`:

```python
from epifanio_research import EpifanioRentalClient, SearchCriteria, PropertyType

client = EpifanioRentalClient()

# 1. Search rental listings in Timóteo
rentals = client.search_rentals(city="timoteo")
for listing in rentals:
    print(listing.identity.property_id, listing.title, listing.price_text)

# 2. Retrieve property details
details = client.get_details("4198561")
print(details.overview.title, details.pricing.amount, details.location.neighborhood)

# 3. Retrieve property gallery photos
photos = client.get_photos("4198561")
print(f"Loaded {len(photos)} photos. Lead: {photos.first_photo()}")
```
