"""Unit tests for HTML, JSON-LD, and AJAX photo parsers."""

from epifanio_research.parsers.detail_parser import PropertyDetailParser
from epifanio_research.parsers.metadata_parser import MetadataParser
from epifanio_research.parsers.photo_parser import PhotoGalleryParser
from epifanio_research.parsers.search_parser import SearchPageParser

SEARCH_HTML_FIXTURE = """
<html>
<body>
  <div class="imovelcard" data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim">
    <a class="imovelcard__img" title="Apartamento para Locação" href="/imovel/4198561">
      <img src="https://imgs2.cdn-imobibrasil.com.br/thumb.png" />
    </a>
    <div class="imovelcard__info">
      <h2 class="imovelcard__info__local">Timirim, Timóteo / MG</h2>
      <p class="imovelcard__info__ref"><strong>Ref: 0423</strong> - Apartamento</p>
      <div class="imovelcard__info__feature"><i class="fa fa-bed"></i><p><b>3</b><span>Dormitórios</span></p></div>
      <div class="imovelcard__info__feature"><i class="fa fa-bath"></i><p><b>1</b><span>Suíte</span></p></div>
      <div class="imovelcard__info__feature"><i class="fa fa-shower"></i><p><b>2</b><span>Banheiros</span></p></div>
      <div class="imovelcard__info__feature"><i class="fa fa-car"></i><p><b>2</b><span>Vagas</span></p></div>
    </div>
    <div class="imovelcard__valor">
      <p class="imovelcard__valor__valor"><span>R$</span> 2.930</p>
    </div>
  </div>
  <div class="lista_imoveis_paginacao">
    <a class="lipagina-btn-paginacao-atual" href="/imovel/?pag=1">1</a>
    <a class="lipagina-btn-paginacao" href="/imovel/?pag=2" title="Próxima Página">&gt;</a>
  </div>
</body>
</html>
"""

DETAIL_HTML_FIXTURE = """
<html>
<head>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "RentAction",
    "price": "2930.00",
    "object": {
      "@type": "Place",
      "address": {"addressLocality": "Timóteo", "addressRegion": "MG"}
    }
  }
  </script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Product",
    "mpn": "4198561",
    "sku": "4198561"
  }
  </script>
</head>
<body>
  <h1>Apartamento para Locação, Timóteo / MG</h1>
  <div class="info__col">Apartamento para Locação, Timóteo / MG Ref: 0423, bairro Timirim</div>
  <div class="info__valor">R$ 2.930</div>
  <span class="info__tag">3 Dormitórios</span>
  <span class="info__tag">1 Suíte</span>
  <span class="info__tag">2 Banheiros</span>
  <span class="info__tag">2 Vagas</span>
  <div class="imovel_cx_caracteristicas">Cômodos Área de Serviço Copa Cozinha Despensa</div>
  <div class="descricao" id="desc_descricao">
    <p>Apartamento espaçoso no bairro Timirim.</p>
  </div>
</body>
</html>
"""

METADATA_HTML_FIXTURE = """
<html>
<body>
  <script>
    dgCidadesBairros.prototype = {
      cidades: [['', '- todas -'], ['timoteo', 'Timóteo']],
      bairros: [[''], ['Timirim', 'Funcionários']],
      bairros_value: [[''], ['timirim-479695', 'funcionarios-479319']]
    };
  </script>
</body>
</html>
"""


def test_search_page_parser():
    """Verify search parser extracts listings and pagination correctly."""
    parser = SearchPageParser()
    col = parser.parse(SEARCH_HTML_FIXTURE, page_number=1)
    assert len(col) == 1
    assert col.current_page == 1
    assert col.has_next_page is True

    card = col[0]
    assert card.identity.property_id == "4198561"
    assert card.location.neighborhood == "Timirim"
    assert card.location.city == "Timóteo"
    assert card.reference_code == "0423"
    assert card.price_text == "R$ 2.930"
    assert card.specs.bedrooms == 3
    assert card.specs.suites == 1
    assert card.specs.bathrooms == 2
    assert card.specs.parking_spaces == 2


def test_property_detail_parser():
    """Verify detail parser extracts overview, pricing, location, and specs."""
    parser = PropertyDetailParser()
    detail = parser.parse(DETAIL_HTML_FIXTURE, property_id="4198561", canonical_url="http://test/4198561")
    assert detail.overview.property_id == "4198561"
    assert detail.overview.title == "Apartamento para Locação, Timóteo / MG"
    assert detail.overview.reference_code == "0423"
    assert "Timirim" in detail.overview.description
    assert detail.pricing.amount == 2930.0
    assert detail.location.city == "Timóteo"
    assert detail.location.neighborhood == "Timirim"
    assert detail.specs.bedrooms == 3
    assert detail.specs.suites == 1
    assert len(detail.characteristics) == 1


