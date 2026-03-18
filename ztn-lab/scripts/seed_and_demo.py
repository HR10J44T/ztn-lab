import itertools
import time
import requests

BASE_URL = "http://localhost:8000"
USERS = [
    ("admin_user", "Admin@123"),
    ("dev_user", "Dev@123"),
    ("analyst_user", "Analyst@123"),
    ("guest_user", "Guest@123"),
]
REQUESTS = [
    {"resource": "/zones/admin", "action": "read", "device_trust": "trusted", "location": "corporate", "ip_address": "10.0.0.10"},
    {"resource": "/zones/admin", "action": "read", "device_trust": "unknown", "location": "remote", "ip_address": "203.0.113.20"},
    {"resource": "/zones/db", "action": "write", "device_trust": "managed", "location": "corporate", "ip_address": "10.1.0.15"},
    {"resource": "/zones/engineering", "action": "read", "device_trust": "managed", "location": "remote", "ip_address": "198.51.100.8"},
    {"resource": "/zones/finance", "action": "read", "device_trust": "compromised", "location": "foreign", "ip_address": "203.0.113.99"},
]


def login(username: str, password: str) -> str:
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password}, timeout=10)
    response.raise_for_status()
    return response.json()["access_token"]


def main():
    for (username, password), payload in itertools.product(USERS, REQUESTS):
        token = login(username, password)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/access/evaluate", json=payload, headers=headers, timeout=10)
        print(username, payload["resource"], response.json())
        time.sleep(0.2)


if __name__ == "__main__":
    main()
