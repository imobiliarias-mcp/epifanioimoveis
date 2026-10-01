import argparse
import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.exceptions import RentalSearchException
from scripts.domain.value_objects import PropertyCode
from scripts.providers.epifanio import EpifanioRentalProvider


def parse_arguments() -> argparse.Namespace:
    """Parse property code from CLI arguments."""
    parser = argparse.ArgumentParser(description="View full rental property details by code.")
    parser.add_argument("code", type=str, help="Property listing code (e.g. 4198561)")
    return parser.parse_args()


def main() -> None:
    """Main execution function."""
    arguments = parse_arguments()
    code_value_object = PropertyCode(arguments.code)
    provider = EpifanioRentalProvider.create_default()
    try:
        property_detail = provider.get_property_detail(code_value_object)
    except RentalSearchException as error:
        print(f"Erro ao buscar imóvel: {error}", file=sys.stderr)
        sys.exit(1)
    formatted_view = property_detail.format_detailed_view()
    print("\n" + "=" * 70)
    print(formatted_view)
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