def test_photo_gallery_parser_json():
    """Verify photo gallery parser constructs correct image URLs from AJAX response."""
    parser = PhotoGalleryParser()
    json_data = '{"0": {"codigo_imo": "4198561", "arquivo_imm": "foto1.png"}, "1": {"codigo_imo": "4198561", "arquivo_imm": "foto2.png"}}'
    gallery = parser.parse_ajax_json(json_data)
    assert len(gallery) == 2
    assert gallery[0] == "https://www.epifanioimoveis.com/imagens/imoveis/foto1.png"
    assert gallery[1] == "https://www.epifanioimoveis.com/imagens/imoveis/foto2.png"


def test_metadata_parser():
    """Verify metadata parser extracts cities and neighborhoods catalog."""
    parser = MetadataParser()
    catalog = parser.parse(METADATA_HTML_FIXTURE)
    assert len(catalog) == 1
    city = catalog.find_city_by_slug("timoteo")
    assert city is not None
    assert len(city.neighborhoods) == 2
    nb = city.neighborhoods.find_by_name("Timirim")
    assert nb is not None
    assert nb.numeric_id == "479695"


def test_search_page_parser_exposes_absolute_public_url():
    """Resolve the listing path without discarding an identifying query."""
    path = "/imovel/4198561/apartamento-locacao-timoteo-mg-timirim?id=608"
    html = SEARCH_HTML_FIXTURE.replace(
        'data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"',
        f'data-link="{path}"',
    )
    listing = SearchPageParser().parse(html)[0]

    assert listing.identity.url_path == path
    assert getattr(listing, "url", None) == f"https://www.epifanioimoveis.com{path}"


def test_listing_collection_serializes_public_url_and_pagination():
    """Serialize property URLs alongside typed collection metadata."""
    collection = SearchPageParser().parse(SEARCH_HTML_FIXTURE, page_number=3)
    serialized = collection.to_dictionary()

    assert serialized["items"][0]["url"] == (
        "https://www.epifanioimoveis.com/imovel/4198561/"
        "apartamento-locacao-timoteo-mg-timirim"
    )
    assert serialized["items"][0]["url_path"].startswith("/imovel/4198561/")
    assert serialized["current_page"] == 3
    assert serialized["has_next_page"] is True


def test_search_parser_rejects_non_public_property_links():
    """Reject schemes, image/search destinations, and site roots."""
    import pytest

    invalid_links = (
        "javascript:alert(1)",
        "https://evil.example/imovel/4198561/apartamento",
        "https://www.epifanioimoveis.com/imagens/4198561.jpg",
        "https://www.epifanioimoveis.com/imovel/locacao/todos/timoteo",
        "https://www.epifanioimoveis.com/",
    )
    for invalid_link in invalid_links:
        invalid_html = SEARCH_HTML_FIXTURE.replace(
            'data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"',
            f'data-link="{invalid_link}"',
        ).replace('href="/imovel/4198561"', f'href="{invalid_link}"')
        with pytest.raises(ValueError, match="invalid public URL"):
            SearchPageParser().parse(invalid_html)


def test_scripts_search_serializes_public_url_and_preserves_path():
    """Expose the public listing URL in the script result serializer."""
    from scripts.client.parsers import SearchResultParser

    result = SearchResultParser().parse_search_response(SEARCH_HTML_FIXTURE)
    listing = result.to_dictionary()["listings"][0]

    assert listing["url"] == (
        "https://www.epifanioimoveis.com/imovel/4198561/"
        "apartamento-locacao-timoteo-mg-timirim"
    )
    assert listing["url_path"] == (
        "/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"
    )


def test_scripts_search_rejects_non_public_property_links():
    """Reject schemes, image/search destinations, and site roots."""
    import pytest

    from scripts.client.parsers import SearchResultParser

    invalid_links = (
        "javascript:alert(1)",
        "https://evil.example/imovel/4198561/apartamento",
        "https://www.epifanioimoveis.com/imagens/4198561.jpg",
        "https://www.epifanioimoveis.com/imovel/locacao/todos/timoteo",
        "https://www.epifanioimoveis.com/",
    )
    for invalid_link in invalid_links:
        invalid_html = SEARCH_HTML_FIXTURE.replace(
            'data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"',
            f'data-link="{invalid_link}"',
        ).replace('href="/imovel/4198561"', f'href="{invalid_link}"')
        with pytest.raises(ValueError, match="invalid public URL"):
            SearchResultParser().parse_search_response(invalid_html)


