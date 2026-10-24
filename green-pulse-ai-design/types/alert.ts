import type { Severity } from './common'

export type AlertStatus = 'open' | 'investigating' | 'acknowledged' | 'resolved'

export type AlertFilter = Severity | 'all'

export interface PlantAlert {
  id: string
  severity: Severity
  title: string
  machine: string
  occurredAt: string
  status: AlertStatus
}
