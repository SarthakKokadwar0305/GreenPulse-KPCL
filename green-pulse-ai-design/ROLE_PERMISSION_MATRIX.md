# Role-Permission Matrix & Enterprise Access Control Specification

**Project**: GreenPulse AI — Industrial Energy & Asset Intelligence Platform  
**Architecture**: FastAPI Backend + Clean Architecture + Next.js Enterprise Shell  
**Security Standard**: OAuth2 JWT Bearer Tokens, Granular Permission-Based RBAC, Dynamic Asset Isolation  

---

## 1. Executive Summary

GreenPulse AI enforces a dual-layered security governance model combining **Role-Based Access Control (RBAC)** with **Granular Functional Permissions** and **Dynamic Machinery Scoping**:

1. **Role Layer**: Coarse-grained enterprise identity (`Plant Head`, `Energy Manager`, `Maintenance Manager`, `Operator`).
2. **Permission Layer**: Fine-grained authorization gates (`VIEW_DASHBOARD`, `VIEW_ENERGY`, `APPROVE_RECOMMENDATIONS`, `SCHEDULE_MAINTENANCE`, `MANAGE_USERS`, etc.).
3. **Data Scoping Layer**: Multi-tenant machine-level partitioning (`user_machines` relationship). Operators can only access machinery explicitly assigned to their user ID (e.g., COMP-01, CNC-01).

---

## 2. Enterprise Roles Overview

| Role Code | Role Name | Authority Scope | Asset Access Boundary | Primary Responsibility |
|:---|:---|:---|:---|:---|
| `PLANT_HEAD` | **Plant Head** | Global Executive | **All Machinery & Facilities** | Full plant supervision, user governance, capital approvals, compliance audit. |
| `ENERGY_MANAGER` | **Energy Manager** | Plant Energy & ESG | **Plant Aggregate & Energy Systems** | Energy consumption optimization, carbon abatement, forecasting, simulations. |
| `MAINTENANCE_MANAGER` | **Maintenance Manager** | Reliability & Health | **All Machinery** | Asset health, anomaly investigation, maintenance work orders, alert resolution. |
| `OPERATOR` | **Operator** | Shift Operations | **Assigned Machinery Only** | Running assigned assets safely, telemetry tracking, operational alert acknowledgement. |

---

## 3. Comprehensive Role-to-Permission Matrix

| Permission Code | Permission Description | Plant Head | Energy Manager | Maintenance Manager | Operator |
|:---|:---|:---:|:---:|:---:|:---:|
| `VIEW_DASHBOARD` | Access enterprise KPI dashboard | ✅ | ✅ | ✅ | ✅ |
| `VIEW_PLANT` | View global plant layout and department metrics | ✅ | ❌ | ❌ | ❌ |
| `VIEW_MACHINE` | View all plant machines across all lines | ✅ | ❌ | ✅ | ❌ |
| `VIEW_ASSIGNED_MACHINE` | View assigned machines in operator shift scope | ✅ | ❌ | ✅ | ✅ |
| `VIEW_DIGITAL_TWIN` | Access physics & 3D digital twin models | ✅ | ❌ | ✅ | ✅ *(Assigned Only)* |
| `VIEW_ENERGY` | Access Energy Explorer, ISO 50001 metrics | ✅ | ✅ | ❌ | ❌ |
| `VIEW_CARBON` | Access GHG Protocol Scope 1 & 2 carbon accounting | ✅ | ✅ | ❌ | ❌ |
| `VIEW_FORECAST` | View AI load & consumption forecasting | ✅ | ✅ | ❌ | ❌ |
| `VIEW_ALERTS` | View operational & health alerts | ✅ | ❌ | ✅ | ✅ *(Assigned Only)* |
| `VIEW_RECOMMENDATIONS` | View AI energy conservation recommendations | ✅ | ✅ | ❌ | ❌ |
| `VIEW_SIMULATOR` | Access What-If tariff & operational simulator | ✅ | ✅ | ❌ | ❌ |
| `VIEW_REPORTS` | Access enterprise compliance & KPI reports | ✅ | ✅ *(Energy Only)* | ❌ | ❌ |
| `VIEW_AUDIT_LOGS` | Access security, auth, and action audit trail | ✅ | ❌ | ❌ | ❌ |
| `MANAGE_USERS` | Register, edit, and deactivate enterprise users | ✅ | ❌ | ❌ | ❌ |
| `CONFIGURE_THRESHOLDS` | Modify machine alert and telemetry thresholds | ✅ | ❌ | ❌ | ❌ |
| `ACKNOWLEDGE_ALERT` | Acknowledge active alerts and anomalies | ✅ | ❌ | ✅ | ✅ *(Assigned Only)* |
| `UPDATE_MACHINE_STATUS` | Toggle machine state (RUNNING, IDLE, STOPPED) | ✅ | ❌ | ✅ | ✅ *(Assigned Only)* |
| `SCHEDULE_MAINTENANCE` | Create and schedule maintenance work orders | ✅ | ❌ | ✅ | ❌ |
| `CLOSE_WORK_ORDER` | Sign off and close completed maintenance tickets | ✅ | ❌ | ✅ | ❌ |
| `EXPORT_REPORTS` | Generate and export PDF/CSV audit reports | ✅ | ✅ | ❌ | ❌ |
| `APPROVE_RECOMMENDATIONS`| Approve ECM energy-saving actions | ✅ | ✅ | ❌ | ❌ |
| `RUN_SIMULATION` | Execute compute-intensive what-if models | ✅ | ✅ | ❌ | ❌ |

