import type { IconKey, Tone } from './common'

export interface TimelineEvent {
  id: string
  time: string
  title: string
  description: string
  iconKey: IconKey
  tone: Tone
  source: string
}
