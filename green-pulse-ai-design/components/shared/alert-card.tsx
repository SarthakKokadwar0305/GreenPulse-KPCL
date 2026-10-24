import { AlertOctagon, AlertTriangle, Info, type LucideIcon } from 'lucide-react'

import { formatTimeOfDay } from '@/lib/format'
import { ALERT_STATUS_META } from '@/lib/status'
import { SEVERITY_TONE } from '@/lib/tone'
import type { PlantAlert, Severity } from '@/types'

import { IconTile } from './icon-tile'
import { ToneBadge } from './tone-badge'

const SEVERITY_ICON: Record<Severity, LucideIcon> = {
  critical: AlertOctagon,
  warning: AlertTriangle,
  info: Info,
}

const SEVERITY_LABEL: Record<Severity, string> = {
  critical: 'Critical',
  warning: 'Warning',
  info: 'Info',
}

interface AlertCardProps {
  alert: PlantAlert
  timeZone: string
}

export function AlertCard({ alert, timeZone }: AlertCardProps) {
  const tone = SEVERITY_TONE[alert.severity]
  const status = ALERT_STATUS_META[alert.status]

  return (
    <article className="flex items-start gap-3 rounded-tile border bg-card p-3.5 transition-colors hover:bg-muted/40">
      <IconTile icon={SEVERITY_ICON[alert.severity]} tone={tone} />
      <div className="flex min-w-0 flex-1 flex-col gap-2">
        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
          <h3 className="text-sm font-semibold text-foreground">{alert.title}</h3>
          <ToneBadge tone={tone} withDot={false}>
            {SEVERITY_LABEL[alert.severity]}
          </ToneBadge>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1.5 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="font-medium text-foreground/80">{alert.machine}</span>
            <span aria-hidden="true">·</span>
            <time dateTime={alert.occurredAt} className="tabular-nums">
              {formatTimeOfDay(alert.occurredAt, timeZone)}
            </time>
          </div>
          <ToneBadge tone={status.tone} className="h-5 px-2 text-[11px]">
            {status.label}
          </ToneBadge>
        </div>
      </div>
    </article>
  )
}
