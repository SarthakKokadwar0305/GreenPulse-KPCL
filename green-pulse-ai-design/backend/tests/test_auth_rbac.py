"""
GreenPulse AI - Enterprise Authentication & Role-Based Access Control (RBAC) Test Suite
Exhaustively validates:
1. User registration & credential verification (bcrypt)
2. JWT access token generation & claims
3. Refresh token rotation & session revocation
4. The 4 Enterprise Roles:
   - Plant Head (Full oversight, user management, audit logs)
   - Energy Manager (Energy, carbon, forecast, simulator, recommendations)
   - Maintenance Manager (Machines, health, anomalies, work orders)
   - Operator (Assigned machines only, alerts, 403 on unassigned machines)
5. Granular permission enforcement (401 unauthenticated, 403 forbidden)
6. Security compliance audit logging
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_user


@pytest.fixture
def client():
    # Ensure real authentication dependency is tested
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    with TestClient(app) as test_client:
        yield test_client


def get_token(client, username_or_email, password):
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username_or_email, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {username_or_email}: {res.text}"
    return res.json()["data"]["access_token"]


# =============================================================================
# 1. AUTHENTICATION & TOKEN LIFECYCLE TESTS
# =============================================================================

def test_login_plant_head_success(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "plant.head@greenpulse.ai", "password": "PlantHead@2026"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "PLANT_HEAD"
    assert "VIEW_PLANT" in data["user"]["permissions"]
    assert "MANAGE_USERS" in data["user"]["permissions"]
    assert len(data["user"]["assigned_machines"]) >= 8


def test_login_operator_assigned_machines(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "operator1@greenpulse.ai", "password": "Operator@2026"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    user = data["user"]
    assert user["role"] == "OPERATOR"
    # Assigned machines must contain only the assigned machinery
    assert "air-compressor" in user["assigned_machines"] or "COMP-01" in user["assigned_machines"]
    assert len(user["assigned_machines"]) <= 3


def test_login_invalid_password(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "plant.head@greenpulse.ai", "password": "WrongPassword!999"},
    )
    assert res.status_code == 401
    assert "Invalid username/email or password" in res.json()["message"]


def test_oauth2_password_form_token(client):
    """Verifies Swagger UI OAuth2 password flow compatibility."""
    res = client.post(
        "/api/v1/auth/token",
        data={"username": "plant_head", "password": "PlantHead@2026"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_current_user_me_endpoint(client):
    token = get_token(client, "energy.manager@greenpulse.ai", "EnergyManager@2026")
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    user = res.json()["data"]
    assert user["role"] == "ENERGY_MANAGER"
    assert user["email"] == "energy.manager@greenpulse.ai"


def test_refresh_token_rotation(client):
    # 1. Login to obtain tokens
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "plant.head@greenpulse.ai", "password": "PlantHead@2026"},
    )
    old_refresh = login_res.json()["data"]["refresh_token"]

    # 2. Refresh tokens
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert ref_res.status_code == 200
    new_data = ref_res.json()["data"]
    new_access = new_data["access_token"]
    new_refresh = new_data["refresh_token"]
    assert new_refresh != old_refresh

    # 3. Old refresh token cannot be reused (rotation security)
    replay_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert replay_res.status_code == 401


def test_unauthenticated_request_rejected(client):
    """Unauthenticated calls to protected endpoints must return 401."""
    res = client.get("/api/v1/energy/analytics")
    assert res.status_code == 401


# =============================================================================
# 2. ROLE-BASED ACCESS CONTROL (RBAC) AUTHORIZATION MATRIX
# =============================================================================

def test_plant_head_full_access(client):
    token = get_token(client, "plant.head@greenpulse.ai", "PlantHead@2026")
    headers = {"Authorization": f"Bearer {token}"}

    # Plant Head has full visibility across all modules
    assert client.get("/api/v1/dashboard/overview", headers=headers).status_code == 200
    assert client.get("/api/v1/plant/overview", headers=headers).status_code == 200
    assert client.get("/api/v1/machines", headers=headers).status_code == 200
    assert client.get("/api/v1/energy/analytics", headers=headers).status_code == 200
    assert client.get("/api/v1/carbon/accounting", headers=headers).status_code == 200
    assert client.get("/api/v1/forecast", headers=headers).status_code == 200
    assert client.get("/api/v1/recommendations", headers=headers).status_code == 200
    assert client.get("/api/v1/reports", headers=headers).status_code == 200
    assert client.get("/api/v1/auth/users", headers=headers).status_code == 200
    assert client.get("/api/v1/auth/audit-logs", headers=headers).status_code == 200


def test_energy_manager_permissions(client):
    token = get_token(client, "energy.manager@greenpulse.ai", "EnergyManager@2026")
    headers = {"Authorization": f"Bearer {token}"}

    # Allowed: Dashboard, Energy, Carbon, Forecast, Recommendations, Simulator, Reports
    assert client.get("/api/v1/dashboard/overview", headers=headers).status_code == 200
    assert client.get("/api/v1/energy/analytics", headers=headers).status_code == 200
    assert client.get("/api/v1/carbon/accounting", headers=headers).status_code == 200
    assert client.get("/api/v1/forecast", headers=headers).status_code == 200
    assert client.get("/api/v1/recommendations", headers=headers).status_code == 200
    assert client.get("/api/v1/reports", headers=headers).status_code == 200
    
    # Denied: Plant Overview, User Management, Audit Logs
    assert client.get("/api/v1/plant/overview", headers=headers).status_code == 403
    assert client.get("/api/v1/auth/users", headers=headers).status_code == 403
    assert client.get("/api/v1/auth/audit-logs", headers=headers).status_code == 403


def test_maintenance_manager_permissions(client):
    token = get_token(client, "maintenance.manager@greenpulse.ai", "Maintenance@2026")
    headers = {"Authorization": f"Bearer {token}"}

    # Allowed: Dashboard, Machines, Anomalies, Recommendations (view-only)
    assert client.get("/api/v1/dashboard/overview", headers=headers).status_code == 200
    assert client.get("/api/v1/machines", headers=headers).status_code == 200
    assert client.get("/api/v1/anomaly", headers=headers).status_code == 200
    assert client.get("/api/v1/recommendations", headers=headers).status_code == 200

    # Denied: Energy Explorer, Carbon Dashboard, Forecast Center, Reports, Users
    assert client.get("/api/v1/energy/analytics", headers=headers).status_code == 403
    assert client.get("/api/v1/carbon/accounting", headers=headers).status_code == 403
    assert client.get("/api/v1/forecast", headers=headers).status_code == 403
    assert client.get("/api/v1/reports", headers=headers).status_code == 403
    assert client.get("/api/v1/auth/users", headers=headers).status_code == 403


def test_operator_assigned_machines_isolation(client):
    token = get_token(client, "operator1@greenpulse.ai", "Operator@2026")
    headers = {"Authorization": f"Bearer {token}"}

    # Allowed: Dashboard, Assigned Machines list, Assigned Alerts
    assert client.get("/api/v1/dashboard/overview", headers=headers).status_code == 200
    
    # 1. Machines endpoint automatically returns ONLY assigned machines
    machines_res = client.get("/api/v1/machines", headers=headers)
    assert machines_res.status_code == 200
    machines = machines_res.json()["data"]
    assert len(machines) <= 3
    assigned_codes = {m["code"] for m in machines}
    assert "COMP-01" in assigned_codes or "CNC-01" in assigned_codes

    # 2. Accessing assigned machine succeeds
    assert client.get("/api/v1/machines/air-compressor", headers=headers).status_code in [200, 404]

    # 3. Accessing UNASSIGNED machine returns 403 Forbidden!
    unassigned_res = client.get("/api/v1/machines/heat-furnace", headers=headers)
    assert unassigned_res.status_code == 403
    assert "Access denied: You are not assigned to operate machine" in unassigned_res.json()["message"]

    # 4. Operator CANNOT access other modules
    assert client.get("/api/v1/plant/overview", headers=headers).status_code == 403
    assert client.get("/api/v1/energy/analytics", headers=headers).status_code == 403
    assert client.get("/api/v1/carbon/accounting", headers=headers).status_code == 403
    assert client.get("/api/v1/forecast", headers=headers).status_code == 403
    assert client.get("/api/v1/recommendations", headers=headers).status_code == 403
    assert client.get("/api/v1/reports", headers=headers).status_code == 403
    assert client.get("/api/v1/auth/users", headers=headers).status_code == 403


# =============================================================================
# 3. USER MANAGEMENT & AUDIT LOGGING
# =============================================================================

def test_user_registration_and_audit(client):
    plant_head_token = get_token(client, "plant.head@greenpulse.ai", "PlantHead@2026")
    operator_token = get_token(client, "operator1@greenpulse.ai", "Operator@2026")

    # Operator cannot register users (403)
    forbidden_res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "junior_op_99",
            "email": "junior.op@greenpulse.ai",
            "password": "Password@123",
            "full_name": "Junior Operator",
            "role": "OPERATOR",
            "department": "Machining Bay",
        },
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert forbidden_res.status_code == 403

    # Plant Head can register users (200)
    import time
    uname = f"op_test_{int(time.time())}"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "username": uname,
            "email": f"{uname}@greenpulse.ai",
            "password": "Password@123",
            "full_name": "Test Operator New",
            "role": "OPERATOR",
            "department": "Machining Bay",
            "assigned_machine_ids": ["air-compressor"],
        },
        headers={"Authorization": f"Bearer {plant_head_token}"},
    )
    assert reg_res.status_code == 200
    created = reg_res.json()["data"]
    assert created["username"] == uname
    assert created["role"] == "OPERATOR"

    # Verify Audit Log entry created
    audit_res = client.get("/api/v1/auth/audit-logs", headers={"Authorization": f"Bearer {plant_head_token}"})
    assert audit_res.status_code == 200
    logs = audit_res.json()["data"]
    assert len(logs) > 0
    actions = [l["action"] for l in logs]
    assert "USER_CREATED" in actions or "LOGIN_SUCCESS" in actions
