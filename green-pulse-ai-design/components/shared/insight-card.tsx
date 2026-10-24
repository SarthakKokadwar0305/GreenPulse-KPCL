import { ArrowRight } from 'lucide-react'

import { buttonVariants } from '@/components/ui/button'
import { resolveIcon } from '@/lib/icons'
import { SEVERITY_LABEL } from '@/lib/status'
import { SEVERITY_TONE, TONE_STYLES } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { AiInsight } from '@/types'

import { IconTile } from './icon-tile'
import { MeterBar } from './meter-bar'
import { ModuleLink } from './module-link'
import { ToneBadge } from './tone-badge'

interface InsightCardProps {
  insight: AiInsight
}

export function InsightCard({ insight }: InsightCardProps) {
  const Icon = resolveIcon(insight.iconKey)
  const tone = SEVERITY_TONE[insight.severity]
  const styles = TONE_STYLES[tone]

  return (
    <article
      className={cn(
        'relative flex h-full flex-col gap-4 overflow-hidden rounded-tile border bg-card p-4 pl-5',
        'transition-shadow duration-200 hover:shadow-card-hover',
      )}
    >
      <span
        aria-hidden="true"
        className={cn('absolute inset-y-0 left-0 w-1', styles.dot)}
      />

      <header className="flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2.5">
          <IconTile icon={Icon} tone={tone} size="sm" />
          <span className="truncate text-xs font-medium text-muted-foreground">
            {insight.category}
          </span>
        </div>
        <ToneBadge tone={tone}>{SEVERITY_LABEL[insight.severity]}</ToneBadge>
      </header>

      <div className="flex flex-col gap-1.5">
        <h3 className="text-[15px] leading-snug font-semibold text-foreground">
          {insight.title}
        </h3>
        <p className="text-[13px] leading-relaxed text-muted-foreground">
          {insight.summary}
        </p>
      </div>

      <dl className="grid grid-cols-2 gap-x-4 gap-y-2.5 rounded-lg bg-muted/60 p-3">
        <dt className="col-span-2 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">
          Supporting evidence
        </dt>
        {insight.evidence.map((item) => (
          <div key={item.label} className="flex min-w-0 flex-col">
            <dd className="truncate text-sm font-semibold text-foreground tabular-nums">
              {item.value}
            </dd>
            <dt className="truncate text-xs text-muted-foreground">
              {item.label}
            </dt>
          </div>
        ))}
      </dl>

      <footer className="mt-auto flex items-center justify-between gap-4">
        <div className="flex w-28 flex-col gap-1.5">
          <span className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Confidence</span>
            <span className="font-semibold text-foreground tabular-nums">
              {insight.confidence}%
            </span>
          </span>
          <MeterBar
            value={insight.confidence}
            tone={tone}
            label={`${insight.title} confidence`}
          />
        </div>
        <ModuleLink
          href={insight.action.href}
          className={buttonVariants({ variant: 'outline', size: 'sm' })}
        >
          {insight.action.label}
          <ArrowRight data-icon="inline-end" aria-hidden="true" />
        </ModuleLink>
      </footer>
    </article>
  )
}