---

## 4. API Endpoint Authorization Matrix

Every backend route is guarded using FastAPI's dependency injection (`require_permissions` and `verify_machine_authorization`).

| HTTP Method | API Endpoint Path | Required Permission(s) | Allowed Roles | Denied Roles | Machinery Scoping / Special Rules |
|:---|:---|:---|:---|:---|:---|
| `POST` | `/api/v1/auth/login` | *Public* | *All* | None | Validates credentials, issues JWT token pair, records audit log |
| `POST` | `/api/v1/auth/token` | *Public (OAuth2 Form)* | *All* | None | Standard OAuth2 Password Flow for Swagger UI |
| `POST` | `/api/v1/auth/refresh` | *Valid Refresh Token* | *All* | None | Single-use rotation; invalidates parent refresh token |
| `POST` | `/api/v1/auth/logout` | *Authenticated* | *All* | None | Revokes active session tokens, records audit log |
| `GET` | `/api/v1/auth/me` | *Authenticated* | *All* | None | Returns user profile, role, permissions, assigned machines |
| `POST` | `/api/v1/auth/register` | `MANAGE_USERS` | `PLANT_HEAD` | `ENERGY_MGR`, `MAINT_MGR`, `OPERATOR` | Creates user, assigns roles & machines |
| `GET` | `/api/v1/auth/users` | `MANAGE_USERS` | `PLANT_HEAD` | `ENERGY_MGR`, `MAINT_MGR`, `OPERATOR` | Lists all users, departments, and machine mappings |
| `GET` | `/api/v1/auth/roles` | `MANAGE_USERS` | `PLANT_HEAD` | `ENERGY_MGR`, `MAINT_MGR`, `OPERATOR` | Lists defined roles and associated permission codes |
| `GET` | `/api/v1/auth/audit-logs` | `VIEW_AUDIT_LOGS` | `PLANT_HEAD` | `ENERGY_MGR`, `MAINT_MGR`, `OPERATOR` | Paginated immutable security audit log |
| `GET` | `/api/v1/dashboard/overview` | `VIEW_DASHBOARD` | *All Roles* | None | Returns role-tailored summary metrics |
| `GET` | `/api/v1/plant/overview` | `VIEW_PLANT` | `PLANT_HEAD` | `ENERGY_MGR`, `MAINT_MGR`, `OPERATOR` | Executive plant overview and multi-line statistics |
| `GET` | `/api/v1/machines` | `VIEW_MACHINE`, `VIEW_ASSIGNED_MACHINE` | *All Roles* | None | **Operator Isolation**: Auto-filtered to assigned machines only |
| `GET` | `/api/v1/machines/{machine_id}` | `VIEW_MACHINE`, `VIEW_ASSIGNED_MACHINE` | *All Roles* | None | **403 Forbidden** if Operator attempts access to unassigned asset |
| `GET` | `/api/v1/machines/{machine_id}/status` | `VIEW_MACHINE`, `VIEW_ASSIGNED_MACHINE` | *All Roles* | None | Isolated to assigned machines for Operators |
| `GET` | `/api/v1/machines/{machine_id}/digital-twin`| `VIEW_DIGITAL_TWIN` | `PLANT_HEAD`, `MAINT_MGR`, `OPERATOR` | `ENERGY_MGR` | Isolated to assigned machines for Operators |
| `GET` | `/api/v1/energy/overview` | `VIEW_ENERGY` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | Plant-level power factor, peak demand, consumption |
| `GET` | `/api/v1/energy/breakdown` | `VIEW_ENERGY` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | Departmental energy consumption allocation |
| `GET` | `/api/v1/carbon/overview` | `VIEW_CARBON` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | Scope 1 & 2 GHG footprint, emission intensity |
| `GET` | `/api/v1/forecast` | `VIEW_FORECAST` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | AI energy forecast (Prophet, XGBoost, LSTM) |
| `GET` | `/api/v1/recommendations` | `VIEW_RECOMMENDATIONS` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | AI Energy Conservation Measures (ECM) |
| `POST`| `/api/v1/recommendations/{id}/apply` | `APPROVE_RECOMMENDATIONS` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | Commits ECM action, logs approval in audit log |
| `POST`| `/api/v1/simulator/run` | `RUN_SIMULATION` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | Tariff and load shifting what-if simulation |
| `GET` | `/api/v1/reports` | `VIEW_REPORTS` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | Lists generated compliance reports |
| `POST`| `/api/v1/reports/generate` | `EXPORT_REPORTS` | `PLANT_HEAD`, `ENERGY_MGR` | `MAINT_MGR`, `OPERATOR` | Triggers PDF/Excel report generation job |
| `GET` | `/api/v1/anomaly/alerts` | `VIEW_ALERTS` | `PLANT_HEAD`, `MAINT_MGR`, `OPERATOR` | `ENERGY_MGR` | **Operator Isolation**: Auto-filtered to assigned machines |
| `POST`| `/api/v1/anomaly/alerts/{id}/ack` | `ACKNOWLEDGE_ALERT` | `PLANT_HEAD`, `MAINT_MGR`, `OPERATOR` | `ENERGY_MGR` | Operators can only acknowledge assigned asset alerts |
| `POST`| `/api/v1/anomaly/work-orders` | `SCHEDULE_MAINTENANCE` | `PLANT_HEAD`, `MAINT_MGR` | `ENERGY_MGR`, `OPERATOR` | Generates CMMS work order ticket |

