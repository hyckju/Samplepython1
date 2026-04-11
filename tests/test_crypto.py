from secure_app.crypto import hash_password, verify_password


def test_hash_and_verify_roundtrip() -> None:
    encoded = hash_password("correct horse battery staple")
    assert encoded.startswith("pbkdf2_sha256$")
    assert verify_password("correct horse battery staple", encoded) is True
    assert verify_password("wrong-password", encoded) is False


def test_verify_rejects_malformed() -> None:
    assert verify_password("pw", "not-a-real-hash") is False
    assert verify_password("pw", "pbkdf2_sha256$abc$def$ghi") is False
