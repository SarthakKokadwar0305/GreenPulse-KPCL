'use client'

import { TrendingUp } from 'lucide-react'
import { useState } from 'react'
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from 'recharts'

import { ChartPanel } from '@/components/shared/chart-container'
import { LoadingPanel } from '@/components/shared/loading-panel'
import {
  SegmentedControl,
  type SegmentedOption,
} from '@/components/shared/segmented-control'
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { useDashboardOverview } from '@/hooks/use-dashboard-data'
import { formatNumber } from '@/lib/format'
import type { EnergyTrendRange } from '@/types'

const chartConfig = {
  actual: { label: 'Actual', color: 'var(--chart-1)' },
  baseline: { label: 'Baseline', color: 'var(--chart-2)' },
  forecast: { label: 'AI forecast', color: 'var(--chart-3)' },
} satisfies ChartConfig

const RANGE_OPTIONS: SegmentedOption<EnergyTrendRange>[] = [
  { value: 'today', label: 'Today' },
  { value: 'week', label: '7 days' },
]

const RANGE_DESCRIPTION: Record<EnergyTrendRange, string> = {
  today: 'Hourly consumption in kWh against baseline and AI forecast.',
  week: 'Daily consumption in kWh over the last seven days.',
}

export function EnergyTrendChart() {
  const { data: overview } = useDashboardOverview()
  const [range, setRange] = useState<EnergyTrendRange>('today')

  if (!overview) return <LoadingPanel className="min-h-96" />

  const points = overview.energyTrend[range]
  const hasForecast = points.some((point) => point.forecast !== null)

  return (
    <ChartPanel
      title="Daily Energy Consumption"
      description={RANGE_DESCRIPTION[range]}
      icon={TrendingUp}
      action={
        <SegmentedControl
          ariaLabel="Energy chart range"
          value={range}
          options={RANGE_OPTIONS}
          onChange={setRange}
        />
      }
    >
      <ChartContainer config={chartConfig} className="aspect-auto h-72 w-full">
        <LineChart data={points} margin={{ left: 4, right: 12, top: 8 }}>
          <CartesianGrid vertical={false} strokeDasharray="3 3" />
          <XAxis
            dataKey="label"
            tickLine={false}
            axisLine={false}
            tickMargin={10}
            minTickGap={28}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={(value: number) => formatNumber(value)}
          />
          <ChartTooltip
            cursor={false}
            content={
              <ChartTooltipContent
                indicator="line"
                formatter={(value, name) => (
                  <div className="flex w-full items-center justify-between gap-6">
                    <span className="text-muted-foreground">
                      {chartConfig[name as keyof typeof chartConfig]?.label}
                    </span>
                    <span className="font-semibold tabular-nums">
                      {formatNumber(Number(value))} kWh
                    </span>
                  </div>
                )}
              />
            }
          />
          <ChartLegend content={<ChartLegendContent />} />
          <Line
            dataKey="baseline"
            type="monotone"
            stroke="var(--color-baseline)"
            strokeWidth={1.75}
            strokeDasharray="5 4"
            dot={false}
          />
          {hasForecast && (
            <Line
              dataKey="forecast"
              type="monotone"
              stroke="var(--color-forecast)"
              strokeWidth={2}
              strokeDasharray="2 4"
              strokeLinecap="round"
              dot={false}
              connectNulls={false}
            />
          )}
          <Line
            dataKey="actual"
            type="monotone"
            stroke="var(--color-actual)"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 5 }}
            connectNulls={false}
          />
        </LineChart>
      </ChartContainer>
    </ChartPanel>
  )
}
