from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import SplitResult, urlsplit


@dataclass(frozen=True)
class OutboundUrlPolicy:
    allowed_hosts: frozenset[str]
    allowed_schemes: frozenset[str] = frozenset({"https"})


def validate_outbound_url(url: str, policy: OutboundUrlPolicy) -> SplitResult:
    if not isinstance(url, str):
        raise TypeError("url must be a str")

    parsed = urlsplit(url)

    if parsed.scheme not in policy.allowed_schemes:
        raise ValueError("scheme not allowed")
    if not parsed.netloc:
        raise ValueError("missing host")
    if parsed.username or parsed.password:
        raise ValueError("userinfo not allowed")

    host = parsed.hostname
    if not host:
        raise ValueError("missing host")

    host_lc = host.lower().rstrip(".")

    # Disallow localhost and other obvious local names unless explicitly allowlisted.
    if host_lc in {"localhost", "localhost.localdomain"} and host_lc not in policy.allowed_hosts:
        raise ValueError("localhost not allowed")

    # If host is an IP literal, block private/link-local/etc unless explicitly allowlisted.
    try:
        ip = ipaddress.ip_address(host_lc)
    except ValueError:
        ip = None

    if ip is not None:
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise ValueError("private or special IP not allowed")
        if host_lc not in policy.allowed_hosts:
            raise ValueError("IP host must be explicitly allowlisted")
    else:
        # Without DNS resolution (which itself can be dangerous), enforce allowlist strictly.
        if host_lc not in policy.allowed_hosts:
            raise ValueError("host not in allowlist")

    return parsed
