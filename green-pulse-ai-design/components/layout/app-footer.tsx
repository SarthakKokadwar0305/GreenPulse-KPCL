'use client'

import { StatusDot } from '@/components/shared/status-dot'
import { Skeleton } from '@/components/ui/skeleton'
import { useSystemStatus } from '@/hooks/use-dashboard-data'
import { useSelectedPlant } from '@/hooks/use-workspace'
import { formatDateTimeStamp } from '@/lib/format'
import type { ServiceHealth } from '@/types'

interface FooterServiceProps {
  label: string
  health: ServiceHealth
}

function FooterService({ label, health }: FooterServiceProps) {
  return (
    <li className="flex items-center gap-2">
      <StatusDot tone={health.tone} />
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium text-foreground">{health.label}</span>
    </li>
  )
}

export function AppFooter() {
  const { data: system } = useSystemStatus()
  const plant = useSelectedPlant()

  return (
    <footer className="border-t bg-card/60 px-4 py-4 sm:px-6 lg:px-8">
      {system && plant ? (
        <div className="flex flex-col gap-3 text-xs md:flex-row md:items-center md:justify-between">
          <p className="font-medium text-foreground">
            GreenPulse AI
            <span className="ml-2 font-normal text-muted-foreground">
              v{system.version}
            </span>
          </p>
          <ul className="flex flex-wrap items-center gap-x-6 gap-y-2">
            <FooterService label="Backend" health={system.backend} />
            <FooterService label="AI Engine" health={system.aiEngine} />
            <li className="text-muted-foreground">
              Last sync{' '}
              <span className="font-medium text-foreground">
                {formatDateTimeStamp(system.lastSyncedAt, plant.timezone)}
              </span>
            </li>
          </ul>
        </div>
      ) : (
        <Skeleton className="h-5 w-full max-w-xl" />
      )}
    </footer>
  )
}
