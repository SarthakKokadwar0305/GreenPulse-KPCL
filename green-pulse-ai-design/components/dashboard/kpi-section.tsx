'use client'

import { Reveal } from '@/components/motion/reveal'
import { KpiCard } from '@/components/shared/kpi-card'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { useDashboardOverview } from '@/hooks/use-dashboard-data'

const KPI_PLACEHOLDER_COUNT = 8

export function KpiSection() {
  const { data: overview } = useDashboardOverview()

  return (
    <section
      aria-label="Key performance indicators"
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
    >
      {overview
        ? overview.kpis.map((metric, index) => (
            <Reveal key={metric.id} index={index} className="h-full">
              <KpiCard metric={metric} />
            </Reveal>
          ))
        : Array.from({ length: KPI_PLACEHOLDER_COUNT }, (_, index) => (
            <LoadingPanel key={index} className="min-h-48" />
          ))}
    </section>
  )
}
