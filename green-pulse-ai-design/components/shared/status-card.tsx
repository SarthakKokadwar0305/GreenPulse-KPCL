import { resolveIcon } from '@/lib/icons'
import { TONE_STYLES } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { PlantStatusMetric } from '@/types'

import { IconTile } from './icon-tile'
import { MeterBar } from './meter-bar'
import { Surface } from './surface'

interface StatusCardProps {
  metric: PlantStatusMetric
}

export function StatusCard({ metric }: StatusCardProps) {
  const Icon = resolveIcon(metric.iconKey)

  return (
    <Surface className="flex h-full flex-col gap-3 p-4">
      <div className="flex items-center gap-3">
        <IconTile icon={Icon} tone={metric.tone} size="sm" />
        <h3 className="truncate text-[13px] font-medium text-muted-foreground">
          {metric.title}
        </h3>
      </div>
      <p
        className={cn(
          'text-xl leading-7 font-semibold tracking-tight tabular-nums',
          metric.tone === 'neutral' ? 'text-foreground' : TONE_STYLES[metric.tone].text,
        )}
      >
        {metric.value}
      </p>
      {metric.progress !== undefined && (
        <MeterBar
          value={metric.progress}
          tone={metric.tone}
          label={metric.title}
        />
      )}
      <p className="text-xs text-muted-foreground">{metric.caption}</p>
    </Surface>
  )
}