def test_search_cli_displays_public_property_url(capsys):
    """Show each public listing link in the existing search CLI."""
    from scripts.client.parsers import SearchResultParser
    from scripts.run_search import display_results

    result = SearchResultParser().parse_search_response(SEARCH_HTML_FIXTURE)
    display_results(result)

    assert "Link: https://www.epifanioimoveis.com/imovel/4198561/" in capsys.readouterr().out


def test_mcp_search_exposes_public_property_url():
    """Preserve the listing URL in the existing MCP search response."""
    from scripts.client.parsers import SearchResultParser
    from scripts.mcp.tools import EpifanioMcpAdapter

    result = SearchResultParser().parse_search_response(SEARCH_HTML_FIXTURE)

    class StubProvider:
        def search_rentals(self, search_filter):
            return result

    response = EpifanioMcpAdapter(StubProvider()).search_rentals()

    assert response["listings"][0]["url"] == (
        "https://www.epifanioimoveis.com/imovel/4198561/"
        "apartamento-locacao-timoteo-mg-timirim"
    )


def test_search_parser_normalizes_absolute_and_protocol_relative_links():
    """Keep identifying queries for absolute and protocol-relative card links."""
    path = "/imovel/4198561/apartamento-locacao-timoteo-mg-timirim?id=608"
    relative_path = path.split("?", maxsplit=1)[0]
    for source in (
        f"https://www.epifanioimoveis.com{path}",
        f"//www.epifanioimoveis.com{path}",
    ):
        html = SEARCH_HTML_FIXTURE.replace(
            f'data-link="{relative_path}"', f'data-link="{source}"'
        )
        listing = SearchPageParser().parse(html)[0]
        assert listing.identity.url_path == source
        expected_url = source
        if source.startswith("//"):
            expected_url = f"https://www.epifanioimoveis.com{path}"
        assert listing.url == expected_url


def test_search_parser_uses_real_anchor_fallback_and_rejects_missing_urls():
    """Use a real card anchor when its canonical data-link is absent."""
    import pytest

    from epifanio_research.domain.listing import InvalidPublicPropertyUrlError

    html = SEARCH_HTML_FIXTURE.replace(
        ' data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"', ""
    )
    listing = SearchPageParser().parse(html)[0]
    assert listing.identity.url_path == "/imovel/4198561"
    assert listing.url == "https://www.epifanioimoveis.com/imovel/4198561"
    unrecoverable = html.replace('href="/imovel/4198561"', "")
    with pytest.raises(InvalidPublicPropertyUrlError, match="recoverable"):
        SearchPageParser().parse(unrecoverable)


def test_search_collection_serializes_zero_and_multiple_results():
    """Retain collection type, counts, and pagination for empty and many results."""
    empty = SearchPageParser().parse("<html></html>", page_number=2).to_dictionary()
    second_card = (
        '<div class="imovelcard" data-link="/imovel/4198562/apartamento">'
        '<div class="imovelcard__info"><h2 class="imovelcard__info__local">Centro, Timóteo / MG</h2></div>'
        "</div>"
    )
    two_results_html = SEARCH_HTML_FIXTURE.replace("</body>", f"{second_card}</body>")
    multiple = SearchPageParser().parse(two_results_html, page_number=2).to_dictionary()

    assert empty == {"items": [], "current_page": 2, "has_next_page": False}
    assert len(multiple["items"]) == 2
    assert multiple["current_page"] == 2
    assert multiple["has_next_page"] is True


def test_scripts_search_preserves_absolute_and_protocol_relative_links():
    """Keep native paths and query parameters when resolving script results."""
    from scripts.client.parsers import SearchResultParser

    path = "/imovel/4198561/apartamento-locacao-timoteo-mg-timirim?id=608"
    source_path = path.split("?", maxsplit=1)[0]
    for source in (
        f"https://www.epifanioimoveis.com{path}",
        f"//www.epifanioimoveis.com{path}",
    ):
        html = SEARCH_HTML_FIXTURE.replace(
            f'data-link="{source_path}"', f'data-link="{source}"'
        )
        listing = SearchResultParser().parse_search_response(html).to_dictionary()["listings"][0]
        expected = source if source.startswith("https:") else f"https://www.epifanioimoveis.com{path}"
        assert listing["url_path"] == source
        assert listing["url"] == expected


