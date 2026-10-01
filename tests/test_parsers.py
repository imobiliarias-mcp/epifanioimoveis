"""Unit tests for HTML, JSON-LD, and AJAX photo parsers."""

from epifanio_research.parsers.detail_parser import PropertyDetailParser
from epifanio_research.parsers.feature_extractor import CardFeatureExtractor
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
