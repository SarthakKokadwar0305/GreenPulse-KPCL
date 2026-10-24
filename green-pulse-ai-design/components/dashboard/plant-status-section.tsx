'use client'

import { Activity } from 'lucide-react'

import { Reveal } from '@/components/motion/reveal'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { SectionHeader } from '@/components/shared/section-header'
import { StatusCard } from '@/components/shared/status-card'
import { useDashboardOverview } from '@/hooks/use-dashboard-data'

const STATUS_PLACEHOLDER_COUNT = 8

export function PlantStatusSection() {
  const { data: overview } = useDashboardOverview()

  return (
    <section aria-label="Plant status" className="flex flex-col gap-4">
      <SectionHeader
        title="Plant Status"
        description="Operational snapshot across production, grid and sustainability."
        icon={Activity}
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {overview
          ? overview.plantStatus.map((metric, index) => (
              <Reveal key={metric.id} index={index} className="h-full">
                <StatusCard metric={metric} />
              </Reveal>
            ))
          : Array.from({ length: STATUS_PLACEHOLDER_COUNT }, (_, index) => (
              <LoadingPanel key={index} />
            ))}
      </div>
    </section>
  )
}
