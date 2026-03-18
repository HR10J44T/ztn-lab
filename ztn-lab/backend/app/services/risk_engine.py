def calculate_risk(role: str, device_trust: str, location: str, resource_segment: str, action: str) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    device_risk = {
        "trusted": 5,
        "managed": 15,
        "unknown": 35,
        "compromised": 60,
    }
    location_risk = {
        "corporate": 5,
        "remote": 15,
        "foreign": 30,
    }
    segment_risk = {
        "engineering": 10,
        "finance": 20,
        "admin": 30,
        "db": 35,
        "public": 0,
    }

    score += device_risk.get(device_trust, 30)
    score += location_risk.get(location, 20)
    score += segment_risk.get(resource_segment, 10)

    if action.lower() in {"write", "delete", "admin"}:
        score += 10
        reasons.append("privileged action requested")

    if device_trust in {"unknown", "compromised"}:
        reasons.append(f"device is {device_trust}")
    if location in {"remote", "foreign"}:
        reasons.append(f"access from {location} location")
    if resource_segment in {"admin", "db", "finance"}:
        reasons.append(f"sensitive resource segment: {resource_segment}")
    if role == "guest":
        score += 10
        reasons.append("guest role carries higher baseline risk")

    return min(score, 100), reasons
