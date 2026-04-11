from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

_PBKDF2_DIGEST = "sha256"
_DEFAULT_ITERATIONS = 200_000
_SALT_BYTES = 16
_DKLEN = 32


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64d(data: str) -> bytes:
    if not isinstance(data, str):
        raise TypeError("b64 input must be str")
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("ascii"))


def hash_password(password: str, *, iterations: int = _DEFAULT_ITERATIONS) -> str:
    if not isinstance(password, str):
        raise TypeError("password must be a str")
    if len(password) < 8:
        raise ValueError("password too short (min 8)")
    if iterations < 100_000:
        raise ValueError("iterations too low")

    salt = secrets.token_bytes(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(
        _PBKDF2_DIGEST,
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=_DKLEN,
    )

    return f"pbkdf2_{_PBKDF2_DIGEST}${iterations}${_b64e(salt)}${_b64e(dk)}"


def verify_password(password: str, encoded: str) -> bool:
    if not isinstance(password, str):
        raise TypeError("password must be a str")
    if not isinstance(encoded, str):
        raise TypeError("encoded must be a str")

    try:
        scheme, iter_s, salt_s, hash_s = encoded.split("$", 3)
        if scheme != f"pbkdf2_{_PBKDF2_DIGEST}":
            return False
        iterations = int(iter_s)
        if iterations < 100_000:
            return False
        salt = _b64d(salt_s)
        expected = _b64d(hash_s)
    except Exception:
        return False

    derived = hashlib.pbkdf2_hmac(
        _PBKDF2_DIGEST,
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=len(expected),
    )

    return hmac.compare_digest(derived, expected)