---

## 5. Frontend Module Visibility & Navigation Matrix

The Next.js enterprise frontend adapts dynamically based on the active user identity stored in the Zustand client auth store (`store/auth-store.ts`).

| Navigation Route | Module Label | Plant Head | Energy Manager | Maintenance Manager | Operator | Direct Access Fallback |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| `/dashboard` | Dashboard Overview | Visible | Visible | Visible | Visible | Allowed |
| `/plant` | Plant Overview | Visible | Hidden | Hidden | Hidden | `403 Forbidden AccessDeniedView` |
| `/machines` | Machine Monitoring | Visible *(All)* | Hidden | Visible *(All)* | Visible *(Assigned)* | Shows assigned assets only for Operator |
| `/digital-twin` | Digital Twin 3D | Visible *(All)* | Hidden | Visible *(All)* | Visible *(Assigned)* | Shows assigned asset models only |
| `/energy` | Energy Explorer | Visible | Visible | Hidden | Hidden | `403 Forbidden AccessDeniedView` |
| `/carbon` | Carbon Accounting | Visible | Visible | Hidden | Hidden | `403 Forbidden AccessDeniedView` |
| `/forecast` | Forecast Center | Visible | Visible | Hidden | Hidden | `403 Forbidden AccessDeniedView` |
| `/alerts` | Alert Center | Visible | Hidden | Visible | Visible *(Assigned)* | Shows alerts for assigned assets only |
| `/recommendations`| Recommendation Center | Visible | Visible | Hidden | Hidden | `403 Forbidden AccessDeniedView` |
| `/simulator` | What-if Simulator | Visible | Visible | Hidden | Hidden | `403 Forbidden AccessDeniedView` |
| `/reports` | Reports & Compliance | Visible | Visible | Hidden | Hidden | `403 Forbidden AccessDeniedView` |
| `/settings` | System Settings & Users | Visible | Hidden | Hidden | Hidden | `403 Forbidden AccessDeniedView` |

