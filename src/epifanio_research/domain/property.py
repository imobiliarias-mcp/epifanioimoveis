"""Domain models for full property details and photo gallery collection."""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class PhotoGallery:
    """First-class collection representing a property's photo image URLs."""

    photo_urls: tuple[str, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        """Return total number of photos in gallery."""
        return len(self.photo_urls)

    def __iter__(self) -> Iterator[str]:
        """Iterate over photo URLs."""
        return iter(self.photo_urls)

    def __getitem__(self, index: int) -> str:
        """Get photo URL by index."""
        return self.photo_urls[index]

    def first_photo(self) -> str | None:
        """Return the primary photo URL if available."""
        if not self.photo_urls:
            return None
        return self.photo_urls[0]


@dataclass(frozen=True)
class PropertyLocation:
    """Detailed geographic location of a property."""

    address: str
    neighborhood: str
    city: str
    state: str = "MG"


@dataclass(frozen=True)
class PropertyPricing:
    """Price and currency details."""

    amount: float | None
    currency: str = "BRL"
    formatted_text: str = ""


@dataclass(frozen=True)
class PropertySpecs:
    """Room counts and dimensions for property details."""

    bedrooms: int | None = None
    suites: int | None = None
    bathrooms: int | None = None
    parking_spaces: int | None = None


@dataclass(frozen=True)
class PropertyOverview:
    """Identity and textual description of the property."""

    property_id: str
    title: str
    reference_code: str = ""
    description: str = ""


@dataclass(frozen=True)
class PropertyDetail:
    """Complete detail view of a real estate property."""

    overview: PropertyOverview
    pricing: PropertyPricing
    location: PropertyLocation
    specs: PropertySpecs
    characteristics: tuple[str, ...] = field(default_factory=tuple)
    photos: PhotoGallery = field(default_factory=PhotoGallery)
    canonical_url: str = ""
