import json

from secure_app.demo import generate_dummy_sensitive_demo


def test_demo_generates_masked_example() -> None:
    demo = generate_dummy_sensitive_demo()

    assert demo.email_masked.endswith("@example.com")

    assert "*" in demo.email_masked
    assert "*" in demo.phone_masked

    assert demo.password_hash.startswith("pbkdf2_sha256$")

    parsed = json.loads(demo.to_json())
    assert parsed["email_masked"].endswith("@example.com")
    assert parsed["password_hash"].startswith("pbkdf2_sha256$")
