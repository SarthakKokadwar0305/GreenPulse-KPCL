# GreenPulse AI - Role-Based Access Control (RBAC) Architecture

This document outlines the enterprise authorization framework, granular permission mappings, operator machine isolation model, dynamic UI transformation, and security boundary enforcement implemented for GreenPulse AI.

---

## 1. Enterprise RBAC Architecture

GreenPulse AI enforces a **Dual-Layer RBAC Architecture** spanning both the FastAPI backend and the Next.js frontend:

```
[ Frontend: Next.js Platform ]
  │
  ├── Dynamic Sidebar Navigation (Hides unauthorized modules based on active role)
  ├── Interactive Role Switcher (Real-time demo persona switching in Profile Menu)
  └── Client Route Guard (Renders 403 AccessDeniedView if URL navigated directly)
  │
  ▼  (Bearer Token: HTTP Authorization header)
[ Backend: FastAPI Gateway ]
  │
  ├── Dependency Layer: require_permissions(*perms), require_roles(*roles)
  ├── Machine Isolation Guard: verify_machine_authorization(machine_id, user)
  ├── Service Layer: Injects role-specific filters (e.g. Assigned Machinery query)
  └── Database Layer: SQLAlchemy Models (users, roles, permissions, user_roles, user_machines)
```

### Core Design Rules:
1. **Never Rely Solely on Role Names**: API authorization is strictly driven by granular **Permissions** (`VIEW_DASHBOARD`, `VIEW_ENERGY`, `APPROVE_RECOMMENDATIONS`, etc.).
2. **Backend Authoritative Enforcement**: The frontend hiding links is purely for UX; the backend strictly rejects unauthorized requests with `HTTP 401 Unauthorized` or `HTTP 403 Forbidden`.
3. **Equipment Isolation for Operators**: Operators are strictly isolated to their assigned equipment (`user_machines` junction table). Accessing any unassigned asset yields `HTTP 403 Forbidden`.

---

## 2. The Four Enterprise Roles

GreenPulse AI strictly implements four standardized manufacturing roles:

### 2.1 Plant Head (`PLANT_HEAD`)
- **Authority**: Highest operational and managerial authority inside the industrial facility.
- **Access Scope**:
  - Executive Dashboard
  - Plant Overview & Department Breakdowns
  - Full Machine Monitoring (All 9 Factory Assets)
  - 3D Digital Twin (All Assets)
  - Energy Explorer & Load Analytics
  - Carbon Accounting (GHG Scope 1 & 2)
  - AI Forecast Center & SHAP Diagnostics
  - Anomaly Center & Root Cause Analysis
  - Recommendation Center & Prescriptive ECMs
  - What-If Parametric Simulator
  - Compliance Reports & PDF/CSV Export
  - User Management & Role Administration
  - Platform Security & Audit Trail
- **Capabilities**: View all departments, view all machines, manage personnel, approve energy conservation measures, approve maintenance tickets, configure baseline thresholds, export reports, inspect compliance audit logs.
- **Constraints**: Cannot modify trained AI weights directly (requires MLOps retraining pipeline).

---

### 2.2 Energy Manager (`ENERGY_MANAGER`)
- **Authority**: Responsible for facility-wide energy efficiency, carbon footprint mitigation, and utility tariff optimization.
- **Access Scope**:
  - Executive Dashboard
  - Energy Explorer & Load Profiles
  - Carbon Accounting (GHG Scope 1 & 2)
  - AI Forecast Center & Expenditure Projections
  - Recommendation Center & Prescriptive ECMs
  - What-If Parametric Simulator
  - Compliance & Energy Audit Reports
- **Capabilities**: View plant electrical telemetry, evaluate multi-horizon demand forecasts, execute what-if tariff scenarios, approve energy optimization recommendations, export energy audit reports.
- **Explicit Denials (HTTP 403)**:
  - ❌ Cannot manage users (`MANAGE_USERS`)
  - ❌ Cannot view maintenance configuration or work order dispatch (`SCHEDULE_MAINTENANCE`)
  - ❌ Cannot configure equipment thresholds (`CONFIGURE_THRESHOLDS`)
  - ❌ Cannot access plant administration or audit trail (`VIEW_PLANT`, `VIEW_AUDIT_LOGS`)

---

### 2.3 Maintenance Manager (`MAINTENANCE_MANAGER`)
- **Authority**: Responsible for mechanical and electrical reliability, equipment vibration profiles, thermal indices, and maintenance scheduling.
- **Access Scope**:
  - Executive Dashboard
  - Full Machine Fleet Monitoring (All 9 Factory Assets)
  - 3D Digital Twin (All Assets)
  - Live Equipment Health Indices
  - Anomaly Center & Incident Diagnostics
  - Alert Center & Active Alarms
  - Maintenance History & Work Orders
  - Recommendation Center (View-Only)
- **Capabilities**: Schedule preventive maintenance work orders, close maintenance tickets, inspect unsupervised anomaly detections, acknowledge critical equipment alarms, view prescriptive maintenance recommendations.
- **Explicit Denials (HTTP 403)**:
  - ❌ Cannot access Energy Explorer (`VIEW_ENERGY`)
  - ❌ Cannot access Carbon Dashboard (`VIEW_CARBON`)
  - ❌ Cannot access What-If Simulator (`VIEW_SIMULATOR`, `RUN_SIMULATION`)
  - ❌ Cannot access Financial & Audit Reports (`VIEW_REPORTS`, `EXPORT_REPORTS`)
  - ❌ Cannot manage plant users (`MANAGE_USERS`)

