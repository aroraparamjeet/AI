"""
fake_api.py  -  A tiny "real" API you can start and stop to test LocalMockr fallback mode.

HOW TO USE
----------
1. Start LocalMockr normally:        python localmockr.py
2. Start this fake API:              python fake_api.py
3. In LocalMockr dashboard, create a rule:
     Path:         /api/users
     Method:       GET
     Mode:         Network + Fallback
     External URL: http://localhost:9000
     Response Body: (paste your fallback JSON here)
4. Hit the rule via the proxy:       http://localhost:3847/api/users   -> gets LIVE data
5. Stop this script (Ctrl+C)
6. Hit the rule again:               http://localhost:3847/api/users   -> gets FALLBACK (local JSON)

ENDPOINTS
---------
GET  /api/users          - list of users
GET  /api/users/{id}     - single user
GET  /api/products        - list of products
GET  /api/products/{id}  - single product
GET  /api/orders          - list of orders
GET  /api/stats           - site statistics
GET  /health              - health check
POST /api/users           - echo back posted body (with a fake created id)

Run on port 9000 by default. Change PORT below if needed.
"""

import json
import random
import time
import urllib.parse
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone

PORT = 9000

# ---------------------------------------------------------------------------
# Fake data
# ---------------------------------------------------------------------------

USERS = [
    {"id": 1, "name": "Alice Nguyen",   "email": "alice@example.com",  "role": "admin",  "active": True,  "joined": "2022-03-15"},
    {"id": 2, "name": "Bob Patel",      "email": "bob@example.com",    "role": "editor", "active": True,  "joined": "2022-07-01"},
    {"id": 3, "name": "Carol Smith",    "email": "carol@example.com",  "role": "viewer", "active": False, "joined": "2023-01-10"},
    {"id": 4, "name": "David Lee",      "email": "david@example.com",  "role": "editor", "active": True,  "joined": "2023-05-20"},
    {"id": 5, "name": "Eva Rossi",      "email": "eva@example.com",    "role": "viewer", "active": True,  "joined": "2024-02-28"},
]

PRODUCTS = [
    {"id": 1, "name": "Widget Pro",     "price": 49.99,  "stock": 120, "category": "hardware",  "rating": 4.5},
    {"id": 2, "name": "DataSync Plus",  "price": 19.99,  "stock": 0,   "category": "software",  "rating": 4.2},
    {"id": 3, "name": "CloudBucket",    "price": 9.99,   "stock": 999, "category": "software",  "rating": 4.8},
    {"id": 4, "name": "DevKit Extreme", "price": 199.00, "stock": 15,  "category": "hardware",  "rating": 4.6},
    {"id": 5, "name": "Sync Cable USB", "price": 12.50,  "stock": 340, "category": "accessory", "rating": 3.9},
]

ORDERS = [
    {"id": 1001, "user_id": 1, "product_id": 3, "qty": 2, "status": "delivered", "total": 19.98,  "date": "2024-11-01"},
    {"id": 1002, "user_id": 2, "product_id": 1, "qty": 1, "status": "shipped",   "total": 49.99,  "date": "2024-11-05"},
    {"id": 1003, "user_id": 4, "product_id": 4, "qty": 1, "status": "pending",   "total": 199.00, "date": "2024-11-08"},
    {"id": 1004, "user_id": 5, "product_id": 5, "qty": 3, "status": "delivered", "total": 37.50,  "date": "2024-11-10"},
    {"id": 1005, "user_id": 1, "product_id": 2, "qty": 1, "status": "cancelled", "total": 19.99,  "date": "2024-11-12"},
]


