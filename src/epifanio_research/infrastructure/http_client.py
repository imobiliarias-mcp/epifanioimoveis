"""HTTP client abstraction and Httpx implementation."""

from dataclasses import dataclass
from typing import Protocol

import httpx


class PortalConnectionError(Exception):
    """Raised when portal network communication fails."""


class PropertyNotFoundError(Exception):
    """Raised when a requested property cannot be found or redirects home."""


@dataclass(frozen=True)
class HttpResponse:
    """Encapsulates response data from HTTP operations."""

    status_code: int
    text: str
    final_url: str


class HttpClientProtocol(Protocol):
    """Contract for HTTP network operations."""

    def get(self, url: str) -> HttpResponse:
        """Perform HTTP GET request."""
        ...


class HttpxHttpClient:
    """Concrete HTTP client using httpx with desktop User-Agent."""

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout_seconds: float = 20.0) -> None:
        """Initialize HTTP client with timeout."""
        self._timeout = timeout_seconds
        self._headers = {"User-Agent": self.DEFAULT_USER_AGENT}

    def get(self, url: str) -> HttpResponse:
        """Execute GET request with redirect following."""
        try:
            return self._execute_request(url)
        except httpx.HTTPError as error:
            raise PortalConnectionError(f"HTTP request failed for {url}: {error}") from error

    def _execute_request(self, url: str) -> HttpResponse:
        """Internal helper to dispatch request via httpx."""
        with httpx.Client(headers=self._headers, timeout=self._timeout, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return HttpResponse(
                status_code=resp.status_code,
                text=resp.text,
                final_url=str(resp.url),
            )
