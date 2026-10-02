"""Configuration settings for Epifânio Imóveis API client."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EpifanioConfiguration:
    """Holds configuration parameters for portal communication."""

    base_hostname: str = "www.epifanioimoveis.com"
    base_url: str = "https://www.epifanioimoveis.com"

    def origin_header_value(self) -> str:
        """Return canonical portal origin."""
        return f"https://{self.base_hostname}"

    def referer_header_value(self) -> str:
        """Return canonical portal referer."""
        return f"https://{self.base_hostname}/"

    def public_site_base_url(self) -> str:
        """Return the configured public listing-site origin."""
        return f"https://{self.base_hostname}"
