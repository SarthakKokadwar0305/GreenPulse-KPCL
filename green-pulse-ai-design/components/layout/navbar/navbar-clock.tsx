'use client'

import { CalendarDays, Clock } from 'lucide-react'

import { Skeleton } from '@/components/ui/skeleton'
import { useClock } from '@/hooks/use-clock'
import { useSelectedPlant } from '@/hooks/use-workspace'
import { formatClockTime, formatShortDate } from '@/lib/format'

export function NavbarClock() {
  const now = useClock()
  const plant = useSelectedPlant()

  if (!now || !plant) {
    return <Skeleton className="h-10 w-48 rounded-tile" />
  }

  return (
    <div
      className="flex items-center gap-4 text-[13px] text-muted-foreground"
      aria-label="Plant local date and time"
    >
      <span className="flex items-center gap-1.5">
        <CalendarDays className="size-4" aria-hidden="true" />
        <time dateTime={now.toISOString()} className="font-medium text-foreground">
          {formatShortDate(now, plant.timezone)}
        </time>
      </span>
      <span className="flex items-center gap-1.5">
        <Clock className="size-4" aria-hidden="true" />
        <time
          dateTime={now.toISOString()}
          className="font-semibold text-foreground tabular-nums"
        >
          {formatClockTime(now, plant.timezone, true)}
        </time>
      </span>
    </div>
  )
}
