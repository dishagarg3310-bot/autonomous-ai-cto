import concurrent.futures
import json
import time
import urllib.error
import urllib.request
import uuid

BASE_URL = "http://127.0.0.1:8000"
PASSWORD = "ConcurrentPass123!"

def request(path, method="GET", payload=None, headers=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request_headers = {"Content-Type": "application/json"} if payload is not None else {}
    request_headers.update(headers or {})
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode())
    except Exception as error:
        return "client_error", {"error_type": type(error).__name__}

def unique_flow(_):
    email = f"concurrent-{uuid.uuid4().hex}@example.test"
    signup_status, _ = request("/auth/signup", "POST", {"email": email, "password": PASSWORD})
    login_status, login_body = request("/auth/login", "POST", {"email": email, "password": PASSWORD})
    token = login_body.get("access_token", "")
    profile_status, profile_body = request("/users/me", headers={"Authorization": f"Bearer {token}"}) if token else ("not_attempted", {})
    return signup_status, login_status, profile_status, profile_body.get("email") == email

def same_email_signup(email):
    status, body = request("/auth/signup", "POST", {"email": email, "password": PASSWORD})
    return status, body.get("detail")

def status_counts(values):
    counts = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts

started = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
    unique_results = list(pool.map(unique_flow, range(10)))

race_email = f"race-{uuid.uuid4().hex}@example.test"
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    race_results = list(pool.map(same_email_signup, [race_email] * 8))

health_status, health_body = request("/health")
print(json.dumps({
    "unique_flows": {
        "count": len(unique_results),
        "signup_statuses": status_counts([row[0] for row in unique_results]),
        "login_statuses": status_counts([row[1] for row in unique_results]),
        "profile_statuses": status_counts([row[2] for row in unique_results]),
        "profile_email_matches": sum(row[3] for row in unique_results),
    },
    "same_email_race": {
        "attempts": len(race_results),
        "statuses": status_counts([row[0] for row in race_results]),
        "details": status_counts([row[1] for row in race_results]),
    },
    "post_test_health": {"status": health_status, "body": health_body},
    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
}))
