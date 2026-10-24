'use client'

import { Zap } from 'lucide-react'

import { Reveal } from '@/components/motion/reveal'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { QuickActionCard } from '@/components/shared/quick-action-card'
import { SectionHeader } from '@/components/shared/section-header'
import { useDashboardOverview } from '@/hooks/use-dashboard-data'

const ACTION_PLACEHOLDER_COUNT = 5

export function QuickActionsSection() {
  const { data: overview } = useDashboardOverview()

  return (
    <section aria-label="Quick actions" className="flex flex-col gap-4">
      <SectionHeader
        title="Quick Actions"
        description="Jump straight into the most common workflows."
        icon={Zap}
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {overview
          ? overview.quickActions.map((action, index) => (
              <Reveal key={action.id} index={index} className="h-full">
                <QuickActionCard action={action} />
              </Reveal>
            ))
          : Array.from({ length: ACTION_PLACEHOLDER_COUNT }, (_, index) => (
              <LoadingPanel key={index} className="min-h-28" />
            ))}
      </div>
    </section>
  )
}
