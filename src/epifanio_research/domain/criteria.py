"""Search criteria and specification models adhering to Object Calisthenics."""

from dataclasses import dataclass, field
from epifanio_research.domain.enums import PropertyType, SortOrder, TransactionType
from epifanio_research.domain.values import AreaRange, PageNumber, PriceRange, RoomCount


@dataclass(frozen=True)
class LocationCriteria:
    """Location parameters: city slug and optional neighborhood identifiers."""

    city_slug: str = "todos"
    neighborhood_ids: tuple[str, ...] = field(default_factory=tuple)

    def query_parameters(self) -> dict[str, str]:
        """Convert neighborhood list to query parameter."""
        if not self.neighborhood_ids:
            return {}
        return {"bairros": ",".join(self.neighborhood_ids)}


@dataclass(frozen=True)
class RoomCriteria:
    """Bedroom and suite quantity criteria."""

    bedrooms: RoomCount | None = None
    suites: RoomCount | None = None

    def query_parameters(self) -> dict[str, str]:
        """Convert room counts into request parameters."""
        params: dict[str, str] = {}
        if self.bedrooms is not None:
            params["dormitorios"] = self.bedrooms.to_param_code()
        if self.suites is not None:
            params["suites"] = self.suites.to_param_code()
        return params


@dataclass(frozen=True)
class FacilityCriteria:
    """Bathroom and parking space criteria."""

    bathrooms: RoomCount | None = None
    parking_spaces: RoomCount | None = None

    def query_parameters(self) -> dict[str, str]:
        """Convert facility counts into request parameters."""
        params: dict[str, str] = {}
        if self.bathrooms is not None:
            params["banheiros"] = self.bathrooms.to_param_code()
        if self.parking_spaces is not None:
            params["vagas"] = self.parking_spaces.to_param_code()
        return params


@dataclass(frozen=True)
class SearchScope:
    """Defines transaction type and property category."""

    transaction: TransactionType = TransactionType.LOCACAO
    property_type: PropertyType = PropertyType.TODOS


@dataclass(frozen=True)
class FilterBundle:
    """Aggregates price range and area range constraints."""

    price_range: PriceRange = field(default_factory=PriceRange)
    area_range: AreaRange = field(default_factory=AreaRange)

    def query_parameters(self) -> dict[str, str]:
        """Combine query parameters for price and area."""
        params = self.price_range.query_parameters()
        params.update(self.area_range.query_parameters())
        return params


@dataclass(frozen=True)
class FeatureBundle:
    """Aggregates room and facility constraint criteria."""

    room_criteria: RoomCriteria = field(default_factory=RoomCriteria)
    facility_criteria: FacilityCriteria = field(default_factory=FacilityCriteria)

    def query_parameters(self) -> dict[str, str]:
        """Combine room and facility criteria parameters."""
        params = self.room_criteria.query_parameters()
        params.update(self.facility_criteria.query_parameters())
        return params


@dataclass(frozen=True)
class SearchCriteria:
    """Top-level search criteria container pairing scope with composite criteria."""

    scope: SearchScope = field(default_factory=SearchScope)
    location: LocationCriteria = field(default_factory=LocationCriteria)
    filters: FilterBundle = field(default_factory=FilterBundle)
    features: FeatureBundle = field(default_factory=FeatureBundle)
    sort_order: SortOrder = SortOrder.DEFAULT
    page: PageNumber = field(default_factory=PageNumber)
    reference_code: str | None = None

    @classmethod
    def create_rental(
        cls,
        city: str = "timoteo",
        property_type: PropertyType = PropertyType.TODOS,
        bedrooms: int | None = None,
        min_bedrooms: bool = False,
        max_price: int | None = None,
        page: int = 1,
    ) -> "SearchCriteria":
        """Factory helper to construct rental search criteria quickly."""
        room_count = None
        if bedrooms:
            room_count = RoomCount(bedrooms, min_bedrooms)
        return cls(
            scope=SearchScope(TransactionType.LOCACAO, property_type),
            location=LocationCriteria(city_slug=city),
            filters=FilterBundle(price_range=PriceRange(maximum=max_price)),
            features=FeatureBundle(room_criteria=RoomCriteria(bedrooms=room_count)),
            page=PageNumber(value=page),
        )
