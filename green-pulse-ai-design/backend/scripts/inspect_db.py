import sqlite3

con = sqlite3.connect("greenpulse.db")
cur = con.cursor()

tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
print("=== DATABASE RECORD COUNTS ===")
for t in tables:
    cnt = cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"Table {t:20s}: {cnt:6d} records")

print("\n=== MACHINES TABLE VERIFICATION ===")
machines = cur.execute("SELECT id, name, code, rated_power_kw, status FROM machines ORDER BY code").fetchall()
print(f"Total Unique Machines in DB: {len(machines)}")
for m in machines:
    print(f"  Code: {m[2]:8s} | ID: {m[0]:15s} | Rated: {m[3]:5.1f} kW | Status: {m[4]:10s} | Name: {m[1]}")

con.close()
