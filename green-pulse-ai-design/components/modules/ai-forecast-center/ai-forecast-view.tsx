'use client'

import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  Calendar,
  Clock,
  Cpu,
  Download,
  IndianRupee,
  Layers,
  Leaf,
  LineChart as LineChartIcon,
  Sparkles,
  TrendingUp,
  Zap,
} from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
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
import { useAiForecastData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'
import { exportToCsv } from '@/lib/export-utils'

const forecastChartConfig = {
  forecastKw: { label: 'AI Forecast (kW)', color: 'var(--chart-1)' },
  actualKw: { label: 'Actual Telemetry (kW)', color: 'var(--chart-4)' },
} satisfies ChartConfig

export function AiForecastView() {
  const { data, isLoading, isError, refetch } = useAiForecastData()
  const [confidenceBand, setConfidenceBand] = useState<'80' | '95' | 'none'>('80')
  const [metricTab, setMetricTab] = useState<'energy' | 'cost' | 'carbon'>('energy')

  if (isLoading) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Predictive Intelligence"
          title="AI Forecast Center"
          description="Machine learning energy, cost, carbon, and peak demand projections."
        />
        <LoadingPanel className="min-h-96" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <Surface className="flex min-h-96 flex-col items-center justify-center gap-4 p-8 text-center">
        <BrainCircuit className="size-12 text-destructive" />
        <h2 className="text-xl font-semibold text-foreground">AI Forecast Model Unavailable</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Temporal Fusion Transformer inference cluster did not return predictions.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Rerun Inference
        </Button>
      </Surface>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="Predictive Intelligence"
        title="AI Forecast Center"
        description="Deep learning multi-horizon predictions for energy demand, financial expenditure, carbon emissions, and peak load threshold breaches."
        meta={
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Model: <strong className="text-foreground">{data.modelArchitecture}</strong></span>
            <span>•</span>
            <span>Accuracy R²: <strong className="text-success">{data.r2Score}</strong></span>
            <span>•</span>
            <span>Horizon: <strong className="text-foreground">{data.forecastRange}</strong></span>
          </div>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                const headers = ['Time', 'Forecast (kW)', 'Actual (kW)', 'Lower Bound 80% (kW)', 'Upper Bound 80% (kW)', 'Cost (INR)', 'Carbon (kg CO2e)']
                const rows = data.hourlyForecast.map(pt => [
                  pt.time,
                  pt.forecastKw,
                  pt.actualKw ?? 'N/A',
                  pt.confidenceLower80,
                  pt.confidenceUpper80,
                  pt.costInr,
                  pt.carbonKg
                ])
                exportToCsv('greenpulse_24h_ai_forecast_model', headers, rows)
                toast.success('Forecast Exported', {
                  description: 'Saved 24-hour hourly machine learning forecast curve as CSV.',
                })
              }}
            >
              <Download className="size-3.5" />
              Export Forecast
            </Button>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                refetch()
                toast.success('Inference Completed', {
                  description: 'Retrained with latest shift batch completion parameters.',
                })
              }}
            >
              <Sparkles className="size-3.5" />
              Re-run Model
            </Button>
          </div>
        }
      />

      {/* 4 Core Forecast KPI Tiles */}
      <section aria-label="Forecast KPIs" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* 1. Energy Forecast */}
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Projected 24h Energy</span>
            <IconTile icon={Zap} tone="info" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {formatNumber(data.projectedDayEnergyKwh)} <span className="text-sm font-normal text-muted-foreground">kWh</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Baseline Variance</span>
            <span className="font-semibold text-success">-2.1% (Lower)</span>
          </div>
        </Surface>

        {/* 2. Cost Forecast */}
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Projected Electricity Cost</span>
            <IconTile icon={IndianRupee} tone="neutral" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            ₹{formatNumber(data.projectedCost)}
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Peak Tariff Share</span>
            <span className="font-semibold text-warning-ink">38.4% of bill</span>
          </div>
        </Surface>

        {/* 3. Carbon Forecast */}
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Projected Carbon Emissions</span>
            <IconTile icon={Leaf} tone="success" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {data.projectedCarbonTons} <span className="text-sm font-normal text-muted-foreground">t CO₂e</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Solar Avoidance</span>
            <span className="font-semibold text-success">-3.4 t avoided</span>
          </div>
        </Surface>

        {/* 4. Peak Demand Forecast */}
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Predicted Peak Spike</span>
            <ToneBadge tone="warning">
              @ {data.peakHour}
            </ToneBadge>
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {formatNumber(data.projectedPeakDemandKw)} <span className="text-sm font-normal text-muted-foreground">kW</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Contract Margin</span>
            <span className="font-semibold text-success">680 kW headroom</span>
          </div>
        </Surface>
      </section>

      {/* Main Forecast Chart with Confidence Intervals */}
      <Surface className="flex flex-col gap-6 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b pb-4">
          <div className="flex items-center gap-2.5">
            <IconTile icon={BrainCircuit} tone="info" />
            <div>
              <h3 className="text-base font-semibold text-foreground">Next 24-Hour Predictive Load & Confidence Intervals</h3>
              <p className="text-xs text-muted-foreground">
                Continuous neural forecast showing actual telemetry vs predicted power demand envelope
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground font-medium">Confidence Band:</span>
            <SegmentedControl
              value={confidenceBand}
              options={[
                { value: '80', label: '80% Interval' },
                { value: '95', label: '95% Interval' },
                { value: 'none', label: 'Curve Only' },
              ]}
              onChange={setConfidenceBand}
              ariaLabel="Confidence interval selector"
            />
          </div>
        </div>

        <ChartContainer config={forecastChartConfig} className="aspect-auto h-72 w-full">
          <AreaChart data={data.hourlyForecast} margin={{ left: -10, right: 10, top: 10 }}>
            <defs>
              <linearGradient id="forecast-band-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.25} />
                <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} strokeDasharray="3 3" />
            <XAxis dataKey="time" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} domain={['dataMin - 100', 'dataMax + 100']} />
            <ChartTooltip content={<ChartTooltipContent />} />

            {/* Shaded Confidence Intervals */}
            {confidenceBand === '95' && (
              <Area
                type="monotone"
                dataKey="upperBound95"
                stroke="transparent"
                fill="url(#forecast-band-grad)"
              />
            )}
            {confidenceBand === '80' && (
              <Area
                type="monotone"
                dataKey="upperBound80"
                stroke="transparent"
                fill="url(#forecast-band-grad)"
              />
            )}

            {/* Actual Telemetry */}
            <Line
              type="monotone"
              dataKey="actualKw"
              stroke="var(--chart-4)"
              strokeWidth={2.5}
              dot={{ r: 3, fill: 'var(--chart-4)' }}
            />

            {/* ML Forecast Line */}
            <Line
              type="monotone"
              dataKey="forecastKw"
              stroke="var(--chart-1)"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={false}
            />
          </AreaChart>
        </ChartContainer>

        <div className="flex flex-wrap items-center justify-between text-xs text-muted-foreground border-t pt-3">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 font-medium text-foreground">
              <span className="size-2 rounded-full bg-success" /> Solid Green: Measured Actual Telemetry
            </span>
            <span className="flex items-center gap-1.5 font-medium text-foreground">
              <span className="size-2 rounded-full bg-primary" /> Dashed Blue: TFT Neural Forecast
            </span>
          </div>
          <span>Ambient Temp Range: 21°C (night) to 34°C (peak day)</span>
        </div>
      </Surface>

      {/* AI Explanation & Primary Drivers Section */}
      <section aria-label="AI Explainability and Timeline" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* AI Explainability Card */}
        <Surface className="flex flex-col gap-4 p-5">
          <SectionHeader
            title="AI Model Explainability (SHAP Value Drivers)"
            description="Neural network feature attribution explaining why this load curve is predicted."
            icon={BrainCircuit}
          />

          <div className="flex flex-col gap-3">
            {data.aiExplanation.primaryDrivers.map((driver, idx) => (
              <div key={idx} className="flex flex-col gap-1.5 rounded-lg border bg-muted/20 p-3 text-xs">
                <div className="flex items-center justify-between font-semibold text-foreground">
                  <span>{driver.factor}</span>
                  <Badge variant={driver.direction === 'up' ? 'destructive' : 'secondary'} className="text-[11px] font-mono">
                    {driver.impactKw}
                  </Badge>
                </div>
                <p className="text-muted-foreground">{driver.rationale}</p>
              </div>
            ))}
          </div>

          <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-muted-foreground">
            <p className="font-semibold text-primary">Model Confidence Rationale</p>
            {data.aiExplanation.modelConfidenceNote}
          </div>
        </Surface>

        {/* Forecast Timeline Milestones */}
        <Surface className="flex flex-col justify-between gap-4 p-5">
          <SectionHeader
            title="Forecast Timeline Milestones"
            description="Anticipated operational transitions and tariff inflection points."
            icon={Clock}
          />

          <div className="flex flex-col gap-3">
            {data.timelineMilestones.map((m, idx) => (
              <div key={idx} className="flex flex-col gap-1 rounded-lg border bg-card p-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-foreground">{m.event}</span>
                  <Badge variant="outline" className="font-mono text-[10px]">{m.time}</Badge>
                </div>
                <p className="text-muted-foreground">{m.impact}</p>
                <p className="text-primary font-medium mt-1">Action: {m.recommendation}</p>
              </div>
            ))}
          </div>

          <div className="rounded-lg border bg-muted/30 p-3 text-xs flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Peak Demand Alert Monitor</p>
              <p className="text-muted-foreground">Exceedance probability for 2,500 kW ceiling: 4.8% (Nominal)</p>
            </div>
            <ToneBadge tone="success">Safe</ToneBadge>
          </div>
        </Surface>
      </section>
    </div>
  )
}
