"""Domain entities and first-class collection for property search listings."""

from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from urllib.parse import urlsplit


class InvalidPublicPropertyUrlError(ValueError):
    """Raised when a listing lacks a valid public property URL."""


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
    url: str = ""

    def to_dictionary(self) -> dict:
        """Serialize listing values and its original relative path."""
        property_id = self.identity.property_id
        if not _is_public_property_url(self.url, property_id):
            raise InvalidPublicPropertyUrlError(
                f"Property '{property_id}' has invalid public URL '{self.url}'."
            )
        listing_data = asdict(self)
        listing_data["url_path"] = self.identity.url_path
        return listing_data


def _is_public_property_url(url: str, property_id: str) -> bool:
    """Check that the serialized URL is absolute and identifies this property."""
    if not url or url != url.strip():
        return False
    try:
        parsed_url = urlsplit(url)
        port = parsed_url.port
    except ValueError:
        return False
    path_segments = [segment for segment in parsed_url.path.split("/") if segment]
    return (
        parsed_url.scheme in {"http", "https"}
        and bool(parsed_url.hostname)
        and (port is None or 0 <= port <= 65535)
        and len(path_segments) > 1
        and path_segments[0] == "imovel"
        and path_segments[1] == property_id
    )


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

    def to_dictionary(self) -> dict:
        """Serialize listing items while preserving pagination metadata."""
        serialized_items = [item.to_dictionary() for item in self.items]
        return {
            "items": serialized_items,
            "current_page": self.current_page,
            "has_next_page": self.has_next_page,
        }