def get_stats():
    return {
        "source": "LIVE",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": int(time.time() - START_TIME),
        "users": {
            "total": len(USERS),
            "active": sum(1 for u in USERS if u["active"]),
            "inactive": sum(1 for u in USERS if not u["active"]),
        },
        "products": {
            "total": len(PRODUCTS),
            "in_stock": sum(1 for p in PRODUCTS if p["stock"] > 0),
            "out_of_stock": sum(1 for p in PRODUCTS if p["stock"] == 0),
            "avg_rating": round(sum(p["rating"] for p in PRODUCTS) / len(PRODUCTS), 2),
        },
        "orders": {
            "total": len(ORDERS),
            "by_status": {
                "delivered": sum(1 for o in ORDERS if o["status"] == "delivered"),
                "shipped":   sum(1 for o in ORDERS if o["status"] == "shipped"),
                "pending":   sum(1 for o in ORDERS if o["status"] == "pending"),
                "cancelled": sum(1 for o in ORDERS if o["status"] == "cancelled"),
            },
            "total_revenue": round(sum(o["total"] for o in ORDERS if o["status"] != "cancelled"), 2),
        },
        "random_metric": random.randint(100, 999),  # changes every request - proves it's live
    }


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

START_TIME = time.time()


class FakeAPIHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}]  {self.command}  {self.path}")

    def _send(self, code, data, extra_headers=None):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Fake-API", "true")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self, msg="Not found"):
        self._send(404, {"error": msg})

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")

        # Health
        if path == "/health":
            self._send(200, {"status": "ok", "uptime": int(time.time() - START_TIME)})
            return

        # Stats
        if path == "/api/stats":
            self._send(200, get_stats())
            return

        # Users list
        if path == "/api/users":
            self._send(200, {"source": "LIVE", "count": len(USERS), "data": USERS})
            return

        # Single user
        m = re.fullmatch(r"/api/users/(\d+)", path)
        if m:
            uid = int(m.group(1))
            user = next((u for u in USERS if u["id"] == uid), None)
            if user:
                self._send(200, {"source": "LIVE", "data": user})
            else:
                self._not_found(f"User {uid} not found")
            return

        # Products list
        if path == "/api/products":
            self._send(200, {"source": "LIVE", "count": len(PRODUCTS), "data": PRODUCTS})
            return

        # Single product
        m = re.fullmatch(r"/api/products/(\d+)", path)
        if m:
            pid = int(m.group(1))
            product = next((p for p in PRODUCTS if p["id"] == pid), None)
            if product:
                self._send(200, {"source": "LIVE", "data": product})
            else:
                self._not_found(f"Product {pid} not found")
            return

        # Orders list
        if path == "/api/orders":
            self._send(200, {"source": "LIVE", "count": len(ORDERS), "data": ORDERS})
            return

        self._not_found()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        body = self._read_body()

        if path == "/api/users":
            new_user = {
                "id": max(u["id"] for u in USERS) + 1,
                "name":   body.get("name", "New User"),
                "email":  body.get("email", "new@example.com"),
                "role":   body.get("role", "viewer"),
                "active": True,
                "joined": datetime.now().strftime("%Y-%m-%d"),
            }
            self._send(201, {"source": "LIVE", "created": True, "data": new_user})
            return

        self._not_found()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("  ============================================")
    print("   Fake API Server  -  for LocalMockr testing")
    print("  ============================================")
    print()
    print(f"  Listening on http://localhost:{PORT}")
    print()
    print("  Endpoints:")
    print(f"    GET  http://localhost:{PORT}/health")
    print(f"    GET  http://localhost:{PORT}/api/stats")
    print(f"    GET  http://localhost:{PORT}/api/users")
    print(f"    GET  http://localhost:{PORT}/api/users/{{id}}")
    print(f"    POST http://localhost:{PORT}/api/users")
    print(f"    GET  http://localhost:{PORT}/api/products")
    print(f"    GET  http://localhost:{PORT}/api/products/{{id}}")
    print(f"    GET  http://localhost:{PORT}/api/orders")
    print()
    print("  HOW TO TEST FALLBACK:")
    print("  1. In LocalMockr, set External URL = http://localhost:9000")
    print("  2. Set mode = Network + Fallback")
    print("  3. Save a local JSON response as your fallback")
    print("  4. Hit the proxy -> you get LIVE data (source: LIVE)")
    print("  5. Press Ctrl+C here to bring this API down")
    print("  6. Hit the proxy again -> you get FALLBACK data")
    print()
    print("  Press Ctrl+C to stop.")
    print()

    server = HTTPServer(("", PORT), FakeAPIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("  Fake API stopped. LocalMockr will now use fallback responses.")
        print()


if __name__ == "__main__":
    main()
