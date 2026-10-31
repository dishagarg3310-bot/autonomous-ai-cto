import sqlite3


DATABASE = "/data/app.db"
TEST_EMAIL = "race-c99fa4025cf94a4ab97e81e6bc9c6827@example.test"


connection = sqlite3.connect(DATABASE)
try:
    connection.execute("BEGIN IMMEDIATE")
    count = connection.execute(
        "SELECT COUNT(*) FROM users WHERE email = ?", (TEST_EMAIL,)
    ).fetchone()[0]
    if count != 8:
        raise RuntimeError(f"Expected 8 known test rows, found {count}")

    connection.execute(
        "DELETE FROM users WHERE email = ? AND rowid != "
        "(SELECT MIN(rowid) FROM users WHERE email = ?)",
        (TEST_EMAIL, TEST_EMAIL),
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email ON users(email)"
    )
    remaining = connection.execute(
        "SELECT COUNT(*) FROM users WHERE email = ?", (TEST_EMAIL,)
    ).fetchone()[0]
    duplicate_groups = connection.execute(
        "SELECT COUNT(*) FROM (SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    indexes = connection.execute("PRAGMA index_list('users')").fetchall()
    connection.commit()
    print({
        "removed_known_test_duplicates": count - remaining,
        "remaining_known_test_rows": remaining,
        "duplicate_group_count": duplicate_groups,
        "unique_index_present": any(name == "uq_users_email" and unique for _, name, unique, *_ in indexes),
    })
except Exception:
    connection.rollback()
    raise
finally:
    connection.close()
