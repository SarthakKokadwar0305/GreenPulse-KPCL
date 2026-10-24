"""
GreenPulse AI - Backend Test Runner
Performs offline integration testing on all Clean Architecture layers and API endpoints.
Tests unauthenticated handling (401) and authenticated requests under Enterprise RBAC.
"""
import sys
from fastapi.testclient import TestClient

from app.main import app

ENDPOINTS_TO_TEST = [
    ("GET", "/"),
    ("GET", "/health"),
    ("GET", "/docs"),
    ("GET", "/api/v1/dashboard/overview"),
    ("GET", "/api/v1/plant/overview"),
    ("GET", "/api/v1/machines"),
    ("GET", "/api/v1/machines/air-compressor"),
    ("GET", "/api/v1/energy/analytics?time_range=24h"),
    ("GET", "/api/v1/carbon/accounting?time_range=month"),
    ("GET", "/api/v1/forecast?horizon=24"),
    ("GET", "/api/v1/anomaly"),
    ("GET", "/api/v1/recommendations"),
    ("POST", "/api/v1/simulator/simulate", {"production_load_percent": 110, "machine_runtime_hours": 18, "shift_schedule": "2-shift", "base_tariff_per_kwh": 7.5, "renewable_share_percent": 25}),
    ("GET", "/api/v1/reports"),
    ("GET", "/api/v1/reports/download/REP-ENG-20261024?format=csv"),
    ("GET", "/api/v1/settings"),
    ("POST", "/api/v1/settings", {"plant": {"facility_name": "GreenPulse Central Hub - Unit 4 (Audited)", "contracted_demand_kw": 2600.0}}),
    ("GET", "/api/v1/copilot/collections"),
    ("POST", "/api/v1/copilot/chat", {"query": "Show highest energy consuming machine right now", "session_id": "test-session-live"}),
    ("POST", "/api/v1/copilot/chat", {"query": "Explain SOP peak demand curtailment protocol", "session_id": "test-session-rag"}),
    ("POST", "/api/v1/copilot/chat", {"query": "What is Power Factor and why does DISCOM penalize low PF?", "session_id": "test-session-concept"}),
    ("GET", "/api/v1/copilot/history/test-session-live"),
]

def run_tests():
    print("\n=======================================================")
    print("GreenPulse AI Backend Test Verification Suite (Enterprise RBAC)")
    print("=======================================================\n")
    
    passed = 0
    failed = 0
    
    with TestClient(app) as client:
        # Step 1: Verify unauthenticated request to protected route is rejected with 401
        res_unauth = client.get("/api/v1/energy/analytics")
        if res_unauth.status_code == 401:
            print("[PASS] Unauthenticated request correctly rejected with HTTP 401 Unauthorized")
            passed += 1
        else:
            print(f"[FAIL] Expected 401 for unauthenticated request, got {res_unauth.status_code}")
            failed += 1

        # Step 2: Authenticate as Plant Head
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username_or_email": "plant.head@greenpulse.ai", "password": "PlantHead@2026"}
        )
        if login_res.status_code == 200:
            token = login_res.json()["data"]["access_token"]
            print("[PASS] Successfully authenticated Plant Head credentials -> JWT Bearer token acquired")
            passed += 1
        else:
            print(f"[FAIL] Plant Head authentication failed: {login_res.text}")
            return 1

        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Test all operational endpoints with authenticated bearer token
        for item in ENDPOINTS_TO_TEST:
            method = item[0]
            url = item[1]
            payload = item[2] if len(item) > 2 else None
            
            try:
                if method == "GET":
                    res = client.get(url, headers=headers)
                elif method == "POST":
                    res = client.post(url, json=payload, headers=headers)
                else:
                    continue
                    
                if res.status_code in [200, 201]:
                    print(f"[PASS] {method:4s} {url:40s} -> HTTP {res.status_code}")
                    passed += 1
                else:
                    print(f"[FAIL] {method:4s} {url:40s} -> HTTP {res.status_code} ({res.text[:120]})")
                    failed += 1
            except Exception as e:
                print(f"[ERROR] {method:4s} {url:40s} -> {e}")
                failed += 1

    print("\n-------------------------------------------------------")
    print(f"Results: {passed} passed, {failed} failed.")
    print("=======================================================\n")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(run_tests())
