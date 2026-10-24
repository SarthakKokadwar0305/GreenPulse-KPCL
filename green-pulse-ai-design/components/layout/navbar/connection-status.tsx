'use client'

import { ToneBadge } from '@/components/shared/tone-badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useSystemStatus } from '@/hooks/use-dashboard-data'

export function ConnectionStatus() {
  const { data: system } = useSystemStatus()

  if (!system) {
    return <Skeleton className="h-7 w-24 rounded-full" />
  }

  return (
    <ToneBadge
      tone={system.backend.tone}
      pulse={system.backend.tone === 'success'}
      className="h-7 px-2.5"
    >
      {system.backend.label}
      <span className="ml-1 hidden font-normal opacity-70 2xl:inline">
        {system.latencyMs} ms
      </span>
    </ToneBadge>
  )
}