---

## 6. Operator Isolation Specifications

### Data Filtering Architecture
When a user with the `OPERATOR` role authenticates:
1. The backend inspects `user.assigned_machines` from the `user_machines` associative table.
2. If `user.roles` does NOT contain `PLANT_HEAD` or `MAINTENANCE_MANAGER`, the query automatically appends a filter:
   ```sql
   WHERE machine_id IN (SELECT machine_id FROM user_machines WHERE user_id = :current_user_id)
   ```
3. Direct lookups by ID (`/api/v1/machines/{machine_id}`) invoke `verify_machine_authorization()`:
   - If the requested `machine_id` is not present in `user.assigned_machine_ids`, FastAPI aborts execution immediately with:
     ```json
     {
       "detail": "Access denied: Machine 'furnace-01' is not assigned to your operator profile"
     }
     ```
     `HTTP 403 Forbidden`

### Concrete Seed Example: Lead Operator
- **Username**: `operator_lead`
- **Assigned Machinery**:
  - `air-compressor` (Code: `COMP-01`, Compressor Station A)
  - `cnc-machine` (Code: `CNC-01`, Precision Machining Cell 1)
- **Blocked Machinery** (Access yields HTTP 403 Forbidden):
  - `induction-furnace` (Code: `FURN-01`)
  - `cooling-tower` (Code: `TOWER-01`)
  - `boiler-system` (Code: `BOIL-01`)
  - `hydraulic-press` (Code: `PRESS-01`)
  - `exhaust-blower` (Code: `BLOW-01`)
  - `chiller-unit` (Code: `CHILL-01`)
  - `water-pump` (Code: `PUMP-01`)

---

## 7. Audit Trail Compliance Matrix

All state-modifying actions are logged to the `audit_logs` table with standard industrial compliance attributes:
- `timestamp`: UTC ISO 8601
- `user_id`: Reference to `users.id`
- `role`: Snapshot of role at time of action
- `action`: Standardized event code
- `ip_address`: Origin IPv4/IPv6 client address
- `details`: JSON payload documenting targeted resources or failure reasons

| Event Category | Action Identifier | Triggers | Logged Data Details |
|:---|:---|:---|:---|
| **Authentication** | `LOGIN_SUCCESS` | Valid password and account credentials | `{ "auth_method": "password", "token_type": "bearer" }` |
| **Authentication** | `LOGIN_FAILED` | Invalid password or unknown username | `{ "reason": "Invalid credentials", "attempted_username": "..." }` |
| **Authentication** | `LOGOUT` | Session revocation endpoint called | `{ "revoked_tokens": 1 }` |
| **Authentication** | `TOKEN_REFRESH` | Valid refresh token exchanged | `{ "token_family_rotated": true }` |
| **Governance** | `USER_CREATED` | New user registered by Plant Head | `{ "created_user_id": 5, "assigned_role": "OPERATOR" }` |
| **Operations** | `ALERT_ACKNOWLEDGED` | Alert state transitioned | `{ "alert_id": 12, "machine_id": "air-compressor" }` |
| **Operations** | `WORK_ORDER_CREATED`| Work order ticket scheduled | `{ "ticket_id": "WO-2026-08", "asset": "cnc-machine" }` |
| **Operations** | `RECOMMENDATION_APPROVED` | ECM action committed | `{ "ecm_id": 4, "projected_saving_kwh": 450.0 }` |
| **Security** | `ACCESS_DENIED` | Unauthorized machine or route accessed | `{ "endpoint": "/api/v1/machines/furnace-01", "code": 403 }` |

---

## 8. Verification & Test Evidence

The RBAC implementation is verified by dedicated automated test suites:

```bash
# Execute RBAC & Auth unit tests
pytest tests/test_auth_rbac.py -v

# Execute full system test suite (including all ML and AI components)
pytest -v

# Execute comprehensive route permission integration test
python test_routes.py

# Execute 23-endpoint full enterprise audit suite
python test_audit_suite.py
```

**Results**:
- `test_auth_rbac.py`: **12 / 12 Passed (100%)**
- Full `pytest`: **36 / 36 Passed (100%)**
- `test_routes.py`: **16 / 16 Passed (100%)**
- `test_audit_suite.py`: **23 / 23 Passed (100%)**
- TypeScript Compiler (`tsc --noEmit`): **0 Errors**
