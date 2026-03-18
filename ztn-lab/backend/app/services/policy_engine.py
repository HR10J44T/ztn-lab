from dataclasses import dataclass
from app.services.risk_engine import calculate_risk

SEGMENT_MAP = {
    "/zones/admin": "admin",
    "/zones/engineering": "engineering",
    "/zones/finance": "finance",
    "/zones/db": "db",
}

ALLOWED_SEGMENTS = {
    "admin": {"admin", "engineering", "finance", "db"},
    "developer": {"engineering"},
    "analyst": {"engineering", "finance"},
    "guest": set(),
}


@dataclass
class PolicyDecision:
    decision: str
    resource_segment: str
    risk_score: int
    reason: str
    policy: str
    explanation: str


def extract_segment(resource: str) -> str:
    return SEGMENT_MAP.get(resource, "public")


def evaluate_access(role: str, resource: str, action: str, device_trust: str, location: str) -> PolicyDecision:
    segment = extract_segment(resource)
    risk_score, risk_reasons = calculate_risk(role, device_trust, location, segment, action)
    allowed_segments = ALLOWED_SEGMENTS.get(role, set())

    if segment not in allowed_segments and segment != "public":
        reason = f"Role not allowed for segment {segment}"
        return PolicyDecision(
            decision="deny",
            resource_segment=segment,
            risk_score=risk_score,
            reason=reason,
            policy=f"deny_{role}_{segment}",
            explanation=f"Access denied because {role} is not authorized for {segment}. Continuous verification risk={risk_score}.",
        )

    if device_trust == "compromised":
        return PolicyDecision(
            decision="deny",
            resource_segment=segment,
            risk_score=max(risk_score, 90),
            reason="Compromised device blocked",
            policy="block_compromised_device",
            explanation="Access denied because device posture is compromised.",
        )

    if segment in {"admin", "db"} and device_trust not in {"trusted", "managed"}:
        return PolicyDecision(
            decision="deny",
            resource_segment=segment,
            risk_score=max(risk_score, 75),
            reason="Sensitive segment requires trusted or managed device",
            policy="sensitive_segment_device_posture",
            explanation="Access denied because sensitive segments need stronger device trust.",
        )

    if risk_score >= 70:
        return PolicyDecision(
            decision="deny",
            resource_segment=segment,
            risk_score=risk_score,
            reason="Risk score exceeded threshold",
            policy="risk_threshold_guardrail",
            explanation=f"Access denied due to elevated contextual risk: {', '.join(risk_reasons) or 'multiple risk signals'}.",
        )

    return PolicyDecision(
        decision="allow",
        resource_segment=segment,
        risk_score=risk_score,
        reason="Access granted after identity and context verification",
        policy="allow_contextual_access",
        explanation=f"Access allowed. Verified role={role}, segment={segment}, contextual risk={risk_score}.",
    )
