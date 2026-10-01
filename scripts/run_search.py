import argparse
import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import ListingPrice
from scripts.providers.epifanio import EpifanioRentalProvider


def build_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(description="Search rental properties on Epifânio Imóveis.")
    parser.add_argument("--city", type=str, default="", help="City name (e.g. Timóteo, Ipatinga)")
    parser.add_argument("--neighborhood", type=str, default="", help="Neighborhood name")
    parser.add_argument("--bedrooms", type=int, default=0, help="Minimum number of bedrooms")
    parser.add_argument("--max-price", type=float, default=0.0, help="Maximum rental price in BRL")
    parser.add_argument("--page", type=int, default=1, help="Page index (1-based)")
    return parser


def create_search_filter(arguments: argparse.Namespace) -> RentalFilter:
    """Translate command line arguments to domain RentalFilter."""
    working_filter = RentalFilter()
    working_filter = working_filter.with_page(arguments.page)
    if arguments.city:
        working_filter = working_filter.with_city(arguments.city)
    if arguments.bedrooms > 0:
        working_filter = working_filter.with_bedrooms(arguments.bedrooms)
    if arguments.max_price > 0.0:
        ceiling = ListingPrice(arguments.max_price)
        working_filter = working_filter.with_price_ceiling(ceiling)
    return working_filter


def display_results(result) -> None:
    """Print search summary and items to console."""
    total = result.total_count()
    returned = result.returned_count()
    print(f"\nResultados: {returned} exibidos de {total} encontrados na Epifânio Imóveis\n")
    print("-" * 75)
    for listing in result.listings():
        summary_line = listing.format_summary()
        print(summary_line)
    print("-" * 75)


def main() -> None:
    """Main execution function."""
    argument_parser = build_argument_parser()
    parsed_arguments = argument_parser.parse_args()
    search_filter = create_search_filter(parsed_arguments)
    provider = EpifanioRentalProvider.create_default()
    search_result = provider.search_rentals(search_filter)
    display_results(search_result)


if __name__ == "__main__":
    main()
