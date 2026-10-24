'use client'

import { Sparkles } from 'lucide-react'

import { Reveal } from '@/components/motion/reveal'
import { InsightCard } from '@/components/shared/insight-card'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { SectionHeader } from '@/components/shared/section-header'
import { Surface } from '@/components/shared/surface'
import { ToneBadge } from '@/components/shared/tone-badge'
import { useInsights } from '@/hooks/use-dashboard-data'
import { useSelectedPlant } from '@/hooks/use-workspace'
import { formatTimeOfDay } from '@/lib/format'

export function InsightsPanel() {
  const { data: feed } = useInsights()
  const plant = useSelectedPlant()

  if (!feed || !plant) return <LoadingPanel className="min-h-96" />

  return (
    <Surface className="flex h-full flex-col gap-5 p-5" aria-label="AI insights">
      <SectionHeader
        title="AI Insights"
        description={`${feed.engine} · generated at ${formatTimeOfDay(feed.generatedAt, plant.timezone)}`}
        icon={Sparkles}
        action={
          <ToneBadge tone="info" withDot={false}>
            {feed.insights.length} active
          </ToneBadge>
        }
      />
      <div className="grid grid-cols-1 gap-4 2xl:grid-cols-2">
        {feed.insights.map((insight, index) => (
          <Reveal key={insight.id} index={index} className="h-full">
            <InsightCard insight={insight} />
          </Reveal>
        ))}
      </div>
    </Surface>
  )
}
