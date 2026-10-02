# Epifânio Imóveis — API Reference & Quick Recipes

This reference provides ready-to-use cURL recipes and parameter dictionaries for querying **Epifânio Imóveis** (`epifanioimoveis.com`).

---

## 1. Quick Recipes (cURL)

### 1.1 All Rental Listings in Timóteo
```bash
curl -s "https://www.epifanioimoveis.com/imovel/locacao/todos/timoteo" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

### 1.2 Target Prompt Search (2 Bedrooms, Max Price R$ 1.600.000)
```bash
curl -s "https://www.epifanioimoveis.com/imovel/venda/todos/timoteo/?&dormitorios=2&vma=1600000" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

### 1.3 Filtered Rental Search (2+ Bedrooms, Max Price R$ 3.000)
```bash
curl -s "https://www.epifanioimoveis.com/imovel/locacao/todos/timoteo/?&dormitorios=22&vma=3000" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

### 1.4 Multi-Neighborhood Search (Timirim & Funcionários)
```bash
curl -s "https://www.epifanioimoveis.com/imovel/locacao/todos/timoteo/?&bairros=479695,479319" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

### 1.5 Property Detail Page by Direct ID
```bash
curl -s "https://www.epifanioimoveis.com/imovel/4198561" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

### 1.6 Property Photos JSON AJAX Endpoint
```bash
curl -s "https://www.epifanioimoveis.com/t27/lista_imoveis_fotos.php?imovel=4198561" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

---

## 2. Parameter Reference Matrix

| Parameter | Type | Allowed Values | Description |
| :--- | :--- | :--- | :--- |
| `finalidade` *(Path)* | `string` | `locacao`, `venda` | Transaction purpose (`locacao` = rental). |
| `tipo` *(Path)* | `string` | `todos`, `apartamento`, `casa`, `lote`, etc. | Typology filter. |
| `cidade` *(Path)* | `string` | `todos`, `timoteo`, `coronel-fabriciano`, etc. | Municipality slug. |
| `dormitorios` | `int` | `1`..`5` (exact), `21`..`25` (minimum $N+$) | Bedroom count constraint. |
| `suites` | `int` | `1`..`5` (exact), `21`..`25` (minimum $N+$) | Suite count constraint. |
| `banheiros` | `int` | `1`..`5` (exact), `21`..`25` (minimum $N+$) | Bathroom count constraint. |
| `vagas` | `int` | `1`..`5` (exact), `21`..`25` (minimum $N+$) | Parking spaces constraint. |
| `vmi` | `int` | e.g. `1000` | Minimum price in BRL. |
| `vma` | `int` | e.g. `2500` | Maximum price in BRL. |
| `areaMinima` | `int` | e.g. `60` | Minimum area in m². |
| `areaMaxima` | `int` | e.g. `200` | Maximum area in m². |
| `bairros` | `string` | e.g. `479695,479319` | Comma-separated neighborhood IDs. |
| `ord` | `string` | `menor_valor`, `maior_valor`, `recentes` | Sort order. |
| `pag` | `int` | `1`, `2`, `3`... | Page index (1-based, 15 items/page). |
| `ref` | `string` | e.g. `0423` | Property reference code. |
| `reftipo` | `string` | `exata` | Match precision for reference search. |

## 3. Search Result Property Links

Search result serializers provide an absolute public `url` for each property and retain its original `url_path`. Relative and protocol-relative card links are resolved against the configured public site origin, and identifying query parameters (for example, `?id=608`) are preserved. The CLI and MCP search results expose the same public URL; no additional detail request is issued to create it.