def test_scripts_search_uses_anchor_fallback_and_rejects_missing_urls():
    """Use a real card anchor and reject a card with no recoverable URL."""
    import pytest

    from scripts.client.parsers import SearchResultParser
    from scripts.domain.exceptions import InvalidPublicPropertyUrlException

    html = SEARCH_HTML_FIXTURE.replace(
        ' data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"', ""
    )
    listing = SearchResultParser().parse_search_response(html).to_dictionary()["listings"][0]
    assert listing["url_path"] == "/imovel/4198561"
    assert listing["url"] == "https://www.epifanioimoveis.com/imovel/4198561"
    unrecoverable = html.replace('href="/imovel/4198561"', "")
    with pytest.raises(InvalidPublicPropertyUrlException, match="recoverable"):
        SearchResultParser().parse_search_response(unrecoverable)


def test_scripts_search_serializes_zero_and_multiple_results():
    """Preserve script result counts for empty and multi-property responses."""
    from scripts.client.parsers import SearchResultParser

    empty = SearchResultParser().parse_search_response("<html></html>").to_dictionary()
    second_card = (
        '<div class="imovelcard" data-link="/imovel/4198562/apartamento">'
        '<div class="imovelcard__info"><h2 class="imovelcard__info__local">Centro, Timóteo / MG</h2></div>'
        "</div>"
    )
    multi_html = SEARCH_HTML_FIXTURE.replace("</body>", f"{second_card}</body>")
    multiple = SearchResultParser().parse_search_response(multi_html).to_dictionary()

    assert empty["returned_count"] == 0
    assert len(multiple["listings"]) == 2
    assert multiple["returned_count"] == 2


def test_core_listing_serializer_rejects_missing_and_relative_public_urls():
    """Reject manually constructed listings that cannot serialize a public URL."""
    from dataclasses import replace

    import pytest

    from epifanio_research.domain.listing import InvalidPublicPropertyUrlError

    listing = SearchPageParser().parse(SEARCH_HTML_FIXTURE)[0]
    for url in ("", "/imovel/4198561"):
        with pytest.raises(InvalidPublicPropertyUrlError, match="4198561"):
            replace(listing, url=url).to_dictionary()


def test_adapter_listing_serializer_rejects_missing_and_relative_public_urls():
    """Reject manually constructed adapter listings with unusable public URLs."""
    from dataclasses import replace

    import pytest

    from scripts.client.parsers import SearchResultParser
    from scripts.domain.exceptions import InvalidPublicPropertyUrlException

    listing = SearchResultParser().parse_search_response(SEARCH_HTML_FIXTURE).listings().listings[0]
    for url in ("", "/imovel/4198561"):
        public_link = replace(listing.details.media.public_link, url=url)
        media = replace(listing.details.media, public_link=public_link)
        details = replace(listing.details, media=media)
        invalid_listing = replace(listing, details=details)
        with pytest.raises(InvalidPublicPropertyUrlException, match="4198561"):
            invalid_listing.to_dictionary()


def test_malformed_card_links_raise_the_local_public_url_exception():
    """Wrap malformed canonical links and detail anchors with URL context."""
    import pytest

    from epifanio_research.domain.listing import InvalidPublicPropertyUrlError

    malformed_link = "https://[broken/imovel/4198561"
    canonical_html = SEARCH_HTML_FIXTURE.replace(
        'data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"',
        f'data-link="{malformed_link}"',
    )
    anchor_html = SEARCH_HTML_FIXTURE.replace(
        ' data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"', ""
    ).replace('href="/imovel/4198561"', f'href="{malformed_link}"')

    for invalid_html in (canonical_html, anchor_html):
        with pytest.raises(InvalidPublicPropertyUrlError, match="malformed public URL") as error:
            SearchPageParser().parse(invalid_html)
        assert malformed_link in str(error.value)


def test_adapter_malformed_card_links_raise_the_local_exception():
    """Wrap malformed adapter links and detail anchors with URL context."""
    import pytest

    from scripts.client.parsers import SearchResultParser
    from scripts.domain.exceptions import InvalidPublicPropertyUrlException

    malformed_link = "https://[broken/imovel/4198561"
    canonical_html = SEARCH_HTML_FIXTURE.replace(
        'data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"',
        f'data-link="{malformed_link}"',
    )
    anchor_html = SEARCH_HTML_FIXTURE.replace(
        ' data-link="/imovel/4198561/apartamento-locacao-timoteo-mg-timirim"', ""
    ).replace('href="/imovel/4198561"', f'href="{malformed_link}"')

    for invalid_html in (canonical_html, anchor_html):
        with pytest.raises(InvalidPublicPropertyUrlException, match="malformed public URL") as error:
            SearchResultParser().parse_search_response(invalid_html)
        assert malformed_link in str(error.value)
