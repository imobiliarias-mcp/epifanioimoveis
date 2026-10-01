"""Parsers package exports."""

from epifanio_research.parsers.detail_parser import PropertyDetailParser
from epifanio_research.parsers.feature_extractor import CardFeatureExtractor
from epifanio_research.parsers.photo_parser import PhotoGalleryParser
from epifanio_research.parsers.search_parser import SearchPageParser

__all__ = [
    "CardFeatureExtractor",
    "PhotoGalleryParser",
    "PropertyDetailParser",
    "SearchPageParser",
]
