'use client'

import { Bell } from 'lucide-react'

import { StatusDot } from '@/components/shared/status-dot'
import { ModuleLink } from '@/components/shared/module-link'
import { buttonVariants } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from '@/components/ui/popover'
import { ROUTES } from '@/config/routes'
import { useAlerts } from '@/hooks/use-dashboard-data'
import { useSelectedPlant } from '@/hooks/use-workspace'
import { formatTimeOfDay } from '@/lib/format'
import { SEVERITY_TONE } from '@/lib/tone'
import { cn } from '@/lib/utils'

const MAX_VISIBLE_NOTIFICATIONS = 4

export function NotificationMenu() {
  const { data: alerts = [] } = useAlerts()
  const plant = useSelectedPlant()
  const timeZone = plant?.timezone ?? 'Asia/Kolkata'

  const unresolved = alerts.filter((alert) => alert.status !== 'resolved')
  const hasCritical = unresolved.some((alert) => alert.severity === 'critical')

  return (
    <Popover>
      <PopoverTrigger
        aria-label={`Notifications, ${unresolved.length} unresolved`}
        className={cn(
          buttonVariants({ variant: 'ghost', size: 'icon' }),
          'relative size-10 rounded-tile',
        )}
      >
        <Bell aria-hidden="true" />
        {unresolved.length > 0 && (
          <span
            className={cn(
              'absolute top-1.5 right-1.5 flex min-w-4 items-center justify-center rounded-full px-1 text-[10px] leading-4 font-semibold text-white ring-2 ring-background',
              hasCritical ? 'bg-danger' : 'bg-primary',
            )}
          >
            {unresolved.length}
          </span>
        )}
      </PopoverTrigger>
      <PopoverContent align="end" className="w-[360px] gap-0 p-0">
        <PopoverHeader className="border-b px-4 py-3">
          <PopoverTitle className="text-sm font-semibold">Notifications</PopoverTitle>
        </PopoverHeader>
        <ul className="flex max-h-80 flex-col overflow-y-auto py-1">
          {unresolved.slice(0, MAX_VISIBLE_NOTIFICATIONS).map((alert) => (
            <li
              key={alert.id}
              className="flex items-start gap-3 px-4 py-3 transition-colors hover:bg-muted/50"
            >
              <StatusDot
                tone={SEVERITY_TONE[alert.severity]}
                className="mt-1.5"
              />
              <div className="flex min-w-0 flex-1 flex-col gap-0.5">
                <p className="text-[13px] leading-5 font-medium text-foreground">
                  {alert.title}
                </p>
                <p className="text-xs text-muted-foreground">
                  {alert.machine} · {formatTimeOfDay(alert.occurredAt, timeZone)}
                </p>
              </div>
            </li>
          ))}
          {unresolved.length === 0 && (
            <li className="px-4 py-8 text-center text-sm text-muted-foreground">
              You are all caught up.
            </li>
          )}
        </ul>
        <div className="border-t p-2">
          <ModuleLink
            href={ROUTES.anomalyCenter}
            className="flex h-9 w-full items-center justify-center rounded-md text-[13px] font-medium text-primary transition-colors hover:bg-accent"
          >
            View all in Anomaly Center
          </ModuleLink>
        </div>
      </PopoverContent>
    </Popover>
  )
}
