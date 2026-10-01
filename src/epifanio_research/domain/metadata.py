"""Domain models for location catalog metadata (cities and neighborhoods)."""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class Neighborhood:
    """Represents a neighborhood entity with display name, slug, and numeric ID."""

    name: str
    slug: str
    numeric_id: str


@dataclass(frozen=True)
class NeighborhoodGroup:
    """First-class collection representing neighborhoods belonging to a city."""

    items: tuple[Neighborhood, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        """Return count of neighborhoods."""
        return len(self.items)

    def __iter__(self) -> Iterator[Neighborhood]:
        """Iterate over neighborhoods."""
        return iter(self.items)

    def find_by_name(self, name: str) -> Neighborhood | None:
        """Lookup neighborhood by exact name match."""
        for item in self.items:
            if item.name.lower() == name.lower():
                return item
        return None


@dataclass(frozen=True)
class City:
    """Represents a municipality with name, slug, and associated neighborhoods."""

    name: str
    slug: str
    neighborhoods: NeighborhoodGroup = field(default_factory=NeighborhoodGroup)


@dataclass(frozen=True)
class LocationCatalog:
    """First-class collection wrapping all available cities in the portal."""

    cities: tuple[City, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        """Return count of cities."""
        return len(self.cities)

    def __iter__(self) -> Iterator[City]:
        """Iterate over cities in catalog."""
        return iter(self.cities)

    def find_city_by_slug(self, slug: str) -> City | None:
        """Locate city by its URL slug identifier."""
        for city in self.cities:
            if city.slug == slug:
                return city
        return None
