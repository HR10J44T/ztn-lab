from app.services.policy_engine import evaluate_access


def test_developer_denied_admin_zone():
    decision = evaluate_access("developer", "/zones/admin", "read", "managed", "corporate")
    assert decision.decision == "deny"


def test_admin_allowed_admin_zone_from_trusted_device():
    decision = evaluate_access("admin", "/zones/admin", "read", "trusted", "corporate")
    assert decision.decision == "allow"


def test_compromised_device_always_denied():
    decision = evaluate_access("admin", "/zones/engineering", "read", "compromised", "corporate")
    assert decision.decision == "deny"