---

### 2.4 Operator (`OPERATOR`)
- **Authority**: Responsible for safely operating assigned machinery during active production shifts.
- **Access Scope**:
  - Executive Dashboard
  - Assigned Machines Telemetry Only
  - Digital Twin (Assigned Machines Only)
  - Live Equipment Operational Status
  - Current Alarms & Critical Alerts for Assigned Machines
  - Standard Operating Procedures (SOPs)
- **Capabilities**: View assigned machinery only, acknowledge active equipment alerts, update operational run/idle status, view shift schedule and assigned work instructions.
- **Explicit Denials (HTTP 403)**:
  - ❌ Cannot access Plant Overview (`VIEW_PLANT`)
  - ❌ Cannot access Energy Explorer (`VIEW_ENERGY`)
  - ❌ Cannot access Carbon Dashboard (`VIEW_CARBON`)
  - ❌ Cannot access Forecast Center (`VIEW_FORECAST`)
  - ❌ Cannot access Recommendation Center (`VIEW_RECOMMENDATIONS`)
  - ❌ Cannot access Reports (`VIEW_REPORTS`)
  - ❌ Cannot access What-If Simulator (`VIEW_SIMULATOR`)
  - ❌ Cannot access unassigned factory assets (e.g. accessing `heat-furnace` returns 403)
  - ❌ Cannot access other plant departments or user management

---

## 3. Assigned Machinery Isolation Model

Operators must never see or interact with machinery outside their certified assignment.

### 3.1 Junction Table: `user_machines`
```sql
CREATE TABLE user_machines (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    machine_id VARCHAR(50) NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, machine_id)
);
```

### 3.2 Seeding Configuration
In `app/utils/seed_data.py`:
- **Lead Operator (`operator_lead`)** is mapped to:
  - `air-compressor` (`COMP-01`)
  - `cnc-machine` (`CNC-01`)

### 3.3 Dynamic Fleet Filtering in API
When `GET /api/v1/machines` is invoked:
- If the caller's role is `PLANT_HEAD` or `MAINTENANCE_MANAGER`, all 9 machines are returned.
- If the caller's role is `OPERATOR`, the query is automatically filtered to matching assigned IDs and codes:
  ```python
  if current_user.role == "OPERATOR":
      assigned_ids = {m.lower() for m in current_user.assigned_machine_ids}
      assigned_codes = {m.upper() for m in current_user.assigned_machine_codes}
      machines = [
          m for m in machines
          if m.id.lower() in assigned_ids or m.code.upper() in assigned_codes
      ]
  ```

### 3.4 Strict Asset Access Verification
When `GET /api/v1/machines/{machine_id}` is called:
```python
def verify_machine_authorization(machine_id_or_code: str, user: User) -> None:
    if not user.can_access_machine(machine_id_or_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You are not assigned to operate machine '{machine_id_or_code}'.",
        )
```
- Requesting `GET /api/v1/machines/air-compressor` $\rightarrow$ `HTTP 200 OK`
- Requesting `GET /api/v1/machines/heat-furnace` $\rightarrow$ `HTTP 403 Forbidden` ("Access denied: You are not assigned to operate machine 'heat-furnace'.")

---

## 4. Frontend Dynamic Transformation

### 4.1 Dynamic Sidebar Generation
In `components/layout/sidebar/sidebar-content.tsx`:
- Modules are filtered in real-time using `useAuthStore.canAccessRoute(href)`.
- When switching to **Lead Operator**, unauthorized modules (Plant Overview, Energy Explorer, Carbon Accounting, Forecast Center, Recommendation Center, What-if Simulator, Reports, Settings) are immediately removed from the DOM.
- The sidebar displays a distinct role badge with the user's title and department.

### 4.2 Interactive Role Switcher
In `components/layout/navbar/profile-menu.tsx`:
- The profile dropdown features a **Switch Role (RBAC Demo)** submenu.
- Evaluators and engineers can toggle between Plant Head, Energy Manager, Maintenance Manager, and Lead Operator with a single click.

### 4.3 Route Guarding & Access Denied View
In `layouts/app-shell.tsx`:
- Direct URL navigation (e.g. manually typing `/energy-explorer` into the browser) is intercepted.
- If unauthorized, the platform renders the enterprise `AccessDeniedView`:
  - Highlights the 403 status code.
  - Explains why the active role lacks clearance.
  - Provides a one-click button to return to the Dashboard or switch to the Plant Head demo persona.

---

## 5. Security & Compliance Audit Logging

Every security-sensitive operation is recorded in the `audit_logs` database:
- `LOGIN_SUCCESS`: Records user identity, role, and client IP address.
- `LOGIN_FAILED`: Records invalid credential attempts and target username.
- `LOGIN_BLOCKED_INACTIVE`: Records login attempts on deactivated accounts.
- `TOKEN_ROTATED`: Records refresh token renewal events.
- `LOGOUT`: Records session termination and token invalidation.
- `USER_CREATED`: Records administrative account creation.
- `MACHINES_ASSIGNED`: Records equipment reassignment for operators.
