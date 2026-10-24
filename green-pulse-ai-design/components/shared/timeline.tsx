import { formatTimeOfDay } from '@/lib/format'
import { resolveIcon } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type { TimelineEvent } from '@/types'

import { IconTile } from './icon-tile'

interface TimelineProps {
  events: TimelineEvent[]
  timeZone: string
}

export function Timeline({ events, timeZone }: TimelineProps) {
  return (
    <ol className="flex flex-col">
      {events.map((event, index) => {
        const Icon = resolveIcon(event.iconKey)
        const isLast = index === events.length - 1

        return (
          <li key={event.id} className="grid grid-cols-[3rem_2rem_1fr] gap-x-3">
            <time
              dateTime={event.time}
              className="pt-1.5 text-right text-xs font-semibold text-muted-foreground tabular-nums"
            >
              {formatTimeOfDay(event.time, timeZone)}
            </time>
            <div className="flex flex-col items-center">
              <IconTile icon={Icon} tone={event.tone} size="sm" className="size-8 rounded-full" />
              {!isLast && (
                <span
                  aria-hidden="true"
                  className="min-h-4 w-px flex-1 bg-border"
                />
              )}
            </div>
            <div className={cn('flex min-w-0 flex-col gap-0.5 pt-1', !isLast && 'pb-5')}>
              <p className="text-sm font-semibold text-foreground">{event.title}</p>
              <p className="text-[13px] text-muted-foreground">{event.description}</p>
              <p className="text-[11px] font-medium text-muted-foreground/80">
                {event.source}
              </p>
            </div>
          </li>
        )
      })}
    </ol>
  )
}
