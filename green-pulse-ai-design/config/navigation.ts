import {
  BarChart3,
  Boxes,
  BrainCircuit,
  FileText,
  FlaskConical,
  Lightbulb,
  Factory,
  LayoutDashboard,
  Leaf,
  Settings,
  Siren,
  Sparkles,
} from 'lucide-react'

import type { NavItem } from '@/types'

import { isRouteEnabled, ROUTES } from './routes'

type NavItemDefinition = Omit<NavItem, 'enabled'>

const NAV_DEFINITIONS: NavItemDefinition[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    href: ROUTES.dashboard,
    icon: LayoutDashboard,
    breadcrumb: ['Dashboard', 'Home'],
  },
  {
    id: 'plant-overview',
    label: 'Plant Overview',
    href: ROUTES.plantOverview,
    icon: Factory,
  },
  {
    id: 'digital-twin',
    label: 'Digital Twin',
    href: ROUTES.digitalTwin,
    icon: Boxes,
  },
  {
    id: 'energy-explorer',
    label: 'Energy Explorer',
    href: ROUTES.energyExplorer,
    icon: BarChart3,
  },
  {
    id: 'carbon-accounting',
    label: 'Carbon Accounting',
    href: ROUTES.carbonAccounting,
    icon: Leaf,
  },
  {
    id: 'ai-forecast-center',
    label: 'AI Forecast Center',
    href: ROUTES.aiForecastCenter,
    icon: BrainCircuit,
  },
  {
    id: 'anomaly-center',
    label: 'Anomaly Center',
    href: ROUTES.anomalyCenter,
    icon: Siren,
  },
  {
    id: 'recommendation-center',
    label: 'Recommendation Center',
    href: ROUTES.recommendationCenter,
    icon: Lightbulb,
  },
  {
    id: 'copilot',
    label: 'AI Copilot (RAG)',
    href: ROUTES.copilot,
    icon: Sparkles,
    breadcrumb: ['Intelligence', 'AI Copilot'],
  },
  {
    id: 'what-if-simulator',
    label: 'What-if Simulator',
    href: ROUTES.whatIfSimulator,
    icon: FlaskConical,
  },
  {
    id: 'reports',
    label: 'Reports',
    href: ROUTES.reports,
    icon: FileText,
  },
  {
    id: 'settings',
    label: 'Settings',
    href: ROUTES.settings,
    icon: Settings,
  },
]

export const NAV_ITEMS: NavItem[] = NAV_DEFINITIONS.map((item) => ({
  ...item,
  enabled: isRouteEnabled(item.href),
}))

export function getNavItemByPath(pathname: string) {
  return NAV_ITEMS.find((item) => item.href === pathname)
}

export function getBreadcrumb(pathname: string) {
  const item = getNavItemByPath(pathname)
  if (!item) return ['Dashboard', 'Home']
  return item.breadcrumb ?? ['GreenPulse AI', item.label]
}
