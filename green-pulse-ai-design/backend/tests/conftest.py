"""
Pytest configuration and path resolution for GreenPulse AI.
Ensures both backend and project root are in sys.path and configures
test dependency injection for enterprise security.
"""
import sys
from pathlib import Path
import pytest

# Paths
TESTS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TESTS_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

for p in [str(BACKEND_DIR), str(PROJECT_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.core.dependencies import get_current_user
from app.models.user import User
from app.main import app


@pytest.fixture(autouse=True)
def setup_test_auth(request):
    """
    Automatically sets mock super-user for general ML/endpoint tests,
    while leaving real auth dependencies intact for test_auth_*.py modules.
    """
    if "test_auth" in request.node.nodeid or "rbac" in request.node.nodeid:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        yield
    else:
        mock_plant_head = User(
            id=1,
            username="plant_head",
            email="plant.head@greenpulse.ai",
            hashed_password="",
            full_name="Rajesh Nair (Test Plant Head)",
            role="PLANT_HEAD",
            department="Executive Management",
            status="active",
            is_active=True,
            is_admin=True,
        )
        app.dependency_overrides[get_current_user] = lambda: mock_plant_head
        yield
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
