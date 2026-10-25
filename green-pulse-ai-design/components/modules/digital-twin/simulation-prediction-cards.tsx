'use client'

import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Clock,
  Cpu,
  Flame,
  Gauge,
  HeartPulse,
  Hourglass,
  IndianRupee,
  Leaf,
  ShieldAlert,
  Sparkles,
  Zap,
} from 'lucide-react'

import { AnimatedNumber } from '@/components/shared/animated-number'
import { ToneBadge } from '@/components/shared/tone-badge'
import { formatNumber } from '@/lib/format'
import type { MachineSimulationResult } from '@/types/digital-twin'

interface SimulationPredictionCardsProps {
  result: MachineSimulationResult
}

export function SimulationPredictionCards({ result }: SimulationPredictionCardsProps) {
  const getRiskTone = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'severe':
        return 'danger'
      case 'high':
        return 'warning'
      case 'moderate':
        return 'info'
      default:
        return 'success'
    }
  }

  const riskTone = getRiskTone(result.operationalRisk)

  return (
    <div className="flex flex-col gap-3.5">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/60 pb-2.5">
        <div className="flex items-center gap-2">
          <Sparkles className="size-4 text-primary animate-pulse" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
            Live AI Multi-Variable Predictions (Real-Time Physics & Neural Inference)
          </h4>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-muted-foreground">
          <span>Confidence:</span>
          <span className="font-bold text-emerald-400">
            {Math.round(result.confidenceScore * 100)}%
          </span>
          <span className="text-border">·</span>
          <span>Model: {result.modelVersion}</span>
          <span className="text-border">·</span>
          <span className="text-emerald-400 font-semibold">Zero-Latency Reactive</span>
        </div>
      </div>

      {/* 12 Live AI Metric Cards Grid - Spacious, on-page layout */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {/* 1. Energy Consumption */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <Zap className="size-3.5 text-primary shrink-0" /> Energy
            </span>
            {result.deltaEnergyPercent !== 0 && (
              <span className={`text-[10px] font-mono shrink-0 px-1 py-0.5 rounded ${
                result.deltaEnergyPercent < 0 ? 'bg-emerald-500/10 text-emerald-400 font-semibold' : 'bg-amber-500/10 text-amber-400 font-semibold'
              }`}>
                {result.deltaEnergyPercent < 0 ? '▼' : '▲'} {Math.abs(result.deltaEnergyPercent)}%
              </span>
            )}
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.predictedEnergyKwh} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">kWh/day</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Baseline: {formatNumber(result.baselineEnergyKwh, 0)} kWh
          </p>
        </div>

        {/* 2. Electricity Cost */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <IndianRupee className="size-3.5 text-amber-400 shrink-0" /> Daily Cost
            </span>
            {result.deltaCostPercent !== 0 && (
              <span className={`text-[10px] font-mono shrink-0 px-1 py-0.5 rounded ${
                result.deltaCostPercent < 0 ? 'bg-emerald-500/10 text-emerald-400 font-semibold' : 'bg-amber-500/10 text-amber-400 font-semibold'
              }`}>
                {result.deltaCostPercent < 0 ? '▼' : '▲'} {Math.abs(result.deltaCostPercent)}%
              </span>
            )}
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-sm font-semibold text-muted-foreground">₹</span>
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.predictedCostInr} />
            </span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Tariff @ ₹7.20/kWh
          </p>
        </div>

        {/* 3. Carbon Emissions */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <Leaf className="size-3.5 text-emerald-400 shrink-0" /> Carbon
            </span>
            {result.deltaCarbonPercent !== 0 && (
              <span className={`text-[10px] font-mono shrink-0 px-1 py-0.5 rounded ${
                result.deltaCarbonPercent < 0 ? 'bg-emerald-500/10 text-emerald-400 font-semibold' : 'bg-amber-500/10 text-amber-400 font-semibold'
              }`}>
                {result.deltaCarbonPercent < 0 ? '▼' : '▲'} {Math.abs(result.deltaCarbonPercent)}%
              </span>
            )}
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.predictedCarbonKg} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">kg CO₂e</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Scope 2 GHG offset
          </p>
        </div>

        {/* 4. Machine Health */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <HeartPulse className="size-3.5 text-rose-400 shrink-0" /> Health
            </span>
            <span className={`text-[10px] font-mono shrink-0 px-1 py-0.5 rounded ${
              result.machineHealthPercent > 85 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
            }`}>
              {result.machineHealthPercent > 85 ? 'Optimal' : 'Caution'}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className={`text-lg sm:text-xl font-bold tabular-nums ${
              result.machineHealthPercent > 85
                ? 'text-emerald-400'
                : result.machineHealthPercent > 70
                  ? 'text-amber-400'
                  : 'text-rose-400'
            }`}>
              <AnimatedNumber value={result.machineHealthPercent} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">%</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            ISO 10816 Vibration
          </p>
        </div>

        {/* 5. Equipment Efficiency */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <Gauge className="size-3.5 text-sky-400 shrink-0" /> Efficiency
            </span>
            <span className="text-[10px] font-mono text-muted-foreground">
              PF {result.powerFactor.toFixed(2)}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.equipmentEfficiencyPercent} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">%</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Thermodynamic ratio
          </p>
        </div>

        {/* 6. Failure Probability */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <ShieldAlert className="size-3.5 text-rose-400 shrink-0" /> Failure Risk
            </span>
            <span className="text-[10px] font-mono text-muted-foreground">72h Window</span>
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className={`text-lg sm:text-xl font-bold tabular-nums ${
              result.failureProbabilityPercent > 25
                ? 'text-rose-400'
                : result.failureProbabilityPercent > 10
                  ? 'text-amber-400'
                  : 'text-emerald-400'
            }`}>
              <AnimatedNumber value={result.failureProbabilityPercent} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">%</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Thermal excursion risk
          </p>
        </div>

        {/* 7. Peak Demand Contribution */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <Cpu className="size-3.5 text-primary shrink-0" /> Peak Demand
            </span>
            <span className="text-[10px] font-mono text-muted-foreground">MDI</span>
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.peakDemandContributionKw} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">kW</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Max electrical spike
          </p>
        </div>

        {/* 8. Expected Downtime */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <Hourglass className="size-3.5 text-amber-400 shrink-0" /> Downtime
            </span>
            <span className="text-[10px] font-mono text-muted-foreground">MTTR</span>
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.expectedDowntimeHours} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">Hours</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Expected outage hours
          </p>
        </div>

        {/* 9. Remaining Useful Life (RUL) */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <Clock className="size-3.5 text-primary shrink-0" /> RUL Estimate
            </span>
            <span className="text-[10px] font-mono text-muted-foreground">Fatigue</span>
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.remainingUsefulLifeDays} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">Days</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Until mandatory PM
          </p>
        </div>

        {/* 10. Operational Risk */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <AlertTriangle className="size-3.5 text-amber-400 shrink-0" /> Op Risk
            </span>
            <ToneBadge tone={riskTone} label={result.operationalRisk} />
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className={`text-base sm:text-lg font-bold ${
              result.operationalRisk === 'Severe'
                ? 'text-rose-400'
                : result.operationalRisk === 'High'
                  ? 'text-amber-400'
                  : 'text-emerald-400'
            }`}>
              {result.operationalRisk}
            </span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Yield & safety index
          </p>
        </div>

        {/* 11. Overall Equipment Effectiveness (OEE) */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <Activity className="size-3.5 text-emerald-400 shrink-0" /> OEE Index
            </span>
            <span className="text-[10px] font-mono text-muted-foreground">&gt;85% W-Class</span>
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.oeePercent} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">%</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            Avail × Perf × Qual
          </p>
        </div>

        {/* 12. Active Power & Rating */}
        <div className="rounded-xl border border-border/80 bg-card/80 p-3.5 flex flex-col justify-between shadow-xs min-w-0">
          <div className="flex items-center justify-between gap-1 text-muted-foreground">
            <span className="text-xs font-medium flex items-center gap-1.5 truncate">
              <Flame className="size-3.5 text-primary shrink-0" /> Active Draw
            </span>
            <span className="text-[10px] font-mono text-muted-foreground">
              {Math.round(result.temperatureC)}°C
            </span>
          </div>
          <div className="mt-2 flex flex-wrap items-baseline gap-1">
            <span className="text-lg sm:text-xl font-bold text-foreground tabular-nums">
              <AnimatedNumber value={result.predictedPowerKw} />
            </span>
            <span className="text-xs text-muted-foreground font-mono">kW</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            At {result.voltageV}V / {result.currentA}A
          </p>
        </div>
      </div>
    </div>
  )
}
