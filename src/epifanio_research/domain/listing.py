"""Domain entities and first-class collection for property search listings."""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class ListingIdentity:
    """Identification and canonical link for a property."""

    property_id: str
    url_path: str


@dataclass(frozen=True)
class ListingLocation:
    """Geographic information parsed from a listing."""

    neighborhood: str
    city: str
    state: str = "MG"


@dataclass(frozen=True)
class ListingSpecs:
    """Property specifications parsed from search card."""

    bedrooms: int | None = None
    suites: int | None = None
    bathrooms: int | None = None
    parking_spaces: int | None = None
    area_text: str | None = None


@dataclass(frozen=True)
class ListingSummary:
    """Summary of a property listing card returned from search."""

    identity: ListingIdentity
    title: str
    location: ListingLocation
    price_text: str
    specs: ListingSpecs
    reference_code: str | None = None
    thumbnail_url: str | None = None


@dataclass(frozen=True)
class ListingCollection:
    """First-class collection wrapping search results and pagination status."""

    items: tuple[ListingSummary, ...] = field(default_factory=tuple)
    current_page: int = 1
    has_next_page: bool = False

    def __len__(self) -> int:
        """Return the number of listings in this page."""
        return len(self.items)

    def __iter__(self) -> Iterator[ListingSummary]:
        """Iterate over the listing items."""
        return iter(self.items)

    def __getitem__(self, index: int) -> ListingSummary:
        """Access a listing by index."""
        return self.items[index]

    def is_empty(self) -> bool:
        """Check if collection contains no items."""
        return len(self.items) == 0
