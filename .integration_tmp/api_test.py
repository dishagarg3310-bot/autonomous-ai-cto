import json
import time
import urllib.error
import urllib.request
import uuid


BASE_URL = "http://127.0.0.1:8000"
PASSWORD = "IntegrationPass123!"
EMAIL = f"integration-{uuid.uuid4().hex}@example.test"


def request(path, method="GET", payload=None, headers=None):
    encoded = json.dumps(payload).encode("utf-8") if payload is not None else None
    request_headers = {"Content-Type": "application/json"} if payload is not None else {}
    request_headers.update(headers or {})
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=encoded, headers=request_headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw)
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        return error.code, json.loads(raw)


started = time.perf_counter()
signup_status, signup_body = request("/auth/signup", "POST", {"email": EMAIL, "password": PASSWORD})
login_status, login_body = request("/auth/login", "POST", {"email": EMAIL, "password": PASSWORD})
token = login_body.get("access_token", "")
profile_status, profile_body = request(
    "/users/me", headers={"Authorization": f"Bearer {token}"}
)
duplicate_status, duplicate_body = request(
    "/auth/signup", "POST", {"email": EMAIL, "password": PASSWORD}
)
invalid_login_status, invalid_login_body = request(
    "/auth/login", "POST", {"email": EMAIL, "password": "WrongPass123!"}
)
missing_token_status, missing_token_body = request("/users/me")
invalid_token_status, invalid_token_body = request(
    "/users/me", headers={"Authorization": "Bearer invalid.token.value"}
)

print(json.dumps({
    "email_redacted": True,
    "signup": {"status": signup_status, "body_keys": sorted(signup_body.keys()), "email_matches": signup_body.get("email") == EMAIL},
    "login": {"status": login_status, "body_keys": sorted(login_body.keys()), "token_returned": bool(token), "token_type": login_body.get("token_type")},
    "profile": {"status": profile_status, "body_keys": sorted(profile_body.keys()), "email_matches": profile_body.get("email") == EMAIL},
    "duplicate_signup": {"status": duplicate_status, "detail": duplicate_body.get("detail")},
    "invalid_login": {"status": invalid_login_status, "detail": invalid_login_body.get("detail")},
    "missing_token": {"status": missing_token_status, "detail": missing_token_body.get("detail")},
    "invalid_token": {"status": invalid_token_status, "detail": invalid_token_body.get("detail")},
    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
}))
