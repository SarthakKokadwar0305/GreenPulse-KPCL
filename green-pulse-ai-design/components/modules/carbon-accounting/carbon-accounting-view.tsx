'use client'

import {
  AlertTriangle,
  ArrowDownRight,
  Award,
  CheckCircle2,
  Cpu,
  Download,
  Factory,
  FileCheck,
  Flame,
  Globe2,
  Layers,
  Leaf,
  Recycle,
  Sparkles,
  Sun,
  TrendingDown,
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
import { Progress } from '@/components/ui/progress'
import { useCarbonAccountingData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'
import { exportAuditDocument } from '@/lib/export-utils'

const carbonTrendChartConfig = {
  scope1: { label: 'Scope 1 (Direct)', color: '#f9a825' },
  scope2: { label: 'Scope 2 (Electricity)', color: 'var(--chart-1)' },
  target: { label: 'Glidepath Target', color: 'var(--chart-4)' },
} satisfies ChartConfig

export function CarbonAccountingView() {
  const { data, isLoading, isError, refetch } = useCarbonAccountingData()
  const [scopeTab, setScopeTab] = useState<'all' | 'scope1' | 'scope2'>('all')

  if (isLoading) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Decarbonization & ESG"
          title="Carbon Accounting"
          description="GHG Protocol Scope 1 and Scope 2 carbon footprint tracking."
        />
        <LoadingPanel className="min-h-96" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <Surface className="flex min-h-96 flex-col items-center justify-center gap-4 p-8 text-center">
        <AlertTriangle className="size-12 text-destructive" />
        <h2 className="text-xl font-semibold text-foreground">Failed to Load Carbon Accounting Data</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Emissions factor calculation engine could not be contacted.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Retry GHG Calculation
        </Button>
      </Surface>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="GHG Protocol Corporate Standard"
        title="Carbon Accounting & Decarbonization"
        description="Comprehensive audit-grade carbon accounting. Track direct combustion (Scope 1), purchased grid electricity (Scope 2), renewable solar offsets, and ESG performance metrics."
        meta={
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Grid Emission Factor: <strong className="text-foreground">{data.scope2.gridEmissionFactorKgPerKwh} kg CO₂/kWh</strong></span>
            <span>•</span>
            <span>Rooftop Solar Offset: <strong className="text-success">-{data.scope2.renewableOffsetTons} t CO₂e</strong></span>
            <span>•</span>
            <span>Assurance Standard: <strong className="text-foreground">{data.esgOverview.griCompliance}</strong></span>
          </div>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                exportAuditDocument(
                  'SEBI BRSR & GHG Protocol Scope 1 & 2 Carbon Audit Statement',
                  'Carbon Accounting',
                  'PDF',
                  {
                    'Today Scope 1': `${data.scope1.totalTons} tCO2e`,
                    'Today Scope 2': `${data.scope2.totalTons} tCO2e`,
                    'Month To Date': `${data.monthToDateTons} tCO2e`,
                    'Sustainability Tier': data.sustainabilityTier,
                    'GRI Compliance': data.esgOverview.griCompliance,
                    'BRSR Status': data.esgOverview.brsrStatus,
                  },
                  [
                    { label: 'Today Total Emissions', value: `${data.todayTotalTons} tCO2e` },
                    { label: 'Scope 1 Target', value: `${data.scope1.targetTons} tCO2e` },
                    { label: 'Renewable Offset', value: `${data.scope2.renewableOffsetTons} tCO2e` },
                    { label: 'ESG Index', value: `${data.esgOverview.environmentalIndex}/100` },
                  ],
                  {
                    headers: ['Machine Asset', 'Carbon Footprint (tCO2e)', 'Intensity (kg/unit)', 'Facility Share %'],
                    rows: data.byMachine.map(m => [m.machine, m.carbonTons, m.intensityKgPerUnit, `${m.percent}%`])
                  }
                )
                toast.success('ESG Report Generated', {
                  description: 'BRSR-aligned Scope 1 & 2 GHG footprint pack exported as document.',
                })
              }}
            >
              <Download className="size-3.5" />
              Download Audit Pack
            </Button>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                refetch()
                toast.success('Emissions Recalculated', {
                  description: 'Applied real-time regional grid emission factor 0.82 kg/kWh.',
                })
              }}
            >
              <Sparkles className="size-3.5" />
              Recalculate GHG
            </Button>
          </div>
        }
      />

      {/* Top Carbon KPI Tiles */}
      <section aria-label="Carbon KPIs" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Daily Net Carbon Footprint</span>
            <IconTile icon={Leaf} tone="success" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {data.todayTotalTons} <span className="text-sm font-normal text-muted-foreground">t CO₂e</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Target Ceiling</span>
            <span className="font-semibold text-success">{data.todayTargetTons} t CO₂e (-14% optimal)</span>
          </div>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Scope 1 Direct Combustion</span>
            <IconTile icon={Flame} tone="warning" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {data.scope1.totalTons} <span className="text-sm font-normal text-muted-foreground">t CO₂e</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Natural Gas Burners</span>
            <span className="font-semibold text-foreground">81.8% share</span>
          </div>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Scope 2 Purchased Grid</span>
            <IconTile icon={Zap} tone="info" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {data.scope2.totalTons} <span className="text-sm font-normal text-muted-foreground">t CO₂e</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Clean Solar Offset</span>
            <span className="font-semibold text-success">-{data.scope2.renewableOffsetTons} t CO₂e</span>
          </div>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Sustainability ESG Score</span>
            <Badge variant="outline" className="text-xs font-bold text-primary">
              {data.sustainabilityTier}
            </Badge>
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {data.sustainabilityScore}<span className="text-sm font-normal text-muted-foreground">/100</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Renewable Power Share</span>
            <span className="font-semibold text-foreground">{data.esgOverview.renewableEnergySharePercent}%</span>
          </div>
        </Surface>
      </section>

      {/* Scope 1 vs Scope 2 Breakdown Sections */}
      <section aria-label="Scope 1 and Scope 2 Breakdown" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Scope 1 Card */}
        <Surface className="flex flex-col gap-4 p-5">
          <div className="flex items-center justify-between border-b pb-3">
            <div className="flex items-center gap-2.5">
              <IconTile icon={Flame} tone="warning" />
              <div>
                <h3 className="text-base font-semibold text-foreground">Scope 1: Direct On-Site Combustion</h3>
                <p className="text-xs text-muted-foreground">Thermal furnace natural gas, diesel generator testing, LPG fleets</p>
              </div>
            </div>
            <ToneBadge tone="warning">{data.scope1.totalTons} t CO₂e</ToneBadge>
          </div>

          <div className="flex flex-col gap-3">
            {data.scope1.breakdown.map((item) => (
              <div key={item.source} className="flex flex-col gap-1.5 rounded-lg border bg-muted/20 p-3 text-xs">
                <div className="flex items-center justify-between font-medium">
                  <span className="text-foreground">{item.source}</span>
                  <span className="font-bold text-foreground tabular-nums">{item.tons} t CO₂e ({item.share}%)</span>
                </div>
                <MeterBar value={item.share} label={item.source} tone="warning" />
                <span className="text-[11px] text-muted-foreground">Activity: {item.activityData}</span>
              </div>
            ))}
          </div>
        </Surface>

        {/* Scope 2 Card */}
        <Surface className="flex flex-col gap-4 p-5">
          <div className="flex items-center justify-between border-b pb-3">
            <div className="flex items-center gap-2.5">
              <IconTile icon={Zap} tone="info" />
              <div>
                <h3 className="text-base font-semibold text-foreground">Scope 2: Indirect Purchased Electricity</h3>
                <p className="text-xs text-muted-foreground">33kV grid electricity consumption adjusted for on-site solar generation</p>
              </div>
            </div>
            <ToneBadge tone="success">{data.scope2.totalTons} t CO₂e</ToneBadge>
          </div>

          <div className="flex flex-col gap-3">
            {data.scope2.breakdown.map((item) => (
              <div key={item.source} className="flex flex-col gap-1.5 rounded-lg border bg-muted/20 p-3 text-xs">
                <div className="flex items-center justify-between font-medium">
                  <span className="text-foreground">{item.source}</span>
                  <span className={`font-bold tabular-nums ${item.tons < 0 ? 'text-success' : 'text-foreground'}`}>
                    {item.tons > 0 ? `+${item.tons}` : item.tons} t CO₂e
                  </span>
                </div>
                <MeterBar value={Math.abs(item.share)} label={item.source} tone={item.tons < 0 ? 'success' : 'info'} />
              </div>
            ))}
          </div>
        </Surface>
      </section>

      {/* Carbon Trend (Glidepath) */}
      <Surface className="flex flex-col gap-4 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-3">
          <div className="flex items-center gap-2">
            <IconTile icon={TrendingDown} tone="success" />
            <div>
              <h3 className="text-base font-semibold text-foreground">Historical Carbon Trajectory & Net Zero Glidepath</h3>
              <p className="text-xs text-muted-foreground">
                Monthly GHG performance against corporate Science Based Targets initiative (SBTi) 2030 trajectory.
              </p>
            </div>
          </div>
          <Badge variant="outline" className="text-xs">SBTi 1.5°C Aligned</Badge>
        </div>

        <ChartContainer config={carbonTrendChartConfig} className="aspect-auto h-72 w-full">
          <BarChart data={data.monthlyTrend} margin={{ left: -10, right: 10, top: 10 }}>
            <CartesianGrid vertical={false} strokeDasharray="3 3" />
            <XAxis dataKey="month" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="scope1" stackId="a" fill="#f9a825" radius={[0, 0, 0, 0]} />
            <Bar dataKey="scope2" stackId="a" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
            <Line type="monotone" dataKey="target" stroke="var(--chart-4)" strokeWidth={2} dot={false} />
          </BarChart>
        </ChartContainer>
      </Surface>

      {/* Carbon by Machine & Department */}
      <section aria-label="Machine and Department Carbon Breakdown" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Carbon by Machine */}
        <Surface className="flex flex-col gap-4 p-5">
          <SectionHeader
            title="Carbon Footprint by Machine"
            description="Tons emitted and carbon intensity per produced unit across machinery."
            icon={Cpu}
          />
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b bg-muted/30 text-muted-foreground font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Machine</th>
                  <th className="py-2.5 px-3 text-right">Daily Carbon</th>
                  <th className="py-2.5 px-3 text-right">Intensity</th>
                  <th className="py-2.5 px-3 text-right">Share</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data.byMachine.map((item) => (
                  <tr key={item.machine} className="hover:bg-muted/20">
                    <td className="py-2.5 px-3 font-semibold text-foreground">{item.machine}</td>
                    <td className="py-2.5 px-3 text-right tabular-nums">{item.carbonTons} t CO₂e</td>
                    <td className="py-2.5 px-3 text-right text-muted-foreground tabular-nums">{item.intensityKgPerUnit} kg/u</td>
                    <td className="py-2.5 px-3 text-right font-medium text-foreground tabular-nums">{item.percent}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Surface>

        {/* ESG Overview & Compliance Badges */}
        <Surface className="flex flex-col justify-between gap-5 p-5">
          <SectionHeader
            title="ESG & Sustainability Indices"
            description="Environmental metrics, circularity, and corporate reporting status."
            icon={Award}
          />

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="rounded-lg border bg-muted/20 p-3 text-center">
              <span className="text-muted-foreground">Renewable Share</span>
              <p className="mt-1 text-xl font-bold text-success">{data.esgOverview.renewableEnergySharePercent}%</p>
              <span className="text-[10px] text-muted-foreground">Rooftop Solar PV</span>
            </div>
            <div className="rounded-lg border bg-muted/20 p-3 text-center">
              <span className="text-muted-foreground">Water Recycling</span>
              <p className="mt-1 text-xl font-bold text-foreground">{data.esgOverview.waterRecycleRatioPercent}%</p>
              <span className="text-[10px] text-muted-foreground">Zero Liquid Discharge</span>
            </div>
            <div className="rounded-lg border bg-muted/20 p-3 text-center">
              <span className="text-muted-foreground">Waste Diverted</span>
              <p className="mt-1 text-xl font-bold text-foreground">{data.esgOverview.wasteDivertedPercent}%</p>
              <span className="text-[10px] text-muted-foreground">Circular Economy</span>
            </div>
            <div className="rounded-lg border bg-muted/20 p-3 text-center">
              <span className="text-muted-foreground">BRSR Status</span>
              <p className="mt-1 text-base font-bold text-primary">{data.esgOverview.brsrStatus}</p>
              <span className="text-[10px] text-muted-foreground">SEBI Compliant</span>
            </div>
          </div>

          <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-muted-foreground">
            <p className="font-semibold text-primary">Carbon Offsets Notice</p>
            On-site rooftop solar generated 3,800 kWh today, avoiding 3.12 metric tons of grid CO₂ emissions. Certified for ISO 14064 credit issuance.
          </div>
        </Surface>
      </section>
    </div>
  )
}
