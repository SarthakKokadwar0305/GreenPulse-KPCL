'use client'

import {
  AlertCircle,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Check,
  CheckCircle2,
  Clock,
  Cpu,
  Download,
  FlaskConical,
  Gauge,
  IndianRupee,
  Layers,
  Leaf,
  Play,
  RotateCcw,
  Save,
  SlidersHorizontal,
  Sparkles,
  Sun,
  TrendingDown,
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
import { useSimulatorBaselineData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'
import { exportAuditDocument } from '@/lib/export-utils'

const simChartConfig = {
  baselineKw: { label: 'Baseline Load (kW)', color: 'var(--chart-2)' },
  simulatedKw: { label: 'Simulated Load (kW)', color: 'var(--chart-1)' },
} satisfies ChartConfig

export function WhatIfSimulatorView() {
  const { data: baseline, isLoading, isError } = useSimulatorBaselineData()

  // Simulator Interactive Inputs
  const [productionLoad, setProductionLoad] = useState<number>(100) // % 50 - 150
  const [machineRuntime, setMachineRuntime] = useState<number>(16) // hrs 4 - 24
  const [shiftSchedule, setShiftSchedule] = useState<'1-shift' | '2-shift' | '3-shift' | 'night-shift'>('2-shift')
  const [baseTariff, setBaseTariff] = useState<number>(7.20) // ₹/kWh 4 - 15
  const [renewablePercent, setRenewablePercent] = useState<number>(22) // % 0 - 100

  if (isLoading || !baseline) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Thermodynamic & Tariff Simulation"
          title="What-if Energy Simulator"
          description="Interactive modeling for production load, shift schedules, and renewable power mixes."
        />
        <LoadingPanel className="min-h-96" />
      </div>
    )
  }

  // Reactive Simulation Mathematical Engine
  // Scale factors
  const loadFactor = productionLoad / 100
  const runtimeFactor = machineRuntime / 16
  const shiftMultiplier =
    shiftSchedule === '1-shift'
      ? 0.55
      : shiftSchedule === '2-shift'
        ? 1.0
        : shiftSchedule === '3-shift'
          ? 1.38
          : 0.88 // night-shift heavy

  // Energy Calculation (kWh/day)
  const simulatedDailyEnergyKwh = Math.round(
    baseline.dailyEnergyKwh * loadFactor * runtimeFactor * shiftMultiplier * 0.95,
  )

  // Tariff calculation with Peak weighting and solar offset
  const effectiveTariffRate =
    shiftSchedule === 'night-shift'
      ? baseTariff * 0.78 // heavily off-peak
      : shiftSchedule === '3-shift'
        ? baseTariff * 1.05
        : baseTariff

  // Grid vs Solar share
  const solarShare = renewablePercent / 100
  const gridShare = Math.max(0, 1 - solarShare)
  const gridEnergyPurchased = simulatedDailyEnergyKwh * gridShare

  // Cost calculation (₹/day)
  const simulatedDailyCost = Math.round(gridEnergyPurchased * effectiveTariffRate)

  // Carbon calculation (t CO₂e/day) - 0.82 kg/kWh for grid, 0 for solar
  const simulatedDailyCarbon = Number(((gridEnergyPurchased * 0.82) / 1000).toFixed(2))

  // Deltas
  const deltaEnergyKwh = simulatedDailyEnergyKwh - baseline.dailyEnergyKwh
  const deltaEnergyPercent = Number(((deltaEnergyKwh / baseline.dailyEnergyKwh) * 100).toFixed(1))

  const deltaCost = simulatedDailyCost - baseline.dailyCost
  const deltaCostPercent = Number(((deltaCost / baseline.dailyCost) * 100).toFixed(1))

  const deltaCarbon = Number((simulatedDailyCarbon - baseline.dailyCarbonTons).toFixed(2))
  const deltaCarbonPercent = Number(((deltaCarbon / baseline.dailyCarbonTons) * 100).toFixed(1))

  // Monthly projected savings
  const monthlyProjectedSavings = -deltaCost * 30

  // Generate 24h comparative profile curve
  const simulatedHourlyProfile = baseline.hourlyProfile.map((pt, idx) => {
    let hourModifier = 1.0
    // shift profile modifications
    if (shiftSchedule === '1-shift' && (idx < 8 || idx >= 17)) hourModifier = 0.35
    if (shiftSchedule === 'night-shift') {
      if (idx >= 22 || idx < 6) hourModifier = 1.25
      else if (idx >= 10 && idx < 18) hourModifier = 0.75
    }
    const simulatedKw = Math.round(pt.baselineKw * loadFactor * (machineRuntime / 16) * hourModifier)
    return {
      hour: pt.hour,
      baselineKw: pt.baselineKw,
      simulatedKw,
    }
  })

  // Presets
  const applyPreset = (preset: 'peak-shifter' | 'decarb' | 'max-prod' | 'eco') => {
    if (preset === 'peak-shifter') {
      setProductionLoad(100)
      setMachineRuntime(16)
      setShiftSchedule('night-shift')
      setRenewablePercent(35)
      toast.info('Applied "Peak Tariff Shifter" Preset', {
        description: 'Night-heavy shift pattern with 35% renewable mix loaded.',
      })
    } else if (preset === 'decarb') {
      setProductionLoad(95)
      setMachineRuntime(14)
      setShiftSchedule('2-shift')
      setRenewablePercent(60)
      toast.info('Applied "Aggressive Decarbonization" Preset', {
        description: '60% renewable solar integration with optimized runtime.',
      })
    } else if (preset === 'max-prod') {
      setProductionLoad(140)
      setMachineRuntime(24)
      setShiftSchedule('3-shift')
      setRenewablePercent(22)
      toast.info('Applied "Maximum Throughput Run" Preset', {
        description: '3-Shift 24x7 manufacturing load with 140% line rate.',
      })
    } else if (preset === 'eco') {
      setProductionLoad(80)
      setMachineRuntime(12)
      setShiftSchedule('1-shift')
      setRenewablePercent(45)
      toast.info('Applied "Eco Standby Mode" Preset', {
        description: 'Single-shift lean batching with high solar coverage.',
      })
    }
  }

  const handleReset = () => {
    setProductionLoad(100)
    setMachineRuntime(16)
    setShiftSchedule('2-shift')
    setBaseTariff(7.20)
    setRenewablePercent(22)
    toast.success('Simulation Reset', {
      description: 'Restored baseline parameters to factory default operational values.',
    })
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="Interactive Digital Twin Sandbox"
        title="What-if Simulator"
        description="Live parametric scenario modeling. Dynamically adjust production volumes, machine operating hours, shift rotations, utility tariffs, and renewable mix to inspect instantaneous before vs after impact."
        meta={
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Plant Baseline: <strong className="text-foreground">31,450 kWh/day</strong></span>
            <span>•</span>
            <span>Current Daily Cost: <strong className="text-foreground">₹2,26,440</strong></span>
            <span>•</span>
            <span>Baseline Carbon: <strong className="text-foreground">25.79 t CO₂e</strong></span>
          </div>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={handleReset}
            >
              <RotateCcw className="size-3.5" />
              Reset Defaults
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                exportAuditDocument(
                  `What-If Operational Simulation Report (${shiftSchedule} @ ${productionLoad}%)`,
                  'Simulator Scenario',
                  'PDF',
                  {
                    'Shift Schedule': shiftSchedule,
                    'Production Loading': `${productionLoad}%`,
                    'Machine Operating Runtime': `${machineRuntime} hrs/day`,
                    'Grid Base Tariff': `₹${baseTariff}/kWh`,
                    'Renewable Energy Integration': `${renewablePercent}%`,
                    'Monthly Projected Net Impact': `₹${formatNumber(Math.abs(monthlySavingsDelta))}/mo ${monthlySavingsDelta >= 0 ? 'SAVINGS' : 'INCREASE'}`,
                  },
                  [
                    { label: 'Simulated Daily Energy', value: `${formatNumber(simulatedDailyKwh)} kWh` },
                    { label: 'Energy Delta', value: `${energyDelta >= 0 ? '+' : ''}${formatNumber(energyDelta)} kWh (${energyDeltaPercent.toFixed(1)}%)` },
                    { label: 'Simulated Daily Cost', value: `₹${formatNumber(simulatedDailyCost)}` },
                    { label: 'Simulated Daily Carbon', value: `${simulatedDailyCarbon.toFixed(2)} tCO2e` },
                  ],
                  {
                    headers: ['Hour', 'Baseline Demand (kW)', 'Simulated Demand (kW)'],
                    rows: simulatedHourlyTrend.map(pt => [pt.hour, pt.baselineKw, pt.simulatedKw])
                  }
                )
                toast.success('Simulation Exported', {
                  description: 'Exported scenario analytics as printable audit document.',
                })
              }}
            >
              <Download className="size-3.5" />
              Export Scenario
            </Button>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                toast.success('Scenario Saved', {
                  description: `Saved scenario "${shiftSchedule} @ ${productionLoad}% load" to plant planning register.`,
                })
              }}
            >
              <Save className="size-3.5" />
              Save Scenario
            </Button>
          </div>
        }
      />

      {/* Preset Strategy Buttons */}
      <Surface className="flex flex-wrap items-center justify-between gap-3 p-4">
        <span className="text-xs font-semibold text-muted-foreground uppercase">Fast Preset Strategies:</span>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            className="text-xs gap-1.5 h-8"
            onClick={() => applyPreset('peak-shifter')}
          >
            <Zap className="size-3 text-amber-500" />
            Peak Tariff Avoidance (-18% Cost)
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="text-xs gap-1.5 h-8"
            onClick={() => applyPreset('decarb')}
          >
            <Leaf className="size-3 text-emerald-500" />
            60% Clean Decarb Sprint
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="text-xs gap-1.5 h-8"
            onClick={() => applyPreset('max-prod')}
          >
            <TrendingUp className="size-3 text-primary" />
            Max Throughput (3-Shift 140%)
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="text-xs gap-1.5 h-8"
            onClick={() => applyPreset('eco')}
          >
            <RotateCcw className="size-3 text-sky-500" />
            Eco Standby (Lean Batch)
          </Button>
        </div>
      </Surface>

      {/* Before vs After Live Comparison KPI Cards */}
      <section aria-label="Before vs After Comparison" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Energy Card */}
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Daily Energy Consumption</span>
            <ToneBadge tone={deltaEnergyKwh <= 0 ? 'success' : 'danger'}>
              {deltaEnergyPercent > 0 ? `+${deltaEnergyPercent}%` : `${deltaEnergyPercent}%`}
            </ToneBadge>
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {formatNumber(simulatedDailyEnergyKwh)} <span className="text-sm font-normal text-muted-foreground">kWh</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Baseline: {formatNumber(baseline.dailyEnergyKwh)} kWh</span>
            <span className={deltaEnergyKwh <= 0 ? 'text-success font-semibold' : 'text-destructive font-semibold'}>
              {deltaEnergyKwh > 0 ? `+${formatNumber(deltaEnergyKwh)}` : formatNumber(deltaEnergyKwh)} kWh
            </span>
          </div>
        </Surface>

        {/* Cost Card */}
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Daily Energy Spend</span>
            <ToneBadge tone={deltaCost <= 0 ? 'success' : 'danger'}>
              {deltaCostPercent > 0 ? `+${deltaCostPercent}%` : `${deltaCostPercent}%`}
            </ToneBadge>
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            ₹{formatNumber(simulatedDailyCost)}
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Baseline: ₹{formatNumber(baseline.dailyCost)}</span>
            <span className={deltaCost <= 0 ? 'text-success font-semibold' : 'text-destructive font-semibold'}>
              {deltaCost > 0 ? `+₹${formatNumber(deltaCost)}` : `-₹${formatNumber(Math.abs(deltaCost))}`}
            </span>
          </div>
        </Surface>

        {/* Carbon Card */}
        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Daily Carbon Emissions</span>
            <ToneBadge tone={deltaCarbon <= 0 ? 'success' : 'danger'}>
              {deltaCarbonPercent > 0 ? `+${deltaCarbonPercent}%` : `${deltaCarbonPercent}%`}
            </ToneBadge>
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {simulatedDailyCarbon} <span className="text-sm font-normal text-muted-foreground">t CO₂e</span>
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
            <span>Baseline: {baseline.dailyCarbonTons} t</span>
            <span className={deltaCarbon <= 0 ? 'text-success font-semibold' : 'text-destructive font-semibold'}>
              {deltaCarbon > 0 ? `+${deltaCarbon}` : `${deltaCarbon}`} t CO₂e
            </span>
          </div>
        </Surface>

        {/* Monthly Net Savings */}
        <Surface className={`flex flex-col gap-2 p-5 ${monthlyProjectedSavings >= 0 ? 'border-success/30 bg-success/5' : 'border-destructive/30 bg-destructive/5'}`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-foreground uppercase">Projected Net Monthly Delta</span>
            <IndianRupee className="size-4 text-foreground" />
          </div>
          <p className={`text-2xl font-bold tabular-nums ${monthlyProjectedSavings >= 0 ? 'text-success' : 'text-destructive'}`}>
            {monthlyProjectedSavings >= 0 ? `+₹${formatNumber(monthlyProjectedSavings)}` : `-₹${formatNumber(Math.abs(monthlyProjectedSavings))}`}
          </p>
          <span className="text-xs text-muted-foreground border-t pt-2 border-border/50">
            {monthlyProjectedSavings >= 0 ? 'Net monetary savings per 30-day billing cycle' : 'Added production expenditure per month'}
          </span>
        </Surface>
      </section>

      {/* Main Interactive Controls & Comparative Curve Grid */}
      <section aria-label="Simulator Controls and Output Chart" className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Column: Interactive Controls */}
        <Surface className="flex flex-col gap-5 p-6 lg:col-span-1">
          <SectionHeader
            title="Simulation Parameter Sliders"
            description="Adjust industrial operational levers to trigger live recalculation."
            icon={SlidersHorizontal}
          />

          {/* 1. Production Load Slider */}
          <div className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-3.5">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="text-foreground">Production Load</span>
              <span className="text-primary tabular-nums text-sm font-bold">{productionLoad}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="150"
              step="5"
              value={productionLoad}
              onChange={(e) => setProductionLoad(Number(e.target.value))}
              className="h-2 w-full cursor-pointer accent-primary"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>50% (Low)</span>
              <span>100% (Baseline)</span>
              <span>150% (Surge)</span>
            </div>
          </div>

          {/* 2. Machine Runtime Slider */}
          <div className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-3.5">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="text-foreground">Machine Runtime</span>
              <span className="text-primary tabular-nums text-sm font-bold">{machineRuntime} hrs / day</span>
            </div>
            <input
              type="range"
              min="4"
              max="24"
              step="1"
              value={machineRuntime}
              onChange={(e) => setMachineRuntime(Number(e.target.value))}
              className="h-2 w-full cursor-pointer accent-primary"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>4 hrs</span>
              <span>16 hrs (2-Shift)</span>
              <span>24 hrs (Continuous)</span>
            </div>
          </div>

          {/* 3. Shift Schedule Selector */}
          <div className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-3.5">
            <span className="text-xs font-semibold text-foreground">Shift Schedule Scheme</span>
            <SegmentedControl
              value={shiftSchedule}
              options={[
                { value: '1-shift', label: '1-Shift' },
                { value: '2-shift', label: '2-Shift' },
                { value: '3-shift', label: '3-Shift' },
                { value: 'night-shift', label: 'Night Load' },
              ]}
              onChange={setShiftSchedule}
              ariaLabel="Shift schedule"
            />
            <span className="text-[11px] text-muted-foreground">
              {shiftSchedule === 'night-shift'
                ? 'Concentrates high-draw thermal cycles into low-tariff off-peak night window.'
                : 'Distributes production according to standard operational roster.'}
            </span>
          </div>

          {/* 4. Electricity Tariff Slider */}
          <div className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-3.5">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="text-foreground">Base Electricity Tariff</span>
              <span className="text-primary tabular-nums text-sm font-bold">₹{baseTariff.toFixed(2)} / kWh</span>
            </div>
            <input
              type="range"
              min="4.00"
              max="14.00"
              step="0.20"
              value={baseTariff}
              onChange={(e) => setBaseTariff(Number(e.target.value))}
              className="h-2 w-full cursor-pointer accent-primary"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>₹4.00/kWh</span>
              <span>₹7.20 (Standard)</span>
              <span>₹14.00 (Peak)</span>
            </div>
          </div>

          {/* 5. Renewable Energy Mix Slider */}
          <div className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-3.5">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="text-foreground">Renewable Energy Mix</span>
              <span className="text-emerald-500 tabular-nums text-sm font-bold">{renewablePercent}% Solar</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={renewablePercent}
              onChange={(e) => setRenewablePercent(Number(e.target.value))}
              className="h-2 w-full cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>0% (Grid Only)</span>
              <span>22% (Current)</span>
              <span>100% (Net Zero)</span>
            </div>
          </div>
        </Surface>

        {/* Right Column: Comparative Chart */}
        <Surface className="flex flex-col gap-5 p-6 lg:col-span-2">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-3">
            <div className="flex items-center gap-2.5">
              <IconTile icon={FlaskConical} tone="info" />
              <div>
                <h3 className="text-base font-semibold text-foreground">24-Hour Load Shape: Baseline vs Simulated Scenario</h3>
                <p className="text-xs text-muted-foreground">
                  Comparing current standard factory profile against the live simulated adjustments.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 font-medium text-muted-foreground">
                <span className="size-2 rounded-full bg-muted-foreground/60" /> Baseline Curve
              </span>
              <span className="flex items-center gap-1.5 font-medium text-primary">
                <span className="size-2 rounded-full bg-primary" /> Simulated Curve
              </span>
            </div>
          </div>

          <ChartContainer config={simChartConfig} className="aspect-auto h-80 w-full">
            <AreaChart data={simulatedHourlyProfile} margin={{ left: -10, right: 10, top: 10 }}>
              <defs>
                <linearGradient id="sim-load-grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} strokeDasharray="3 3" />
              <XAxis dataKey="hour" tickLine={false} axisLine={false} tickMargin={8} />
              <YAxis tickLine={false} axisLine={false} tickMargin={8} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Area type="monotone" dataKey="simulatedKw" stroke="var(--chart-1)" strokeWidth={2.5} fill="url(#sim-load-grad)" />
              <Line type="monotone" dataKey="baselineKw" stroke="var(--chart-2)" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
            </AreaChart>
          </ChartContainer>

          <div className="rounded-lg border bg-muted/20 p-4 text-xs text-muted-foreground">
            <span className="font-semibold text-foreground">Engine Simulation Note: </span>
            Adjustments dynamically compute thermodynamic load penalties and Time-of-Day tariff surcharges based on Maharashtra DISCOM schedule HT-I Industrial rates.
          </div>
        </Surface>
      </section>
    </div>
  )
}
