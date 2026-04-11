from __future__ import annotations

import json
import secrets
import string
from dataclasses import dataclass, asdict

from .crypto import hash_password


def _rand_alnum(n: int) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if not local or not domain:
        raise ValueError("invalid email")
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + ("*" * (len(local) - 2)) + local[-1]
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    digits = [c for c in phone if c.isdigit()]
    if len(digits) < 7:
        raise ValueError("invalid phone")
    # Keep last 2 digits, mask the rest.
    masked = "*" * (len(digits) - 2) + "".join(digits[-2:])
    return masked


@dataclass(frozen=True)
class DummySensitiveDemo:
    full_name: str
    email_masked: str
    phone_masked: str
    password_hash: str
    note_preview: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2) + "\n"


def generate_dummy_sensitive_demo() -> DummySensitiveDemo:
    # Use reserved domains / numbers so it can't be real.
    # RFC 2606 reserved: example.com
    local = f"user.{_rand_alnum(10)}"
    email = f"{local}@example.com"

    # NANP 555-01xx is reserved for fictional use.
    last2 = secrets.randbelow(100)
    phone = f"+1-202-555-01{last2:02d}"

    # Generate a password but do not return it.
    password = secrets.token_urlsafe(18)
    pw_hash = hash_password(password)

    note_preview = (
        "Demo note (masked): "
        f"name=Sample User, email={mask_email(email)}, phone={mask_phone(phone)}"
    )

    return DummySensitiveDemo(
        full_name="Sample User",
        email_masked=mask_email(email),
        phone_masked=mask_phone(phone),
        password_hash=pw_hash,
        note_preview=note_preview,
    )
