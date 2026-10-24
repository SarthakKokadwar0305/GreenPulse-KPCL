import type {
  IconKey,
  ServiceHealth,
  StatusIndicator,
  Tone,
  Trend,
} from './common'

export interface KpiMetric {
  id: string
  title: string
  value: number
  decimals?: number
  prefix?: string
  unit?: string
  iconKey: IconKey
  trend: Trend
  status: StatusIndicator
  description: string
  sparkline: number[]
}

export interface PlantStatusMetric {
  id: string
  title: string
  value: string
  caption: string
  iconKey: IconKey
  tone: Tone
  progress?: number
}

export interface EnergyTrendPoint {
  label: string
  actual: number | null
  baseline: number
  forecast: number | null
}

export type EnergyTrendRange = 'today' | 'week'

export interface QuickActionItem {
  id: string
  title: string
  description: string
  iconKey: IconKey
  href: string
}

export interface SystemStatus {
  version: string
  backend: ServiceHealth
  aiEngine: ServiceHealth
  lastSyncedAt: string
  latencyMs: number
}

export interface DashboardOverview {
  kpis: KpiMetric[]
  plantStatus: PlantStatusMetric[]
  energyTrend: Record<EnergyTrendRange, EnergyTrendPoint[]>
  quickActions: QuickActionItem[]
  system: SystemStatus
}
