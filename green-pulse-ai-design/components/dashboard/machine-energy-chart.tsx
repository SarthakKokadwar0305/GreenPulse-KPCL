'use client'

import { BarChart3 } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from 'recharts'

import { ChartPanel } from '@/components/shared/chart-container'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { ToneBadge } from '@/components/shared/tone-badge'
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { useMachineEnergyComparison } from '@/hooks/use-dashboard-data'
import { formatNumber } from '@/lib/format'

const chartConfig = {
  actual: { label: 'Actual', color: 'var(--chart-1)' },
  target: { label: 'Target', color: 'var(--chart-2)' },
} satisfies ChartConfig

export function MachineEnergyChart() {
  const { data: comparison } = useMachineEnergyComparison()

  if (!comparison) return <LoadingPanel className="min-h-96" />

  const overTarget = comparison.filter((item) => item.actual > item.target)

  return (
    <ChartPanel
      title="Machine Energy Comparison"
      description="Energy consumed today against assigned target, in kWh."
      icon={BarChart3}
      footer={
        <ToneBadge tone={overTarget.length > 0 ? 'warning' : 'success'}>
          {overTarget.length > 0
            ? `${overTarget.map((item) => item.machine).join(', ')} above target`
            : 'All machines within target'}
        </ToneBadge>
      }
    >
      <ChartContainer config={chartConfig} className="aspect-auto h-72 w-full">
        <BarChart
          data={comparison}
          margin={{ left: 4, right: 4, top: 8 }}
          barGap={4}
        >
          <CartesianGrid vertical={false} strokeDasharray="3 3" />
          <XAxis
            dataKey="machine"
            tickLine={false}
            axisLine={false}
            tickMargin={10}
            interval={0}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            width={44}
            tickFormatter={(value: number) => formatNumber(value)}
          />
          <ChartTooltip
            cursor={{ fill: 'var(--muted)', opacity: 0.6 }}
            content={<ChartTooltipContent indicator="dot" />}
          />
          <ChartLegend content={<ChartLegendContent />} />
          <Bar
            dataKey="actual"
            fill="var(--color-actual)"
            radius={[5, 5, 0, 0]}
            maxBarSize={22}
          />
          <Bar
            dataKey="target"
            fill="var(--color-target)"
            radius={[5, 5, 0, 0]}
            maxBarSize={22}
          />
        </BarChart>
      </ChartContainer>
    </ChartPanel>
  )
}
