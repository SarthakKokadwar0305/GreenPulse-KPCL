export type Tone = 'success' | 'warning' | 'danger' | 'info' | 'neutral'

export type Severity = 'critical' | 'warning' | 'info'

export type TrendDirection = 'up' | 'down' | 'flat'

export type TrendSentiment = 'positive' | 'negative' | 'neutral'

export interface Trend {
  value: number
  direction: TrendDirection
  sentiment: TrendSentiment
  comparison: string
}

export interface StatusIndicator {
  tone: Tone
  label: string
}

export interface ServiceHealth {
  tone: Tone
  label: string
  detail: string
}

export type IconKey = string
