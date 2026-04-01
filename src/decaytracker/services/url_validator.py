"""URL validation + SSRF protection."""
import ipaddress
import socket
from urllib.parse import urlparse

from loguru import logger


class URLValidationError(ValueError):
    """Raised when URL fails validation or SSRF check."""
    pass


# Private/internal IP ranges to block
_PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

_BLOCKED_HOSTNAMES = {"localhost", "0.0.0.0"}

_MAX_URL_LENGTH = 2000


def _is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is in a private/internal range."""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(addr in network for network in _PRIVATE_NETWORKS)


def validate_url(url: str) -> str:
    """Validate URL and block SSRF attempts. Returns cleaned URL.

    Raises URLValidationError on invalid or dangerous URLs.
    """
    if not url or not isinstance(url, str):
        raise URLValidationError("URL is required")

    url = url.strip()

    # Length check
    if len(url) > _MAX_URL_LENGTH:
        raise URLValidationError("URL exceeds maximum length of 2000 characters")

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        raise URLValidationError("Malformed URL")

    # Scheme check — only http and https
    if parsed.scheme not in ("http", "https"):
        raise URLValidationError("Only http and https URLs are allowed")

    # Must have a hostname
    hostname = parsed.hostname
    if not hostname:
        raise URLValidationError("URL must contain a valid hostname")

    hostname_lower = hostname.lower()

    # Block known dangerous hostnames
    if hostname_lower in _BLOCKED_HOSTNAMES:
        raise URLValidationError("URL hostname is not allowed")

    # Must have a valid domain (not bare IP) — require at least one dot
    # This blocks http://192.168.1.1 style URLs
    try:
        ipaddress.ip_address(hostname_lower)
        raise URLValidationError("IP addresses are not allowed; use a domain name")
    except ValueError:
        pass  # Not an IP literal — good

    if "." not in hostname_lower:
        raise URLValidationError("URL must contain a valid domain name")

    # DNS resolution — check if domain resolves to a private IP (SSRF protection)
    # If DNS fails (unknown domain), we allow it through — the audit agent will
    # handle the failure downstream. We only block domains that actively resolve
    # to private/internal IPs.
    try:
        resolved = socket.getaddrinfo(hostname_lower, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, type_, proto, canonname, sockaddr in resolved:
            ip_str = sockaddr[0]
            if _is_private_ip(ip_str):
                logger.warning("SSRF blocked: {} resolves to private IP {}", hostname_lower, ip_str)
                raise URLValidationError("URL resolves to a private network address")
    except socket.gaierror:
        # Domain doesn't resolve — not an SSRF risk, let the audit agent handle it
        logger.debug("DNS resolution failed for {}, allowing through", hostname_lower)
    except URLValidationError:
        raise
    except Exception:
        # Non-critical DNS failure — allow through
        logger.debug("DNS check failed for {}, allowing through", hostname_lower)

    return url
