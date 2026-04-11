import json

from secure_app.demo import generate_dummy_sensitive_demo


def test_demo_generates_masked_example() -> None:
    demo = generate_dummy_sensitive_demo()

    # Reserved domain
    assert demo.email_masked.endswith("@example.com")

    # Masked output should contain '*' to avoid printing full identifiers
    assert "*" in demo.email_masked
    assert "*" in demo.phone_masked

    # Password must not be shown, only a strong hash format.
    assert demo.password_hash.startswith("pbkdf2_sha256$")

    # Output is valid JSON
    parsed = json.loads(demo.to_json())
    assert parsed["email_masked"].endswith("@example.com")
    assert parsed["password_hash"].startswith("pbkdf2_sha256$")
