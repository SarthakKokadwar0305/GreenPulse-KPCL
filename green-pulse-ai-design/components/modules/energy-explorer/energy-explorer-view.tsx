'use client'

import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Calendar,
  Clock,
  Cpu,
  Download,
  Filter,
  Flame,
  Layers,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Zap,
} from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { Reveal } from '@/components/motion/reveal'
import { AnimatedNumber } from '@/components/shared/animated-number'
import { IconTile } from '@/components/shared/icon-tile'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { MeterBar } from '@/components/shared/meter-bar'
import { PageHeader } from '@/components/shared/page-header'
import { SectionHeader } from '@/components/shared/section-header'
import { SegmentedControl } from '@/components/shared/segmented-control'
import { Surface } from '@/components/shared/surface'
import { ToneBadge } from '@/components/shared/tone-badge'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { useEnergyExplorerData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'
import { exportToCsv } from '@/lib/export-utils'

const hourlyChartConfig = {
  actualKw: { label: 'Active Load (kW)', color: 'var(--chart-1)' },
  baselineKw: { label: 'Baseline (kW)', color: 'var(--chart-2)' },
} satisfies ChartConfig

const dailyChartConfig = {
  energyKwh: { label: 'Energy Consumed (kWh)', color: 'var(--chart-1)' },
  targetKwh: { label: 'Energy Target (kWh)', color: 'var(--chart-3)' },
} satisfies ChartConfig

export function EnergyExplorerView() {
  const { data, isLoading, isError, refetch } = useEnergyExplorerData()
  const [timeView, setTimeView] = useState<'hourly' | 'daily' | 'weekly' | 'monthly'>('hourly')
  const [metricType, setMetricType] = useState<'active' | 'apparent' | 'power-factor'>('active')
  const [selectedDeptFilter, setSelectedDeptFilter] = useState<string>('all')

  if (isLoading) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Energy Analytics"
          title="Energy Explorer"
          description="Detailed multi-resolution industrial energy telemetry, peak demand, and consumption heatmaps."
        />
        <LoadingPanel className="min-h-96" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <Surface className="flex min-h-96 flex-col items-center justify-center gap-4 p-8 text-center">
        <AlertTriangle className="size-12 text-destructive" />
        <h2 className="text-xl font-semibold text-foreground">Failed to Load Energy Analytics</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Historical energy time-series datastore could not be queried.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Retry Query
        </Button>
      </Surface>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="Energy Intelligence"
        title="Energy Explorer"
        description="Detailed multi-dimensional electrical load profiling, peak demand tracking, machine energy intensity, and 24x7 consumption heatmaps."
        meta={
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Contract Peak Limit: <strong className="text-foreground">{data.contractedPeakLimitKw} kW</strong></span>
            <span>•</span>
            <span>Headroom: <strong className="text-success">{data.peakHeadroomKw} kW</strong></span>
            <span>•</span>
            <span>Est. Daily Cost: <strong className="text-foreground">₹{formatNumber(data.estimatedDailyCost)}</strong></span>
          </div>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                const headers = ['Hour', 'Actual Demand (kW)', 'Baseline (kW)', 'Tariff (INR/kWh)', 'Peak Tariff Active']
                const rows = data.hourlyTrend.map(pt => [
                  pt.hour,
                  pt.actualKw,
                  pt.baselineKw,
                  pt.tariffRate,
                  pt.isPeakTariff ? 'YES' : 'NO'
                ])
                exportToCsv('greenpulse_energy_hourly_telemetry', headers, rows)
                toast.success('Energy Data Exported', {
                  description: 'Exported 15-minute interval power consumption log as CSV.',
                })
              }}
            >
              <Download className="size-3.5" />
              Export CSV
            </Button>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                refetch()
                toast.success('Energy Explorer Synced', {
                  description: 'Latest utility submetering channels refreshed.',
                })
              }}
            >
              <Sparkles className="size-3.5" />
              Refresh Data
            </Button>
          </div>
        }
      />

      {/* Top Peak Demand & Contract Headroom Tracker Banner */}
      <section aria-label="Peak Demand Tracker" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Current Instantaneous Demand</span>
            <IconTile icon={Zap} tone="info" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {formatNumber(data.currentDemandKw)} <span className="text-sm font-normal text-muted-foreground">kW</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Load Factor</span>
            <span className="font-semibold text-foreground">62.2%</span>
          </div>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Contractual Peak Maximum</span>
            <IconTile icon={Activity} tone="neutral" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {formatNumber(data.contractedPeakLimitKw)} <span className="text-sm font-normal text-muted-foreground">kW</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Penalty Threshold</span>
            <span className="font-semibold text-warning-ink">{data.peakDemandAnalytics.penaltyThresholdKw} kW</span>
          </div>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Recorded Shift Peak</span>
            <ToneBadge tone="warning">
              {data.peakDemandAnalytics.peakTime}
            </ToneBadge>
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {formatNumber(data.peakDemandAnalytics.peakRecordedKw)} <span className="text-sm font-normal text-muted-foreground">kW</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Power Factor at Peak</span>
            <span className="font-semibold text-foreground">{data.peakDemandAnalytics.powerFactorAtPeak}</span>
          </div>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Today's Cumulative Energy</span>
            <IconTile icon={BarChart3} tone="success" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {formatNumber(data.todayTotalKwh)} <span className="text-sm font-normal text-muted-foreground">kWh</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Est. Energy Bill</span>
            <span className="font-semibold text-foreground">₹{formatNumber(data.estimatedDailyCost)}</span>
          </div>
        </Surface>
      </section>

      {/* Main Consumption Trend Section */}
      <Surface className="flex flex-col gap-6 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b pb-4">
          <div className="flex items-center gap-2.5">
            <IconTile icon={Zap} tone="info" />
            <div>
              <h3 className="text-lg font-semibold text-foreground">Factory Power Consumption Profiles</h3>
              <p className="text-xs text-muted-foreground">
                Continuous 24-hour load shape with Time-of-Day (ToD) tariff bands overlay
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <SegmentedControl
              value={timeView}
              options={[
                { value: 'hourly', label: 'Hourly Profile' },
                { value: 'daily', label: '7-Day History' },
                { value: 'weekly', label: 'Weekly Trend' },
                { value: 'monthly', label: 'Monthly Trend' },
              ]}
              onChange={setTimeView}
              ariaLabel="Time view filter"
            />
          </div>
        </div>

        {/* View 1: Hourly Consumption */}
        {timeView === 'hourly' && (
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span className="flex items-center gap-2">
                <span className="size-2 rounded-full bg-primary" /> Active Load (kW)
                <span className="size-2 rounded-full bg-muted-foreground/50" /> Baseline (kW)
              </span>
              <span className="rounded bg-amber-500/10 px-2 py-0.5 text-amber-600 dark:text-amber-400 font-medium">
                Peak Tariff Zone: 10:00 - 12:00 & 18:00 - 22:00 (₹10.40/kWh)
              </span>
            </div>

            <ChartContainer config={hourlyChartConfig} className="aspect-auto h-72 w-full">
              <AreaChart data={data.hourlyTrend} margin={{ left: -10, right: 10, top: 10 }}>
                <defs>
                  <linearGradient id="hourly-load-grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis dataKey="hour" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis tickLine={false} axisLine={false} tickMargin={8} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Area type="monotone" dataKey="actualKw" stroke="var(--chart-1)" strokeWidth={2} fill="url(#hourly-load-grad)" />
                <Line type="monotone" dataKey="baselineKw" stroke="var(--chart-2)" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
              </AreaChart>
            </ChartContainer>
          </div>
        )}

        {/* View 2: Daily Consumption */}
        {timeView === 'daily' && (
          <div className="flex flex-col gap-4">
            <ChartContainer config={dailyChartConfig} className="aspect-auto h-72 w-full">
              <BarChart data={data.dailyTrend} margin={{ left: -10, right: 10, top: 10 }}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis dataKey="date" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis tickLine={false} axisLine={false} tickMargin={8} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="energyKwh" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
                <Line type="monotone" dataKey="targetKwh" stroke="var(--chart-3)" strokeWidth={2} dot={false} />
              </BarChart>
            </ChartContainer>
          </div>
        )}

        {/* View 3: Weekly Trend */}
        {timeView === 'weekly' && (
          <div className="flex flex-col gap-4">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {data.weeklyTrend.map((wk) => (
                <div key={wk.week} className="rounded-lg border bg-muted/20 p-4 text-center">
                  <span className="text-xs text-muted-foreground">{wk.week}</span>
                  <p className="text-xl font-bold text-foreground tabular-nums">{formatNumber(wk.energyKwh)} kWh</p>
                  <span className="text-[11px] text-muted-foreground">Weekend Ratio: {wk.weekendRatioPercent}%</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground text-center">
              Weekly energy intensity decreased 5.4% over 4 weeks due to compressed air system optimization.
            </p>
          </div>
        )}

        {/* View 4: Monthly Trend */}
        {timeView === 'monthly' && (
          <div className="flex flex-col gap-4">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b bg-muted/30 text-muted-foreground font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Billing Month</th>
                    <th className="py-2.5 px-3 text-right">Energy (MWh)</th>
                    <th className="py-2.5 px-3 text-right">Target (MWh)</th>
                    <th className="py-2.5 px-3 text-right">Variance</th>
                    <th className="py-2.5 px-3 text-right">Energy Bill (Lakhs)</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {data.monthlyTrend.map((m) => (
                    <tr key={m.month} className="hover:bg-muted/20">
                      <td className="py-2.5 px-3 font-medium text-foreground">{m.month}</td>
                      <td className="py-2.5 px-3 text-right font-bold tabular-nums">{m.energyMwh} MWh</td>
                      <td className="py-2.5 px-3 text-right text-muted-foreground tabular-nums">{m.budgetMwh} MWh</td>
                      <td className="py-2.5 px-3 text-right tabular-nums text-success">
                        -{((1 - m.energyMwh / m.budgetMwh) * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 px-3 text-right font-semibold text-foreground tabular-nums">
                        ₹{m.costLaksh} L
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Surface>

      {/* Machine Comparison & Department Comparison */}
      <section aria-label="Machine and Department Breakdown" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Machine Comparison */}
        <Surface className="flex flex-col gap-4 p-5">
          <SectionHeader
            title="Machine Energy Comparison"
            description="Active power consumption share across all six key machines."
            icon={Cpu}
          />
          <div className="flex flex-col gap-3">
            {data.machineComparison.map((m) => (
              <div key={m.machine} className="flex flex-col gap-1.5 rounded-lg border bg-muted/20 p-3">
                <div className="flex items-center justify-between text-xs font-medium">
                  <span className="text-foreground">{m.machine}</span>
                  <span className="font-bold text-foreground tabular-nums">
                    {m.currentKw} kW · {m.sharePercent}%
                  </span>
                </div>
                <MeterBar value={m.sharePercent} label={m.machine} tone="info" />
              </div>
            ))}
          </div>
        </Surface>

        {/* Department Comparison */}
        <Surface className="flex flex-col gap-4 p-5">
          <SectionHeader
            title="Department Electrical Intensity"
            description="Power demand and hourly energy expenditure by manufacturing bay."
            icon={Layers}
          />
          <div className="flex flex-col divide-y rounded-lg border">
            {data.departmentComparison.map((dept) => (
              <div key={dept.department} className="flex items-center justify-between p-3.5 text-xs">
                <div>
                  <p className="font-semibold text-foreground">{dept.department}</p>
                  <p className="text-muted-foreground">{dept.sharePercent}% total factory load</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-foreground tabular-nums">{dept.powerKw} kW</p>
                  <p className="text-muted-foreground tabular-nums">₹{formatNumber(dept.costPerHour)} / hr</p>
                </div>
              </div>
            ))}
          </div>
        </Surface>
      </section>

      {/* 7-Day x 24-Hour Energy Heatmap */}
      <Surface className="flex flex-col gap-4 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-3">
          <div className="flex items-center gap-2">
            <IconTile icon={Flame} tone="warning" />
            <div>
              <h3 className="text-base font-semibold text-foreground">7-Day × 24-Hour Energy Intensity Heatmap</h3>
              <p className="text-xs text-muted-foreground">
                Hourly plant load distribution across days of the week. Darker squares signify peak electrical intensity.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <span>Low (20%)</span>
            <span className="size-3 rounded bg-emerald-500/20" />
            <span className="size-3 rounded bg-emerald-500/50" />
            <span className="size-3 rounded bg-amber-500/70" />
            <span className="size-3 rounded bg-rose-500" />
            <span>Peak (100%)</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <div className="min-w-[700px] flex flex-col gap-1.5">
            {/* Heatmap Hour Header */}
            <div className="flex items-center gap-1 text-[10px] text-muted-foreground font-mono">
              <span className="w-10 text-right pr-2">Day</span>
              {Array.from({ length: 24 }).map((_, h) => (
                <span key={h} className="flex-1 text-center">{h}h</span>
              ))}
            </div>

            {/* Heatmap Rows */}
            {data.heatmap7x24.map((row) => (
              <div key={row.day} className="flex items-center gap-1">
                <span className="w-10 text-xs font-semibold text-foreground pr-2 text-right">{row.day}</span>
                {row.hours.map((intensity, hourIdx) => {
                  let bg = 'bg-emerald-500/20 text-emerald-800 dark:text-emerald-300'
                  if (intensity > 40 && intensity <= 70) bg = 'bg-emerald-500/50 text-foreground'
                  if (intensity > 70 && intensity <= 90) bg = 'bg-amber-500/70 text-foreground'
                  if (intensity > 90) bg = 'bg-rose-500 text-white font-bold'

                  return (
                    <div
                      key={hourIdx}
                      title={`${row.day} @ ${hourIdx}:00 - ${intensity}% Intensity`}
                      className={`flex-1 h-7 rounded-sm flex items-center justify-center text-[10px] tabular-nums transition-transform hover:scale-110 cursor-pointer ${bg}`}
                    >
                      {intensity}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      </Surface>
    </div>
  )
}
