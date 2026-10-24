'use client'

import { Clock3, MapPin, UsersRound } from 'lucide-react'

import { PageHeader } from '@/components/shared/page-header'
import { ToneBadge } from '@/components/shared/tone-badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useClock } from '@/hooks/use-clock'
import { useSelectedPlant } from '@/hooks/use-workspace'
import { getGreeting } from '@/lib/format'

export function DashboardHeader() {
  const now = useClock(60_000)
  const plant = useSelectedPlant()

  if (!plant) {
    return (
      <div className="flex flex-col gap-3">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-9 w-80 max-w-full" />
        <Skeleton className="h-4 w-96 max-w-full" />
      </div>
    )
  }

  return (
    <PageHeader
      eyebrow={now ? `${getGreeting(now, plant.timezone)},` : 'Welcome,'}
      title={plant.name}
      description="Monitor energy usage, detect anomalies and optimize sustainability."
      meta={
        <>
          <ToneBadge tone="neutral" withDot={false}>
            <MapPin className="size-3" aria-hidden="true" />
            {plant.location}
          </ToneBadge>
          <ToneBadge tone="info" withDot={false}>
            <UsersRound className="size-3" aria-hidden="true" />
            {plant.currentShift}
          </ToneBadge>
          <ToneBadge tone="success" pulse>
            <Clock3 className="size-3" aria-hidden="true" />
            Live data
          </ToneBadge>
        </>
      }
    />
  )
}
