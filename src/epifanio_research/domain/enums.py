"""Domain enumerations for real estate transactions, property types, and ordering."""

from enum import Enum


class TransactionType(str, Enum):
    """Transaction purpose: rental or sale."""

    LOCACAO = "locacao"
    VENDA = "venda"


class SortOrder(str, Enum):
    """Sorting order for property search listings."""

    DEFAULT = ""
    MENOR_VALOR = "menor_valor"
    MAIOR_VALOR = "maior_valor"
    RECENTES = "recentes"


class PropertyType(str, Enum):
    """Known property categories on the platform."""

    TODOS = "todos"
    APARTAMENTO = "apartamento"
    CASA = "casa"
    LOTE = "lote"
    SALA_COMERCIAL = "sala-comercial"
    SITIO_CHACARA = "sitio-chacara"
    TERRENO = "terreno"
    COBERTURA = "cobertura"
    CHACARA = "chacara"
    PONTO_COMERCIAL = "ponto-comercial"
    DUPLEX = "duplex"
    CASA_GEMINADA = "casa-geminada"
    IMOVEL_COMERCIAL = "imovel-comercial"
    RESIDENCIAL_E_COMERCIAL = "residencial-e-comercial"
    SALAO_DE_FESTA = "salao-de-festa"
    APARTAMENTO_TERREO = "apartamento-terreo"
    LOJA_COMERCIAL = "loja-comercial"
