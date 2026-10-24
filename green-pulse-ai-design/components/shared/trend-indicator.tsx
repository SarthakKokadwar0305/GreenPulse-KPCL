import { ArrowDownRight, ArrowUpRight, Minus } from 'lucide-react'

import { formatNumber } from '@/lib/format'
import { SENTIMENT_TONE, TONE_STYLES } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { Trend, TrendDirection } from '@/types'

const DIRECTION_ICON = {
  up: ArrowUpRight,
  down: ArrowDownRight,
  flat: Minus,
} satisfies Record<TrendDirection, unknown>

interface TrendIndicatorProps {
  trend: Trend
  className?: string
}

export function TrendIndicator({ trend, className }: TrendIndicatorProps) {
  const Icon = DIRECTION_ICON[trend.direction]
  const styles = TONE_STYLES[SENTIMENT_TONE[trend.sentiment]]

  return (
    <span className={cn('inline-flex items-center gap-2 text-xs', className)}>
      <span
        className={cn(
          'inline-flex items-center gap-0.5 rounded-md px-1.5 py-0.5 font-semibold tabular-nums',
          styles.soft,
          styles.text,
        )}
      >
        <Icon className="size-3.5" aria-hidden="true" />
        {formatNumber(Math.abs(trend.value), 1)}%
        <span className="sr-only">
          {trend.direction === 'flat' ? 'no change' : trend.direction}
        </span>
      </span>
      <span className="text-muted-foreground">{trend.comparison}</span>
    </span>
  )
}
