import concurrent.futures
import json
import subprocess
import threading
import urllib.error
import urllib.request
import uuid


ROOT = r"C:\Users\abina\autonomous-ai-cto\ai-cto-task2"
BASE_URL = "http://127.0.0.1:8000"
PASSWORD = "ConcurrentDuplicatePass123!"


def signup(email):
    body = json.dumps({"email": email, "password": PASSWORD}).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE_URL}/auth/signup",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def database_count(email):
    code = (
        "import sqlite3; "
        "c=sqlite3.connect('/data/app.db'); "
        f"print(c.execute('SELECT COUNT(*) FROM users WHERE email = ?', ({email!r},)).fetchone()[0])"
    )
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", "backend", "python", "-c", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return int(result.stdout.strip())


race_email = f"race-fixed-{uuid.uuid4().hex}@example.test"
barrier = threading.Barrier(8)


def concurrent_signup(_):
    barrier.wait()
    return signup(race_email)


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    race_results = list(pool.map(concurrent_signup, range(8)))

race_statuses = [status for status, _ in race_results]
race_details = [body.get("detail") for _, body in race_results]
race_row_count = database_count(race_email)

sequential_email = f"sequential-fixed-{uuid.uuid4().hex}@example.test"
sequential_first_status, _ = signup(sequential_email)
sequential_second_status, sequential_second_body = signup(sequential_email)
sequential_row_count = database_count(sequential_email)

evidence = {
    "emails_redacted": True,
    "concurrent": {
        "attempts": len(race_results),
        "statuses": {str(status): race_statuses.count(status) for status in sorted(set(race_statuses))},
        "success_count": race_statuses.count(200),
        "duplicate_or_conflict_count": sum(status in {400, 409} for status in race_statuses),
        "details": sorted(set(detail for detail in race_details if detail)),
        "database_row_count": race_row_count,
    },
    "sequential": {
        "first_status": sequential_first_status,
        "second_status": sequential_second_status,
        "second_detail": sequential_second_body.get("detail"),
        "database_row_count": sequential_row_count,
    },
}
print(json.dumps(evidence))

if not (
    evidence["concurrent"]["success_count"] == 1
    and evidence["concurrent"]["duplicate_or_conflict_count"] == 7
    and evidence["concurrent"]["database_row_count"] == 1
    and evidence["sequential"]["first_status"] == 200
    and evidence["sequential"]["second_status"] == 400
    and evidence["sequential"]["database_row_count"] == 1
):
    raise SystemExit("duplicate signup verification failed")
