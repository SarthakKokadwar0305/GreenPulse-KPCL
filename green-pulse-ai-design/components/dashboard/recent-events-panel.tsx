'use client'

import { History } from 'lucide-react'

import { LoadingPanel } from '@/components/shared/loading-panel'
import { SectionHeader } from '@/components/shared/section-header'
import { Surface } from '@/components/shared/surface'
import { Timeline } from '@/components/shared/timeline'
import { useTimeline } from '@/hooks/use-dashboard-data'
import { useSelectedPlant } from '@/hooks/use-workspace'

export function RecentEventsPanel() {
  const { data: events } = useTimeline()
  const plant = useSelectedPlant()

  if (!events || !plant) return <LoadingPanel className="min-h-96" />

  return (
    <Surface className="flex h-full flex-col gap-5 p-5" aria-label="Recent events">
      <SectionHeader
        title="Recent Events"
        description="Chronological activity across the plant today."
        icon={History}
      />
      <Timeline events={events} timeZone={plant.timezone} />
    </Surface>
  )
}
