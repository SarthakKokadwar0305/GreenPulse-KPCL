export const ROUTES = {
  dashboard: '/',
  plantOverview: '/plant-overview',
  digitalTwin: '/digital-twin',
  energyExplorer: '/energy-explorer',
  carbonAccounting: '/carbon-accounting',
  aiForecastCenter: '/ai-forecast-center',
  anomalyCenter: '/anomaly-center',
  recommendationCenter: '/recommendation-center',
  whatIfSimulator: '/what-if-simulator',
  reports: '/reports',
  settings: '/settings',
  copilot: '/copilot',
} as const

export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES]

/**
 * Modules shipped in the current phase. To launch a future module, add its
 * `app/(platform)/<segment>/page.tsx` and list its path here.
 */
export const ENABLED_ROUTES: ReadonlySet<string> = new Set<RoutePath>([
  ROUTES.dashboard,
  ROUTES.plantOverview,
  ROUTES.digitalTwin,
  ROUTES.energyExplorer,
  ROUTES.carbonAccounting,
  ROUTES.aiForecastCenter,
  ROUTES.anomalyCenter,
  ROUTES.recommendationCenter,
  ROUTES.whatIfSimulator,
  ROUTES.reports,
  ROUTES.settings,
  ROUTES.copilot,
])

export function isRouteEnabled(href: string) {
  return ENABLED_ROUTES.has(href)
}
