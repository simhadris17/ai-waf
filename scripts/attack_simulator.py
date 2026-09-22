"""
Fires a mix of normal and malicious-looking requests at the running backend
so you can watch the dashboard's live feed and stats update in real time.

Usage:
    python scripts/attack_simulator.py
    python scripts/attack_simulator.py --url http://localhost:8000 --count 40
"""
import argparse
import random
import time

import requests

SAFE_PAYLOADS = [
    "/search?q=running+shoes",
    "/login?user=alex",
    "/profile?view=summary",
    "/cart?action=checkout",
    "/products?category=electronics",
]

ATTACK_PAYLOADS = [
    "/search?q=' UNION SELECT username,password FROM users--",
    "/comment?text=<script>alert(document.cookie)</script>",
    "/file?path=../../../../etc/passwd",
    "/login?user=admin'--",
    "/exec?cmd=cat /etc/shadow",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument("--delay", type=float, default=0.6)
    args = parser.parse_args()

    for i in range(args.count):
        is_attack = random.random() < 0.35
        path = random.choice(ATTACK_PAYLOADS if is_attack else SAFE_PAYLOADS)

        try:
            resp = requests.get(f"{args.url}{path}", timeout=5)
            tag = "ATTACK-BLOCKED" if resp.status_code == 403 else "ALLOWED"
            print(f"[{i+1:03d}] {resp.status_code} {tag:15s} {path}")
        except requests.RequestException as e:
            print(f"[{i+1:03d}] ERROR contacting backend: {e}")

        time.sleep(args.delay)


if __name__ == "__main__":
    main()
