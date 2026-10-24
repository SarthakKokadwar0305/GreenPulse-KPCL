import { resolveIcon } from '@/lib/icons'
import type { KpiMetric } from '@/types'

import { AnimatedNumber } from './animated-number'
import { IconTile } from './icon-tile'
import { Sparkline } from './sparkline'
import { Surface } from './surface'
import { ToneBadge } from './tone-badge'
import { TrendIndicator } from './trend-indicator'

interface KpiCardProps {
  metric: KpiMetric
}

export function KpiCard({ metric }: KpiCardProps) {
  const Icon = resolveIcon(metric.iconKey)

  return (
    <Surface interactive className="flex h-full flex-col gap-4 p-5">
      <div className="flex items-center justify-between gap-3">
        <IconTile icon={Icon} tone={metric.status.tone} />
        <ToneBadge
          tone={metric.status.tone}
          pulse={metric.status.tone === 'danger'}
        >
          {metric.status.label}
        </ToneBadge>
      </div>

      <div className="flex flex-col gap-1">
        <h3 className="text-[13px] font-medium text-muted-foreground">
          {metric.title}
        </h3>
        <div className="flex items-end justify-between gap-3">
          <p className="flex items-baseline gap-1.5 text-[28px] leading-9 font-semibold tracking-tight text-foreground tabular-nums">
            <span>
              {metric.prefix}
              <AnimatedNumber value={metric.value} decimals={metric.decimals} />
            </span>
            {metric.unit && (
              <span className="text-sm font-medium text-muted-foreground">
                {metric.unit}
              </span>
            )}
          </p>
          <Sparkline
            data={metric.sparkline}
            tone={metric.status.tone}
            label={metric.title}
            className="w-24 shrink-0"
          />
        </div>
      </div>

      <div className="mt-auto flex flex-col gap-2 border-t pt-3">
        <TrendIndicator trend={metric.trend} />
        <p className="text-xs text-muted-foreground">{metric.description}</p>
      </div>
    </Surface>
  )
}
