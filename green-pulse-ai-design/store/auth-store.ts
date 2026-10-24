import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

export type EnterpriseRole =
  | 'PLANT_HEAD'
  | 'ENERGY_MANAGER'
  | 'MAINTENANCE_MANAGER'
  | 'OPERATOR'

export interface AuthUser {
  id: number
  name: string
  email: string
  username: string
  role: EnterpriseRole
  roleTitle: string
  initials: string
  department: string
  assignedMachines: string[]
  permissions: string[]
}

export const ENTERPRISE_PERSONAS: Record<EnterpriseRole, AuthUser> = {
  PLANT_HEAD: {
    id: 3,
    name: 'Rajesh Nair',
    email: 'plant.head@greenpulse.ai',
    username: 'plant_head',
    role: 'PLANT_HEAD',
    roleTitle: 'Plant Head',
    initials: 'RN',
    department: 'Executive Plant Management',
    assignedMachines: [
      'COMP-01',
      'COMP-02',
      'CNC-01',
      'CNC-02',
      'FURN-01',
      'HVAC-01',
      'PAINT-01',
      'PUMP-01',
      'ASSY-01',
    ],
    permissions: [
      'VIEW_DASHBOARD',
      'VIEW_PLANT',
      'VIEW_MACHINE',
      'VIEW_ASSIGNED_MACHINE',
      'VIEW_DIGITAL_TWIN',
      'VIEW_ENERGY',
      'VIEW_CARBON',
      'VIEW_FORECAST',
      'VIEW_ALERTS',
      'VIEW_RECOMMENDATIONS',
      'VIEW_SIMULATOR',
      'VIEW_REPORTS',
      'MANAGE_USERS',
      'CONFIGURE_THRESHOLDS',
      'ACKNOWLEDGE_ALERT',
      'UPDATE_MACHINE_STATUS',
      'SCHEDULE_MAINTENANCE',
      'APPROVE_MAINTENANCE',
      'EXPORT_REPORTS',
      'VIEW_AUDIT_LOGS',
      'APPROVE_RECOMMENDATIONS',
      'RUN_SIMULATION',
    ],
  },
  ENERGY_MANAGER: {
    id: 4,
    name: 'Vikram Patel',
    email: 'energy.manager@greenpulse.ai',
    username: 'energy_manager',
    role: 'ENERGY_MANAGER',
    roleTitle: 'Energy Manager',
    initials: 'VP',
    department: 'Energy & Sustainability',
    assignedMachines: [],
    permissions: [
      'VIEW_DASHBOARD',
      'VIEW_ENERGY',
      'VIEW_CARBON',
      'VIEW_FORECAST',
      'VIEW_RECOMMENDATIONS',
      'APPROVE_RECOMMENDATIONS',
      'VIEW_SIMULATOR',
      'RUN_SIMULATION',
      'VIEW_REPORTS',
      'EXPORT_REPORTS',
    ],
  },
  MAINTENANCE_MANAGER: {
    id: 5,
    name: 'Suresh Rao',
    email: 'maintenance.manager@greenpulse.ai',
    username: 'maintenance_manager',
    role: 'MAINTENANCE_MANAGER',
    roleTitle: 'Maintenance Manager',
    initials: 'SR',
    department: 'Reliability & Maintenance Engineering',
    assignedMachines: [
      'COMP-01',
      'COMP-02',
      'CNC-01',
      'CNC-02',
      'FURN-01',
      'HVAC-01',
      'PAINT-01',
      'PUMP-01',
      'ASSY-01',
    ],
    permissions: [
      'VIEW_DASHBOARD',
      'VIEW_MACHINE',
      'VIEW_DIGITAL_TWIN',
      'VIEW_ALERTS',
      'ACKNOWLEDGE_ALERT',
      'SCHEDULE_MAINTENANCE',
      'APPROVE_MAINTENANCE',
      'UPDATE_MACHINE_STATUS',
      'VIEW_RECOMMENDATIONS',
    ],
  },
  OPERATOR: {
    id: 6,
    name: 'Amit Shinde',
    email: 'operator1@greenpulse.ai',
    username: 'operator_lead',
    role: 'OPERATOR',
    roleTitle: 'Lead Machine Operator',
    initials: 'AS',
    department: 'Machining Bay Operations',
    assignedMachines: ['COMP-01', 'CNC-01'],
    permissions: [
      'VIEW_DASHBOARD',
      'VIEW_ASSIGNED_MACHINE',
      'VIEW_DIGITAL_TWIN',
      'VIEW_ALERTS',
      'ACKNOWLEDGE_ALERT',
      'UPDATE_MACHINE_STATUS',
    ],
  },
}

export const ROLE_ROUTE_ALLOWLIST: Record<EnterpriseRole, string[]> = {
  PLANT_HEAD: [
    '/',
    '/plant-overview',
    '/digital-twin',
    '/energy-explorer',
    '/carbon-accounting',
    '/ai-forecast-center',
    '/anomaly-center',
    '/recommendation-center',
    '/what-if-simulator',
    '/reports',
    '/settings',
    '/copilot',
  ],
  ENERGY_MANAGER: [
    '/',
    '/energy-explorer',
    '/carbon-accounting',
    '/ai-forecast-center',
    '/recommendation-center',
    '/what-if-simulator',
    '/reports',
    '/copilot',
  ],
  MAINTENANCE_MANAGER: [
    '/',
    '/digital-twin',
    '/anomaly-center',
    '/recommendation-center',
    '/copilot',
  ],
  OPERATOR: [
    '/',
    '/digital-twin',
    '/anomaly-center',
    '/copilot',
  ],
}

interface AuthState {
  user: AuthUser
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  setAuth: (user: AuthUser, accessToken?: string, refreshToken?: string) => void
  switchRole: (role: EnterpriseRole) => void
  logout: () => void
  canAccessRoute: (routePath: string) => boolean
  hasPermission: (permissionCode: string) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: ENTERPRISE_PERSONAS.PLANT_HEAD,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: true,
      setAuth: (user, accessToken, refreshToken) =>
        set({
          user,
          accessToken: accessToken ?? null,
          refreshToken: refreshToken ?? null,
          isAuthenticated: true,
        }),
      switchRole: (role: EnterpriseRole) => {
        const persona = ENTERPRISE_PERSONAS[role]
        set({ user: persona, isAuthenticated: true })
      },
      logout: () =>
        set({
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
      canAccessRoute: (routePath: string) => {
        const { user } = get()
        const allowed = ROLE_ROUTE_ALLOWLIST[user.role] ?? ['/']
        return allowed.includes(routePath)
      },
      hasPermission: (permissionCode: string) => {
        const { user } = get()
        return user.permissions.includes(permissionCode)
      },
    }),
    {
      name: 'greenpulse-auth-session',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
      skipHydration: true,
    },
  ),
)
