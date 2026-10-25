'use client'

import {
  Activity,
  AlertTriangle,
  Boxes,
  CheckCircle2,
  Cpu,
  Flame,
  Gauge,
  PaintRoller,
  PowerOff,
  SlidersHorizontal,
  Sparkles,
  Waves,
  Wind,
  Wrench,
  Zap,
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { MeterBar } from '@/components/shared/meter-bar'
import { ToneBadge } from '@/components/shared/tone-badge'
import { formatNumber } from '@/lib/format'
import type { MachineTelemetry } from '@/types/modules'
import type { MachineSimulationResult } from '@/types/digital-twin'

interface MachineCardProps {
  machine: MachineTelemetry
  simulationResult?: MachineSimulationResult
  isSelected: boolean
  onClick: () => void
}

export function MachineCard({
  machine,
  simulationResult,
  isSelected,
  onClick,
}: MachineCardProps) {
  // Machine Icon Resolver
  const getIcon = (id: string) => {
    const clean = id.toLowerCase()
    if (clean.includes('compressor')) return Wind
    if (clean.includes('furnace')) return Flame
    if (clean.includes('cnc') || clean.includes('lathe') || clean.includes('milling')) return Cpu
    if (clean.includes('pump') || clean.includes('water')) return Waves
    if (clean.includes('paint')) return PaintRoller
    if (clean.includes('assembly')) return Boxes
    return Activity
  }

  const Icon = getIcon(machine.id)

  // Current interactive values (simulation if active, else telemetry)
  const currentState = simulationResult?.machineState || (machine.status === 'fault' ? 'fault' : machine.status === 'idle' ? 'idle' : machine.status === 'warning' ? 'running' : 'running')
  const currentPowerKw = simulationResult ? simulationResult.predictedPowerKw : machine.powerKw
  const currentTemp = simulationResult ? simulationResult.temperatureC : machine.temperatureC
  const currentHealth = simulationResult ? simulationResult.machineHealthPercent : machine.healthScore
  const currentFailureProb = simulationResult ? simulationResult.failureProbabilityPercent : machine.failureProbability72h
  const thermalThreshold = machine.thermalThresholdC || 85
  const isOverheating = currentTemp > thermalThreshold
  const isHighEnergy = currentPowerKw > machine.ratedPowerKw * 0.82

  // Lightweight visual theme mappings according to industrial specifications
  const getVisualStyles = () => {
    if (currentState === 'emergency_stop') {
      return {
        bg: 'bg-zinc-900/90 dark:bg-zinc-950/90 grayscale opacity-85',
        border: 'border-zinc-700 hover:border-zinc-500',
        glow: 'shadow-[0_0_16px_rgba(113,113,122,0.3)]',
        badge: <ToneBadge tone="neutral" label="Emergency Stop" />,
        accentText: 'text-zinc-400',
        ring: 'ring-1 ring-zinc-700',
        iconBg: 'bg-zinc-800 text-zinc-400 border-zinc-700',
      }
    }

    if (currentState === 'fault') {
      return {
        bg: 'bg-rose-500/10 dark:bg-rose-950/30',
        border: 'border-rose-500 animate-status-pulse',
        glow: 'shadow-[0_0_24px_-2px_rgba(244,63,94,0.5)]',
        badge: <ToneBadge tone="danger" label="Critical Fault" />,
        accentText: 'text-rose-400',
        ring: 'ring-2 ring-rose-500/60',
        iconBg: 'bg-rose-500/20 text-rose-400 border-rose-500/50',
      }
    }

    if (currentState === 'maintenance') {
      return {
        bg: 'bg-amber-500/10 dark:bg-amber-950/25',
        border: 'border-amber-500/70 hover:border-amber-500',
        glow: 'shadow-[0_0_20px_-3px_rgba(245,158,11,0.4)]',
        badge: (
          <Badge variant="outline" className="gap-1 border-amber-500/50 bg-amber-500/10 text-amber-400 text-[10px]">
            <Wrench className="size-3 animate-spin duration-3000" /> Maintenance
          </Badge>
        ),
        accentText: 'text-amber-400',
        ring: 'ring-1 ring-amber-500/40',
        iconBg: 'bg-amber-500/20 text-amber-400 border-amber-500/50',
      }
    }

    if (currentState === 'idle') {
      return {
        bg: 'bg-sky-500/10 dark:bg-sky-950/25 opacity-90',
        border: 'border-sky-500/50 hover:border-sky-400',
        glow: 'shadow-[0_0_18px_-3px_rgba(14,165,233,0.35)]',
        badge: <ToneBadge tone="info" label="Idle Standby" />,
        accentText: 'text-sky-400',
        ring: 'ring-1 ring-sky-500/30',
        iconBg: 'bg-sky-500/20 text-sky-400 border-sky-500/40',
      }
    }

    // High temperature glowing orange/red
    if (isOverheating) {
      return {
        bg: 'bg-gradient-to-br from-orange-500/15 via-red-500/10 to-card dark:from-orange-950/40 dark:to-red-950/20',
        border: 'border-orange-500/80 hover:border-orange-400 animate-pulse',
        glow: 'shadow-[0_0_26px_rgba(249,115,22,0.45)]',
        badge: <ToneBadge tone="warning" label={`High Temp: ${currentTemp}°C`} />,
        accentText: 'text-orange-400',
        ring: 'ring-2 ring-orange-500/50',
        iconBg: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
      }
    }

    // Default Running (Healthy Green)
    return {
      bg: 'bg-emerald-500/10 dark:bg-emerald-950/25',
      border: 'border-emerald-500/50 hover:border-emerald-400',
      glow: 'shadow-[0_0_20px_-3px_rgba(16,185,129,0.35)]',
      badge: <ToneBadge tone="success" label="Healthy (Running)" />,
      accentText: 'text-emerald-400',
      ring: 'ring-1 ring-emerald-500/30',
      iconBg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
    }
  }

  const styles = getVisualStyles()
  const powerUsagePercent = Math.min(100, Math.round((currentPowerKw / Math.max(1, machine.ratedPowerKw)) * 100))

  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`Interactive Digital Twin for ${machine.name}`}
      className={`group relative cursor-pointer rounded-card border-2 p-5 transition-all duration-200 select-none ${styles.bg} ${styles.border} ${
        isSelected ? `ring-2 ring-primary ${styles.glow}` : 'hover:-translate-y-1 hover:shadow-card-hover'
      }`}
    >
      {/* Top Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className={`size-11 rounded-tile flex items-center justify-center border ${styles.iconBg} shadow-sm transition-transform group-hover:scale-105`}>
            {currentState === 'emergency_stop' ? (
              <PowerOff className="size-5 text-zinc-400" />
            ) : currentState === 'maintenance' ? (
              <Wrench className="size-5 text-amber-400" />
            ) : (
              <Icon className="size-5" />
            )}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-foreground text-base tracking-tight truncate group-hover:text-primary transition-colors">
                {machine.name}
              </h3>
            </div>
            <p className="text-xs text-muted-foreground truncate font-mono">
              {machine.code} · {machine.zone}
            </p>
          </div>
        </div>

        <div className="shrink-0">{styles.badge}</div>
      </div>

      {/* Real-time telemetry indicators */}
      <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
        {/* Power Telemetry */}
        <div className={`rounded-lg border border-border/60 bg-card/60 p-2.5 flex flex-col justify-between transition-colors ${
          isHighEnergy ? 'border-amber-500/50 bg-amber-500/5' : ''
        }`}>
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="flex items-center gap-1 text-[11px]">
              <Zap className={`size-3 ${isHighEnergy ? 'text-amber-400 animate-bounce' : 'text-primary'}`} />
              Active Power
            </span>
            {isHighEnergy && (
              <span className="text-[10px] font-semibold text-amber-400 font-mono">PEAK</span>
            )}
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <span className="text-base font-bold text-foreground tabular-nums">
              {formatNumber(currentPowerKw, 1)}
            </span>
            <span className="text-[11px] text-muted-foreground">kW</span>
          </div>
          <MeterBar
            value={powerUsagePercent}
            tone={powerUsagePercent > 85 ? 'warning' : 'success'}
            className="mt-1.5 h-1"
          />
        </div>

        {/* Temperature Telemetry */}
        <div className={`rounded-lg border border-border/60 bg-card/60 p-2.5 flex flex-col justify-between transition-colors ${
          isOverheating ? 'border-red-500/60 bg-red-500/10 animate-pulse' : ''
        }`}>
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="flex items-center gap-1 text-[11px]">
              <Flame className={`size-3 ${isOverheating ? 'text-red-400' : 'text-muted-foreground'}`} />
              Core Temp
            </span>
            <span className="text-[10px] text-muted-foreground font-mono">
              Max {thermalThreshold}°C
            </span>
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <span className={`text-base font-bold tabular-nums ${isOverheating ? 'text-red-400' : 'text-foreground'}`}>
              {Math.round(currentTemp)}
            </span>
            <span className="text-[11px] text-muted-foreground">°C</span>
          </div>
          <MeterBar
            value={Math.min(100, Math.round((currentTemp / (thermalThreshold * 1.25)) * 100))}
            tone={isOverheating ? 'danger' : 'neutral'}
            className="mt-1.5 h-1"
          />
        </div>
      </div>

      {/* Bottom Health & AI Prediction Strip */}
      <div className="mt-3 flex items-center justify-between border-t border-border/50 pt-2.5 text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5 font-medium">
          <span className="text-[11px]">Health:</span>
          <span className={`font-mono font-bold ${
            currentHealth > 85 ? 'text-emerald-400' : currentHealth > 70 ? 'text-amber-400' : 'text-rose-400'
          }`}>
            {currentHealth}%
          </span>
          <span className="text-border">·</span>
          <span className="text-[11px]">Risk:</span>
          <span className={`font-mono text-[11px] ${
            currentFailureProb > 25 ? 'text-rose-400 font-bold' : currentFailureProb > 10 ? 'text-amber-400' : 'text-emerald-400'
          }`}>
            {currentFailureProb}%
          </span>
        </div>

        <Button
          size="sm"
          variant={isSelected ? 'default' : 'outline'}
          className={`h-7 px-2.5 text-xs font-semibold gap-1.5 transition-all ${
            isSelected
              ? 'bg-primary text-primary-foreground shadow-xs'
              : 'hover:bg-primary/10 hover:text-primary hover:border-primary/50'
          }`}
          onClick={(e) => {
            e.stopPropagation()
            onClick()
          }}
        >
          <SlidersHorizontal className="size-3.5" />
          {isSelected ? 'Simulating Below ↓' : 'Simulate Asset ↓'}
        </Button>
      </div>

      {/* Active simulation indicator ribbon */}
      {simulationResult && (
        <div className="absolute top-2 right-2 flex items-center gap-1 rounded bg-primary/20 px-1.5 py-0.5 text-[9px] font-semibold text-primary border border-primary/30">
          <Sparkles className="size-2.5 animate-pulse" /> SIMULATED
        </div>
      )}
    </div>
  )
}
