'use client'

import {
  Activity,
  Calendar,
  CheckCircle2,
  Clock,
  Cpu,
  Download,
  Factory,
  FileSpreadsheet,
  Gauge,
  Layers,
  Leaf,
  ShieldAlert,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Users,
  Wrench,
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
import { KpiCard } from '@/components/shared/kpi-card'
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
import { Progress } from '@/components/ui/progress'
import { usePlantOverviewData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'
import { exportAuditDocument } from '@/lib/export-utils'
import { getScoreTone } from '@/lib/tone'
import type { DepartmentMetric, UtilityConsumptionItem } from '@/types'

const productionChartConfig = {
  actual: { label: 'Actual Units', color: 'var(--chart-1)' },
  target: { label: 'Target Units', color: 'var(--chart-2)' },
} satisfies ChartConfig

export function PlantOverviewView() {
  const { data, isLoading, isError, refetch } = usePlantOverviewData()
  const [departmentFilter, setDepartmentFilter] = useState<'all' | 'high-power' | 'needs-attention'>('all')

  if (isLoading) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Enterprise Operations"
          title="Plant Overview"
          description="Executive overview of the manufacturing plant, real-time energy intensity, and line throughput."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <LoadingPanel key={i} className="min-h-48" />
          ))}
        </div>
        <LoadingPanel className="min-h-80" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <Surface className="flex min-h-96 flex-col items-center justify-center gap-4 p-8 text-center">
        <ShieldAlert className="size-12 text-destructive" />
        <h2 className="text-xl font-semibold text-foreground">Failed to load Plant Overview</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Telemetry stream connection timed out while querying supervisory plant registers.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Retry Telemetry Query
        </Button>
      </Surface>
    )
  }

  const filteredDepartments = data.departments.filter((dept) => {
    if (departmentFilter === 'high-power') return dept.powerKw > 200
    if (departmentFilter === 'needs-attention') return dept.status === 'warning' || dept.healthScore < 85
    return true
  })

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="Executive Plant Operations"
        title="Plant Overview"
        description="Comprehensive real-time telemetry, production rate, energy intensity, and utility health across all manufacturing halls."
        meta={
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5 font-medium text-foreground">
              <span className="size-2 rounded-full bg-success animate-status-pulse" />
              Live Substation Sync
            </span>
            <span>•</span>
            <span>Facility: {data.plantName}</span>
            <span>•</span>
            <span>Shift: {data.shift.currentShift}</span>
          </div>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5 text-xs"
              onClick={() => {
                exportAuditDocument(
                  `${data.plantName} - Shift Operations & Telemetry Brief`,
                  'Plant Operations',
                  'PDF',
                  {
                    'Plant Name': data.plantName,
                    'Plant ID': data.plantId,
                    'Current Shift': `${data.shift.currentShift} (${data.shift.shiftCode})`,
                    'Shift Time Range': data.shift.timeRange,
                    'Lead Engineer': data.shift.leadEngineer,
                    'Operators on Floor': data.shift.operatorsOnFloor,
                    'Maintenance Techs': data.shift.maintenanceTechs,
                    'Plant Health Index': `${data.healthSummary.healthIndex}/100`,
                    'Uptime Rate': `${data.healthSummary.uptimePercent}%`,
                    'ISO 50001 Status': data.healthSummary.iso50001Status,
                  },
                  [
                    { label: 'Shift Energy Budget', value: `${formatNumber(data.shift.shiftEnergyBudgetKwh)} kWh` },
                    { label: 'Energy Consumed', value: `${formatNumber(data.shift.shiftEnergyConsumedKwh)} kWh` },
                    { label: 'Production Units', value: `${formatNumber(data.shift.productionActual)} / ${formatNumber(data.shift.productionTarget)}` },
                    { label: 'First Pass Yield', value: `${data.productionSummary.firstPassYield}%` },
                  ],
                  {
                    headers: ['Department Zone', 'Active Power (kW)', 'Energy Today (kWh)', 'Health Score', 'Status'],
                    rows: data.departments.map(d => [d.name, d.powerKw, d.energyTodayKwh, `${d.healthScore}/100`, d.status.toUpperCase()])
                  }
                )
                toast.success('Shift report exported', {
                  description: 'Plant operations snapshot downloaded as executive document.',
                })
              }}
            >
              <Download className="size-3.5" />
              Export Brief
            </Button>
            <Button
              size="sm"
              className="gap-1.5 text-xs"
              onClick={() => {
                refetch()
                toast.success('Telemetry refreshed', {
                  description: 'All 4,200 Modbus tags re-synchronized with edge gateway.',
                })
              }}
            >
              <Sparkles className="size-3.5" />
              Sync Sensors
            </Button>
          </div>
        }
      />

      {/* 1. Plant KPIs */}
      <section aria-label="Executive Plant KPIs" className="flex flex-col gap-4">
        <SectionHeader
          title="Plant Core KPIs"
          description="High-level operational, energy intensity, and carbon performance indicators."
          icon={Gauge}
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {data.kpis.map((metric, index) => (
            <Reveal key={metric.id} index={index}>
              <KpiCard metric={metric} />
            </Reveal>
          ))}
        </div>
      </section>

      {/* 2. Production Summary & Shift Info */}
      <section aria-label="Production Summary and Shift Progress" className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {/* Production Throughput Chart */}
        <Surface className="flex flex-col gap-4 p-5 xl:col-span-2">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-3">
            <div className="flex items-center gap-2.5">
              <IconTile icon={Factory} tone="info" />
              <div>
                <h3 className="text-base font-semibold text-foreground">Production Throughput vs Target</h3>
                <p className="text-xs text-muted-foreground">Hourly part output tracked against Shift B master schedule</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs font-medium">
                {data.productionSummary.actualUnits} / {data.productionSummary.targetUnits} Units
              </Badge>
              <ToneBadge tone="success">
                {((data.productionSummary.actualUnits / data.productionSummary.targetUnits) * 100).toFixed(1)}% Achieved
              </ToneBadge>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 py-1 sm:grid-cols-4">
            <div className="rounded-lg border bg-muted/30 p-3">
              <p className="text-xs text-muted-foreground">Throughput Rate</p>
              <p className="mt-1 text-xl font-semibold text-foreground">
                {data.productionSummary.throughputRatePerHour} <span className="text-xs font-normal text-muted-foreground">u/hr</span>
              </p>
            </div>
            <div className="rounded-lg border bg-muted/30 p-3">
              <p className="text-xs text-muted-foreground">First Pass Yield</p>
              <p className="mt-1 text-xl font-semibold text-success">
                {data.productionSummary.firstPassYield}%
              </p>
            </div>
            <div className="rounded-lg border bg-muted/30 p-3">
              <p className="text-xs text-muted-foreground">Downtime Incidents</p>
              <p className="mt-1 text-xl font-semibold text-foreground">
                {data.productionSummary.downtimeMinutes} <span className="text-xs font-normal text-muted-foreground">min</span>
              </p>
            </div>
            <div className="rounded-lg border bg-muted/30 p-3">
              <p className="text-xs text-muted-foreground">Active Lines</p>
              <p className="mt-1 text-xl font-semibold text-foreground">
                {data.productionSummary.activeLines} / {data.productionSummary.totalLines}
              </p>
            </div>
          </div>

          <ChartContainer config={productionChartConfig} className="aspect-auto h-64 w-full">
            <BarChart data={data.productionSummary.hourlyThroughput} margin={{ left: -10, right: 10, top: 10 }}>
              <CartesianGrid vertical={false} strokeDasharray="3 3" />
              <XAxis dataKey="hour" tickLine={false} axisLine={false} tickMargin={8} />
              <YAxis tickLine={false} axisLine={false} tickMargin={8} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="target" fill="var(--color-target)" radius={[4, 4, 0, 0]} opacity={0.4} />
              <Bar dataKey="actual" fill="var(--color-actual)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ChartContainer>
        </Surface>

        {/* Shift Information Card */}
        <Surface className="flex flex-col justify-between gap-5 p-5">
          <div className="flex items-center justify-between border-b pb-3">
            <div className="flex items-center gap-2.5">
              <IconTile icon={Clock} tone="info" />
              <div>
                <h3 className="text-base font-semibold text-foreground">Active Shift Information</h3>
                <p className="text-xs text-muted-foreground">{data.shift.timeRange}</p>
              </div>
            </div>
            <Badge variant="secondary" className="font-mono text-xs">
              {data.shift.shiftCode}
            </Badge>
          </div>

          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Shift Lead</span>
              <span className="font-medium text-foreground">{data.shift.leadEngineer}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Floor Personnel</span>
              <span className="font-medium text-foreground">
                {data.shift.operatorsOnFloor} operators · {data.shift.maintenanceTechs} technicians
              </span>
            </div>

            <div className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-3">
              <div className="flex items-center justify-between text-xs font-medium">
                <span className="text-muted-foreground">Shift Energy Budget</span>
                <span className="text-foreground">
                  {formatNumber(data.shift.shiftEnergyConsumedKwh)} / {formatNumber(data.shift.shiftEnergyBudgetKwh)} kWh
                </span>
              </div>
              <Progress
                value={(data.shift.shiftEnergyConsumedKwh / data.shift.shiftEnergyBudgetKwh) * 100}
                className="h-2"
              />
              <p className="text-[11px] text-muted-foreground">
                65% budget consumed vs {data.shift.elapsedPercent}% shift duration elapsed (Within target).
              </p>
            </div>

            <div className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-3">
              <div className="flex items-center justify-between text-xs font-medium">
                <span className="text-muted-foreground">Production Run Progress</span>
                <span className="text-foreground">
                  {data.shift.productionActual} / {data.shift.productionTarget} Units
                </span>
              </div>
              <Progress
                value={(data.shift.productionActual / data.shift.productionTarget) * 100}
                className="h-2"
              />
            </div>
          </div>

          <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-muted-foreground">
            <p className="font-medium text-primary">Shift Energy Note</p>
            Peak tariff starts at 18:00 IST. Ensure heat furnace Zone 2 preheating ramp completes before 17:45.
          </div>
        </Surface>
      </section>

      {/* 3. Department Overview & Comparison */}
      <section aria-label="Department Overview" className="flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <SectionHeader
            title="Department Energy & Health Overview"
            description="Status, real-time load, and asset efficiency across manufacturing departments."
            icon={Layers}
          />
          <SegmentedControl
            value={departmentFilter}
            options={[
              { value: 'all', label: 'All Departments', count: data.departments.length },
              { value: 'high-power', label: 'High Demand (>200 kW)' },
              { value: 'needs-attention', label: 'Needs Attention' },
            ]}
            onChange={setDepartmentFilter}
            ariaLabel="Department filter"
          />
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredDepartments.map((dept, index) => (
            <Reveal key={dept.id} index={index}>
              <Surface interactive className="flex flex-col gap-4 p-5">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="truncate text-base font-semibold text-foreground">{dept.name}</h3>
                    <p className="text-xs text-muted-foreground">{dept.zone} · {dept.machineCount} major assets</p>
                  </div>
                  <ToneBadge
                    tone={dept.status === 'optimal' ? 'success' : dept.status === 'warning' ? 'warning' : 'info'}
                    pulse={dept.status === 'warning'}
                  >
                    {dept.status === 'optimal' ? 'Optimal' : dept.status === 'warning' ? 'Warning' : 'Normal'}
                  </ToneBadge>
                </div>

                <div className="grid grid-cols-2 gap-3 py-1 text-sm">
                  <div>
                    <span className="text-xs text-muted-foreground">Power Draw</span>
                    <p className="text-lg font-semibold text-foreground tabular-nums">
                      {formatNumber(dept.powerKw)} <span className="text-xs font-normal text-muted-foreground">kW</span>
                    </p>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground">Energy Today</span>
                    <p className="text-lg font-semibold text-foreground tabular-nums">
                      {formatNumber(dept.energyTodayKwh)} <span className="text-xs font-normal text-muted-foreground">kWh</span>
                    </p>
                  </div>
                </div>

                <div className="flex flex-col gap-2 border-t pt-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Equipment Efficiency</span>
                    <span className="font-semibold text-foreground">{dept.efficiency}%</span>
                  </div>
                  <MeterBar value={dept.efficiency} label="Efficiency" tone={getScoreTone(dept.efficiency)} />

                  <div className="flex items-center justify-between text-xs mt-1">
                    <span className="text-muted-foreground">Health Index</span>
                    <span className="font-semibold text-foreground">{dept.healthScore}/100</span>
                  </div>
                  <MeterBar value={dept.healthScore} label="Health Index" tone={getScoreTone(dept.healthScore)} />
                </div>
              </Surface>
            </Reveal>
          ))}
        </div>
      </section>

      {/* 4. Utility Consumption & Active Utilities */}
      <section aria-label="Utility Consumption and Active Assets" className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {/* Utility Flow Rates */}
        <Surface className="flex flex-col gap-4 p-5">
          <SectionHeader
            title="Utility Consumption Breakdown"
            description="Continuous volumetric and electrical consumption across plant utilities."
            icon={Zap}
          />
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {data.utilities.map((util) => (
              <div key={util.id} className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-foreground">{util.name}</span>
                  <ToneBadge tone={util.status === 'peak' ? 'warning' : 'success'}>
                    {util.status}
                  </ToneBadge>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="text-xl font-semibold text-foreground tabular-nums">
                    {formatNumber(util.currentRate)} <span className="text-xs font-normal text-muted-foreground">{util.unit}</span>
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Cap: {util.capacity} {util.unit}
                  </span>
                </div>
                <MeterBar
                  value={util.utilizationPercent}
                  label={util.name}
                  tone={util.utilizationPercent > 80 ? 'warning' : 'info'}
                />
              </div>
            ))}
          </div>
        </Surface>

        {/* Active Utility Assets */}
        <Surface className="flex flex-col gap-4 p-5">
          <SectionHeader
            title="Active Heavy Utility Assets"
            description="Rotary compressors, chilled hydronic pumps, and main substation transformers."
            icon={Cpu}
          />
          <div className="flex flex-col divide-y rounded-lg border">
            {data.activeUtilities.map((asset) => (
              <div key={asset.id} className="flex items-center justify-between p-3.5 text-sm">
                <div className="flex items-center gap-3">
                  <span className={`size-2.5 rounded-full ${asset.status === 'warning' ? 'bg-warning animate-status-pulse' : 'bg-success'}`} />
                  <div>
                    <p className="font-medium text-foreground">{asset.name}</p>
                    <p className="text-xs text-muted-foreground">{asset.type} · Runtime: {asset.runtimeTodayHours}h</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-foreground tabular-nums">{asset.powerKw} kW</p>
                  <p className="text-xs text-muted-foreground">{asset.loadFactor}% load</p>
                </div>
              </div>
            ))}
          </div>
        </Surface>
      </section>

      {/* 5. Factory Timeline & Plant Health Summary */}
      <section aria-label="Timeline and Health Summary" className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {/* Factory Operational Timeline */}
        <Surface className="flex flex-col gap-4 p-5 xl:col-span-2">
          <SectionHeader
            title="Factory Operational Timeline"
            description="Chronological event audit for Shift B (production batches, maintenance, solar generation)."
            icon={Activity}
          />
          <div className="relative flex flex-col gap-4 pl-4 before:absolute before:left-1 before:top-2 before:bottom-2 before:w-0.5 before:bg-border">
            {data.timeline.map((event) => (
              <div key={event.id} className="relative flex flex-col gap-1 pl-4">
                <span
                  className={`absolute -left-[15px] top-1.5 size-2.5 rounded-full ring-4 ring-card ${
                    event.severity === 'warning'
                      ? 'bg-warning'
                      : event.severity === 'success'
                        ? 'bg-success'
                        : 'bg-primary'
                  }`}
                />
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-foreground">{event.time}</span>
                  <Badge variant="outline" className="text-[10px] uppercase">
                    {event.category}
                  </Badge>
                  <h4 className="text-sm font-medium text-foreground">{event.title}</h4>
                </div>
                <p className="text-xs text-muted-foreground">{event.description}</p>
              </div>
            ))}
          </div>
        </Surface>

        {/* Plant Health & Compliance Summary */}
        <Surface className="flex flex-col justify-between gap-5 p-5">
          <SectionHeader
            title="Plant Health & Compliance"
            description="Composite engineering risk & statutory compliance status."
            icon={CheckCircle2}
          />

          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between rounded-lg border bg-muted/20 p-4">
              <div>
                <p className="text-xs text-muted-foreground">Composite Health Index</p>
                <p className="text-2xl font-bold text-foreground tabular-nums">
                  {data.healthSummary.healthIndex}<span className="text-sm font-normal text-muted-foreground">/100</span>
                </p>
              </div>
              <ToneBadge tone="success" className="text-xs">
                Low Failure Risk
              </ToneBadge>
            </div>

            <div className="flex items-center justify-between rounded-lg border bg-muted/20 p-4">
              <div>
                <p className="text-xs text-muted-foreground">Total Plant Uptime</p>
                <p className="text-2xl font-bold text-success tabular-nums">
                  {data.healthSummary.uptimePercent}%
                </p>
              </div>
              <Badge variant="outline">World Class</Badge>
            </div>

            <div className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-4 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">ESG Environmental Assurance</span>
                <span className="font-medium text-foreground">{data.healthSummary.complianceStatus}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Energy Management System</span>
                <span className="font-medium text-success">{data.healthSummary.iso50001Status}</span>
              </div>
            </div>
          </div>

          <Button
            variant="outline"
            className="w-full text-xs"
            onClick={() => {
              toast.info('ISO 50001 certificate verified', {
                description: 'Bureau Veritas plant accreditation certificate valid through May 2027.',
              })
            }}
          >
            Inspect Audit Certificate
          </Button>
        </Surface>
      </section>
    </div>
  )
}
