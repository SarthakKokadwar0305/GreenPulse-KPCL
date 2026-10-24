'use client'

import { useId } from 'react'
import { Area, AreaChart, YAxis } from 'recharts'

import { ChartContainer, type ChartConfig } from '@/components/ui/chart'
import { TONE_STYLES } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { Tone } from '@/types'

interface SparklineProps {
  data: number[]
  tone?: Tone
  label?: string
  className?: string
}

export function Sparkline({
  data,
  tone = 'info',
  label = 'Trend',
  className,
}: SparklineProps) {
  const gradientId = `spark-${useId().replace(/:/g, '')}`
  const points = data.map((value, index) => ({ index, value }))
  const config = {
    value: { label, color: TONE_STYLES[tone].stroke },
  } satisfies ChartConfig

  return (
    <ChartContainer
      config={config}
      initialDimension={{ width: 112, height: 48 }}
      className={cn('aspect-auto h-12 w-28 justify-start', className)}
    >
      <AreaChart data={points} margin={{ top: 4, right: 2, bottom: 2, left: 2 }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--color-value)" stopOpacity={0.3} />
            <stop offset="100%" stopColor="var(--color-value)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <YAxis hide domain={['dataMin', 'dataMax']} />
        <Area
          dataKey="value"
          type="monotone"
          stroke="var(--color-value)"
          strokeWidth={1.75}
          fill={`url(#${gradientId})`}
          dot={false}
          activeDot={false}
        />
      </AreaChart>
    </ChartContainer>
  )
}
