import type { Severity, Tone, TrendSentiment } from '@/types'

interface ToneStyle {
  text: string
  soft: string
  dot: string
  bar: string
  stroke: string
}

export const TONE_STYLES: Record<Tone, ToneStyle> = {
  success: {
    text: 'text-success',
    soft: 'bg-success/10',
    dot: 'bg-success',
    bar: 'bg-success',
    stroke: 'var(--success)',
  },
  warning: {
    text: 'text-warning-ink',
    soft: 'bg-warning/15',
    dot: 'bg-warning',
    bar: 'bg-warning',
    stroke: 'var(--warning)',
  },
  danger: {
    text: 'text-danger',
    soft: 'bg-danger/10',
    dot: 'bg-danger',
    bar: 'bg-danger',
    stroke: 'var(--danger)',
  },
  info: {
    text: 'text-primary',
    soft: 'bg-primary/10',
    dot: 'bg-primary',
    bar: 'bg-primary',
    stroke: 'var(--primary)',
  },
  neutral: {
    text: 'text-steel',
    soft: 'bg-steel/10',
    dot: 'bg-steel',
    bar: 'bg-steel',
    stroke: 'var(--steel)',
  },
}

export const SEVERITY_TONE: Record<Severity | 'success', Tone> = {
  critical: 'danger',
  warning: 'warning',
  info: 'info',
  success: 'success',
}

export const SENTIMENT_TONE: Record<TrendSentiment, Tone> = {
  positive: 'success',
  negative: 'danger',
  neutral: 'neutral',
}

export function getScoreTone(score: number): Tone {
  if (score >= 85) return 'success'
  if (score >= 70) return 'warning'
  return 'danger'
}
