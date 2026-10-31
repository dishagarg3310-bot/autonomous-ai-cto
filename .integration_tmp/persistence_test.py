import json
import subprocess
import time
import urllib.error
import urllib.request
import uuid


ROOT = r"C:\Users\abina\autonomous-ai-cto\ai-cto-task2"
BASE_URL = "http://127.0.0.1:8000"
EMAIL = f"persistence-{uuid.uuid4().hex}@example.test"
PASSWORD = "PersistencePass123!"


def request(path, method="GET", payload=None, headers=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request_headers = {"Content-Type": "application/json"} if payload is not None else {}
    request_headers.update(headers or {})
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode())


def wait_for_health():
    deadline = time.time() + 60
    last = None
    while time.time() < deadline:
        try:
            last = request("/health")
            if last[0] == 200:
                return last
        except Exception as error:
            last = repr(error)
        time.sleep(1)
    raise RuntimeError(f"health did not recover: {last}")


signup_status, signup_body = request("/auth/signup", "POST", {"email": EMAIL, "password": PASSWORD})
login_status, login_body = request("/auth/login", "POST", {"email": EMAIL, "password": PASSWORD})
token = login_body["access_token"]
headers = {"Authorization": f"Bearer {token}"}
before_status, before_body = request("/users/me", headers=headers)

backend_restart = subprocess.run(
    ["docker", "compose", "restart", "backend"], cwd=ROOT, text=True, capture_output=True, timeout=90
)
backend_health_status, _ = wait_for_health()
after_backend_status, after_backend_body = request("/users/me", headers=headers)

stack_restart = subprocess.run(
    ["docker", "compose", "restart"], cwd=ROOT, text=True, capture_output=True, timeout=90
)
stack_health_status, _ = wait_for_health()
after_stack_status, after_stack_body = request("/users/me", headers=headers)

print(json.dumps({
    "email_redacted": True,
    "creation": {"signup_status": signup_status, "login_status": login_status, "profile_status": before_status, "email_matches": before_body.get("email") == EMAIL},
    "backend_restart": {"command_exit_code": backend_restart.returncode, "health_status": backend_health_status, "profile_status": after_backend_status, "email_matches": after_backend_body.get("email") == EMAIL},
    "full_stack_restart": {"command_exit_code": stack_restart.returncode, "health_status": stack_health_status, "profile_status": after_stack_status, "email_matches": after_stack_body.get("email") == EMAIL},
}))
