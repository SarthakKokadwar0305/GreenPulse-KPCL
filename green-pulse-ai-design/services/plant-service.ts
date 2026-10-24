import type {
  DashboardOverview,
  InsightsFeed,
  Machine,
  PlantAlert,
  TimelineEvent,
  Workspace,
  PlantOverviewData,
  MachineTelemetry,
  EnergyExplorerData,
  CarbonAccountingData,
  AiForecastData,
  AnomalyIncident,
  AiRecommendation,
  SimulationBaseline,
  IndustrialReport,
  ScheduledReportConfig,
  PlantSettings,
  UserProfileSettings,
  NotificationThresholds,
  ApiConfiguration,
  AuditLogEntry,
} from '@/types'

import { fetchResource } from './api-client'

export function getWorkspace() {
  return fetchResource<Workspace>('/workspace', () => import('@/data/workspace.json'))
}

export function getDashboardOverview(plantId: string) {
  return fetchResource<DashboardOverview>(
    `/plants/${plantId}/dashboard`,
    () => import('@/data/dashboard.json'),
  )
}

export function getMachines(plantId: string) {
  return fetchResource<Machine[]>(
    `/plants/${plantId}/machines`,
    () => import('@/data/machines.json'),
  )
}

export function getAlerts(plantId: string) {
  return fetchResource<PlantAlert[]>(
    `/plants/${plantId}/alerts`,
    () => import('@/data/alerts.json'),
  )
}

export function getInsights(plantId: string) {
  return fetchResource<InsightsFeed>(
    `/plants/${plantId}/insights`,
    () => import('@/data/insights.json'),
  )
}

export function getTimeline(plantId: string) {
  return fetchResource<TimelineEvent[]>(
    `/plants/${plantId}/timeline`,
    () => import('@/data/timeline.json'),
  )
}

export function getPlantOverview(plantId: string) {
  return fetchResource<PlantOverviewData>(
    `/plants/${plantId}/overview`,
    () => import('@/data/plant-overview.json'),
  )
}

export function getDigitalTwin(plantId: string) {
  return fetchResource<MachineTelemetry[]>(
    `/plants/${plantId}/digital-twin`,
    () => import('@/data/digital-twin.json'),
  )
}

export function getEnergyExplorer(plantId: string) {
  return fetchResource<EnergyExplorerData>(
    `/plants/${plantId}/energy-explorer`,
    () => import('@/data/energy-explorer.json'),
  )
}

export function getCarbonAccounting(plantId: string) {
  return fetchResource<CarbonAccountingData>(
    `/plants/${plantId}/carbon-accounting`,
    () => import('@/data/carbon-accounting.json'),
  )
}

export function getAiForecast(plantId: string) {
  return fetchResource<AiForecastData>(
    `/plants/${plantId}/ai-forecast`,
    () => import('@/data/ai-forecast.json'),
  )
}

export function getAnomalies(plantId: string) {
  return fetchResource<AnomalyIncident[]>(
    `/plants/${plantId}/anomalies`,
    () => import('@/data/anomalies.json'),
  )
}

export function getRecommendations(plantId: string) {
  return fetchResource<AiRecommendation[]>(
    `/plants/${plantId}/recommendations`,
    () => import('@/data/recommendations.json'),
  )
}

export function getSimulatorBaseline(plantId: string) {
  return fetchResource<SimulationBaseline>(
    `/plants/${plantId}/simulator`,
    () => import('@/data/simulator.json'),
  )
}

export function getReportsData(plantId: string) {
  return fetchResource<{ recentReports: IndustrialReport[]; scheduledReports: ScheduledReportConfig[] }>(
    `/plants/${plantId}/reports`,
    () => import('@/data/reports.json'),
  )
}

export function getSettingsData(plantId: string) {
  return fetchResource<{
    plant: PlantSettings
    profile: UserProfileSettings
    notifications: NotificationThresholds
    security: { twoFactorRequired: boolean; sessionTimeoutMinutes: number; passwordExpiryDays: number; ipWhitelist: string[]; singleSignOnProvider: string; encryptionStandard: string }
    api: ApiConfiguration
    users: { id: string; name: string; email: string; role: string; department: string; status: string; lastActive: string }[]
    auditLogs: AuditLogEntry[]
  }>(
    `/plants/${plantId}/settings`,
    () => import('@/data/settings.json'),
  )
}

