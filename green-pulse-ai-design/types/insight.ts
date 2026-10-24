import type { IconKey } from './common'

export type InsightSeverity = 'critical' | 'warning' | 'info' | 'success'

export interface InsightEvidence {
  label: string
  value: string
}

export interface InsightAction {
  label: string
  href: string
}

export interface AiInsight {
  id: string
  category: string
  iconKey: IconKey
  severity: InsightSeverity
  title: string
  summary: string
  confidence: number
  evidence: InsightEvidence[]
  action: InsightAction
}

export interface InsightsFeed {
  engine: string
  generatedAt: string
  insights: AiInsight[]
}
