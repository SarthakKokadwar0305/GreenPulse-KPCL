'use client'

import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  Check,
  CheckCircle2,
  Clock,
  Cpu,
  Flame,
  Gauge,
  History,
  Layers,
  Leaf,
  Maximize2,
  Minimize2,
  Power,
  PowerOff,
  RefreshCw,
  Save,
  ShieldAlert,
  SlidersHorizontal,
  Sparkles,
  Thermometer,
  Wrench,
  X,
  Zap,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { toast } from 'sonner'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Surface } from '@/components/shared/surface'
import { ToneBadge } from '@/components/shared/tone-badge'
import { formatNumber } from '@/lib/format'
import type { MachineTelemetry } from '@/types/modules'
import type {
  MachineSimulationParams,
  MachineState,
  MaintenanceCondition,
} from '@/types/digital-twin'
import { useSimulationSyncStore } from '@/store/simulation-sync-store'
import { SimulationPredictionCards } from './simulation-prediction-cards'
import { AiExplanationsPanel } from './ai-explanations-panel'

interface DigitalTwinControlPanelProps {
  machine?: MachineTelemetry
  allMachines: MachineTelemetry[]
  onSelectMachine: (machineId: string) => void
  onClose: () => void
  onOpenScenarioComparison?: () => void
  onOpenTimeline?: () => void
}

export function DigitalTwinControlPanel({
  machine,
  allMachines,
  onSelectMachine,
  onClose,
  onOpenScenarioComparison,
  onOpenTimeline,
}: DigitalTwinControlPanelProps) {
  const {
    machineSimulations,
    machineResults,
    updateMachineParam,
    saveScenario,
    resetMachineSimulation,
    addTimelineEntry,
    plantState,
  } = useSimulationSyncStore()

  // Scenario modal state
  const [scenarioNameInput, setScenarioNameInput] = useState('')
  const [showSaveModal, setShowSaveModal] = useState(false)

  // Machine temperature range calibration - unconditionally run hook
  const tempRange = useMemo(() => {
    if (!machine) {
      return { min: 15, max: 100, step: 1, default: 40, unit: '°C' }
    }
    const id = machine.id.toLowerCase()
    if (id.includes('furnace')) {
      return { min: 200, max: 1200, step: 10, default: machine.temperatureC || 840, unit: '°C' }
    }
    if (id.includes('compressor')) {
      return { min: 30, max: 130, step: 1, default: machine.temperatureC || 86, unit: '°C' }
    }
    if (id.includes('hvac') || id.includes('chiller')) {
      return { min: 2, max: 40, step: 0.5, default: machine.temperatureC || 14, unit: '°C' }
    }
    if (id.includes('cnc') || id.includes('lathe')) {
      return { min: 20, max: 90, step: 1, default: machine.temperatureC || 42, unit: '°C' }
    }
    return { min: 15, max: 100, step: 1, default: machine.temperatureC || 40, unit: '°C' }
  }, [machine])

  if (!machine) return null

  // Current simulation parameters from store or initialize
  const currentParams: MachineSimulationParams = machineSimulations[machine.id] || {
    machineId: machine.id,
    machineState: machine.status === 'fault' ? 'fault' : machine.status === 'idle' ? 'idle' : 'running',
    runtimeHours: machine.runtimeHoursShift || 16,
    productionLoadPercent: 85,
    motorSpeedPercent: 85,
    temperatureC: machine.temperatureC || tempRange.default,
    voltageV: machine.voltage?.lineToLine || 400,
    currentA: machine.current?.l1 || Math.round(machine.ratedPowerKw * 1.45),
    powerFactor: machine.powerFactor || 0.92,
    renewableSharePercent: plantState.renewablePercent || 22,
    maintenanceCondition: machine.healthScore > 90 ? 'excellent' : 'good',
  }

  const simulationResult = machineResults[machine.id] || {
    ...currentParams,
    machineName: machine.name,
    machineCode: machine.code,
    predictedPowerKw: machine.powerKw,
    predictedEnergyKwh: machine.energyTodayKwh || machine.powerKw * 16,
    predictedCostInr: Math.round((machine.energyTodayKwh || machine.powerKw * 16) * 0.78 * 7.20),
    predictedCarbonKg: Number(((machine.energyTodayKwh || machine.powerKw * 16) * 0.78 * 0.82).toFixed(1)),
    machineHealthPercent: machine.healthScore,
    equipmentEfficiencyPercent: 94.5,
    failureProbabilityPercent: machine.failureProbability72h,
    peakDemandContributionKw: Number((machine.powerKw * 1.15).toFixed(1)),
    expectedDowntimeHours: 0.8,
    remainingUsefulLifeDays: 45,
    operationalRisk: 'Low' as const,
    oeePercent: 86.4,
    confidenceScore: 0.96,
    explanations: [
      'Operating at standard baseline: Parameters are currently nominal with harmonic distortion within IEEE 519 standards.',
    ],
    prescriptiveInsights: [
      'Running this machine at 85% load instead of 100% reduces energy by 11%.',
      'Increasing renewable usage to 35% reduces carbon by 18%.',
      'Reducing runtime by one hour saves ₹1,450/day.',
      'Maintenance today avoids a predicted failure within 12 days.',
    ],
    baselineEnergyKwh: machine.energyTodayKwh || machine.powerKw * 16,
    deltaEnergyPercent: 0,
    baselineCostInr: Math.round((machine.energyTodayKwh || machine.powerKw * 16) * 0.78 * 7.20),
    deltaCostPercent: 0,
    baselineCarbonKg: Number(((machine.energyTodayKwh || machine.powerKw * 16) * 0.78 * 0.82).toFixed(1)),
    deltaCarbonPercent: 0,
    baselineHealthScore: machine.healthScore,
    deltaHealthPercent: 0,
    hourlyPowerProfile: [],
    timestamp: new Date().toISOString(),
    modelVersion: '2.4.0-twin',
  }

  // Handle immediate interactive parameter update
  const handleParamChange = (partial: Partial<MachineSimulationParams>) => {
    updateMachineParam(machine.id, partial, machine)
  }

  // Log to timeline on significant state/load changes
  const handleStateChange = async (newState: MachineState) => {
    const prev = currentParams.machineState
    handleParamChange({ machineState: newState })
    await addTimelineEntry({
      timestamp: new Date().toLocaleTimeString(),
      machineId: machine.id,
      machineName: machine.name,
      changedParameters: [`State: ${prev} → ${newState}`],
      previousValues: { state: prev },
      predictedValues: { state: newState, power_kw: simulationResult.predictedPowerKw },
      user: 'Industrial Operator',
    })
    toast.info(`Machine state updated to "${newState.toUpperCase()}"`, {
      description: 'Floor card animation and multi-variable AI predictions updated in real time.',
    })
  }

  // Save Scenario handler
  const handleSaveScenario = () => {
    const name = scenarioNameInput.trim() || `Scenario ${machine.code} - ${new Date().toLocaleTimeString()}`
    saveScenario(name, `Interactive digital twin simulation on ${machine.name}`, machine.id)
    setShowSaveModal(false)
    setScenarioNameInput('')
    toast.success(`Saved Simulation Scenario "${name}"`, {
      description: 'You can now compare this scenario side-by-side with other operating points.',
    })
  }

  const statesList: { key: MachineState; label: string; tone: 'success' | 'info' | 'warning' | 'danger' | 'neutral' }[] = [
    { key: 'running', label: 'Running', tone: 'success' },
    { key: 'idle', label: 'Idle', tone: 'info' },
    { key: 'maintenance', label: 'Maintenance', tone: 'warning' },
    { key: 'fault', label: 'Fault', tone: 'danger' },
    { key: 'emergency_stop', label: 'Emergency Stop', tone: 'neutral' },
  ]

  const conditionsList: { key: MaintenanceCondition; label: string }[] = [
    { key: 'excellent', label: 'Excellent' },
    { key: 'good', label: 'Good' },
    { key: 'warning', label: 'Warning' },
    { key: 'critical', label: 'Critical' },
  ]

  return (
    <Surface
      id="simulation-studio"
      className="relative flex flex-col gap-6 rounded-2xl border-2 border-primary/40 bg-card p-6 shadow-xl transition-all"
    >
      {/* Studio Header Bar */}
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border pb-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="size-12 rounded-xl flex items-center justify-center bg-primary/10 border border-primary/30 text-primary">
            <SlidersHorizontal className="size-6 animate-pulse" />
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs font-bold text-primary px-2 py-0.5 rounded bg-primary/10 border border-primary/30">
                {machine.code}
              </span>
              <ToneBadge
                tone={
                  currentParams.machineState === 'fault'
                    ? 'danger'
                    : currentParams.machineState === 'idle'
                      ? 'info'
                      : currentParams.machineState === 'maintenance'
                        ? 'warning'
                        : currentParams.machineState === 'emergency_stop'
                          ? 'neutral'
                          : 'success'
                }
                label={currentParams.machineState.toUpperCase()}
              />
              <span className="text-xs text-muted-foreground font-medium">{machine.zone}</span>
              <span className="text-xs text-muted-foreground">·</span>
              <span className="text-xs font-mono text-emerald-400 flex items-center gap-1 font-semibold">
                <span className="size-2 rounded-full bg-emerald-500 animate-ping" />
                Live In-Page Twin Studio
              </span>
            </div>

            <h2 className="mt-1 text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <span>{machine.name}</span>
              <span className="text-muted-foreground font-normal text-base">· Cyber-Physical Simulator</span>
            </h2>
            <p className="text-xs text-muted-foreground">
              Adjust parameters below to see the machine card animate above in real-time without obscuring the factory floor.
            </p>
          </div>
        </div>

        {/* Machine Quick Switcher & Studio Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Quick Switch Dropdown */}
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground bg-muted/40 border border-border px-2 py-1 rounded-lg">
            <span className="font-medium text-foreground">Active Asset:</span>
            <select
              value={machine.id}
              onChange={(e) => onSelectMachine(e.target.value)}
              className="bg-transparent text-foreground font-semibold focus:outline-none cursor-pointer"
            >
              {allMachines.map((m) => (
                <option key={m.id} value={m.id} className="bg-card text-foreground">
                  {m.code} - {m.name}
                </option>
              ))}
            </select>
          </div>

          <Button
            variant="outline"
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => {
              resetMachineSimulation(machine.id, machine)
              toast.success('Simulation Reset', {
                description: `Reset ${machine.name} to current live SCADA telemetry baseline.`,
              })
            }}
          >
            <RefreshCw className="size-3.5" />
            Reset
          </Button>

          <Button
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => setShowSaveModal(true)}
          >
            <Save className="size-3.5" />
            Save Scenario
          </Button>

          {onOpenScenarioComparison && (
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5 text-primary border-primary/30"
              onClick={onOpenScenarioComparison}
            >
              <Layers className="size-3.5" />
              Compare Scenarios
            </Button>
          )}

          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            title="Deselect machine"
          >
            <X className="size-5" />
          </button>
        </div>
      </div>

      {/* SECTION 1: Full-Width Live AI Predictions (12 Metrics with generous room) */}
      <SimulationPredictionCards result={simulationResult} />

      {/* SECTION 2: Industrial Machine Physical Levers */}
      <div className="flex flex-col gap-4 rounded-xl border border-border/80 bg-card/60 p-5 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/60 pb-3">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="size-4 text-primary" />
            <h3 className="text-sm font-bold text-foreground tracking-tight">
              Operational Control Levers & Physics Envelope
            </h3>
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono">
            <span>Nameplate Rating: <strong className="text-foreground">{machine.ratedPowerKw} kW</strong></span>
            <span>·</span>
            <span>Thermal Limit: <strong className="text-foreground">{machine.thermalThresholdC || 85}°C</strong></span>
          </div>
        </div>

        {/* 1. Machine State Selector */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-foreground">Machine Operating Mode</span>
            <span className="text-muted-foreground">Immediate contactor & thermal state actuation</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
            {statesList.map((st) => (
              <button
                key={st.key}
                type="button"
                onClick={() => handleStateChange(st.key)}
                className={`flex items-center justify-center gap-2 rounded-xl border p-2.5 text-xs font-semibold transition-all ${
                  currentParams.machineState === st.key
                    ? 'border-primary bg-primary text-primary-foreground shadow-md ring-2 ring-primary/40'
                    : 'border-border/60 bg-muted/20 text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                }`}
              >
                {st.key === 'emergency_stop' ? (
                  <PowerOff className="size-3.5 shrink-0" />
                ) : st.key === 'maintenance' ? (
                  <Wrench className="size-3.5 shrink-0" />
                ) : (
                  <span className={`size-2 rounded-full ${
                    st.key === 'running' ? 'bg-emerald-400' : st.key === 'idle' ? 'bg-sky-400' : 'bg-rose-400'
                  }`} />
                )}
                <span className="truncate">{st.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Sliders Grid: 2 or 4 Columns with plenty of room */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
          {/* Runtime Hours: 0 - 24 */}
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-background/50 p-3.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground flex items-center gap-1.5">
                <Clock className="size-3.5 text-primary" /> Runtime Hours
              </span>
              <span className="font-mono font-bold text-primary text-sm">
                {currentParams.runtimeHours} <span className="text-xs font-normal text-muted-foreground">h/day</span>
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={24}
              step={0.5}
              value={currentParams.runtimeHours}
              onChange={(e) => handleParamChange({ runtimeHours: parseFloat(e.target.value) })}
              className="w-full accent-primary h-2 rounded-lg bg-muted cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>0h (Halt)</span>
              <span>16h (2-Shift)</span>
              <span>24h (24x7)</span>
            </div>
          </div>

          {/* Production Load: 0 - 100% */}
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-background/50 p-3.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground flex items-center gap-1.5">
                <Gauge className="size-3.5 text-primary" /> Production Load
              </span>
              <span className="font-mono font-bold text-primary text-sm">
                {currentParams.productionLoadPercent}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              step={1}
              value={currentParams.productionLoadPercent}
              onChange={(e) => handleParamChange({ productionLoadPercent: parseFloat(e.target.value) })}
              className="w-full accent-primary h-2 rounded-lg bg-muted cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>0% (No Load)</span>
              <span>85% (Optimal)</span>
              <span>100% (Rated)</span>
            </div>
          </div>

          {/* Motor Speed: 0 - 100% */}
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-background/50 p-3.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground flex items-center gap-1.5">
                <Activity className="size-3.5 text-primary" /> Motor Speed
              </span>
              <span className="font-mono font-bold text-primary text-sm">
                {currentParams.motorSpeedPercent}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              step={1}
              value={currentParams.motorSpeedPercent}
              onChange={(e) => handleParamChange({ motorSpeedPercent: parseFloat(e.target.value) })}
              className="w-full accent-primary h-2 rounded-lg bg-muted cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>0%</span>
              <span>85% (VFD Match)</span>
              <span>100% (Max RPM)</span>
            </div>
          </div>

          {/* Operating Temperature Slider with machine-specific range */}
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-background/50 p-3.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground flex items-center gap-1.5">
                <Flame className={`size-3.5 ${currentParams.temperatureC > (machine.thermalThresholdC || 85) ? 'text-red-400' : 'text-primary'}`} />
                Core Temperature
              </span>
              <span className={`font-mono font-bold text-sm ${
                currentParams.temperatureC > (machine.thermalThresholdC || 85)
                  ? 'text-red-400'
                  : 'text-primary'
              }`}>
                {Math.round(currentParams.temperatureC)} {tempRange.unit}
              </span>
            </div>
            <input
              type="range"
              min={tempRange.min}
              max={tempRange.max}
              step={tempRange.step}
              value={currentParams.temperatureC}
              onChange={(e) => handleParamChange({ temperatureC: parseFloat(e.target.value) })}
              className="w-full accent-primary h-2 rounded-lg bg-muted cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>{tempRange.min}{tempRange.unit}</span>
              <span className="text-amber-500 font-semibold">
                Limit: {machine.thermalThresholdC || 85}{tempRange.unit}
              </span>
              <span>{tempRange.max}{tempRange.unit}</span>
            </div>
          </div>

          {/* Voltage: 360 - 440 V */}
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-background/50 p-3.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground flex items-center gap-1.5">
                <Zap className="size-3.5 text-primary" /> Line Voltage (3-Phase)
              </span>
              <span className="font-mono font-bold text-primary text-sm">
                {currentParams.voltageV} V
              </span>
            </div>
            <input
              type="range"
              min={360}
              max={440}
              step={2}
              value={currentParams.voltageV}
              onChange={(e) => handleParamChange({ voltageV: parseFloat(e.target.value) })}
              className="w-full accent-primary h-2 rounded-lg bg-muted cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>360V (-10%)</span>
              <span>400V (Nominal)</span>
              <span>440V (+10%)</span>
            </div>
          </div>

          {/* Current (Amperes): Scaled */}
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-background/50 p-3.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground flex items-center gap-1.5">
                <Activity className="size-3.5 text-primary" /> Phase Current
              </span>
              <span className="font-mono font-bold text-primary text-sm">
                {Math.round(currentParams.currentA)} A
              </span>
            </div>
            <input
              type="range"
              min={Math.round(machine.ratedPowerKw * 0.2)}
              max={Math.round(machine.ratedPowerKw * 2.2)}
              step={1}
              value={currentParams.currentA}
              onChange={(e) => handleParamChange({ currentA: parseFloat(e.target.value) })}
              className="w-full accent-primary h-2 rounded-lg bg-muted cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>No-Load</span>
              <span>Nominal FLA</span>
              <span>Overload</span>
            </div>
          </div>

          {/* Power Factor: 0.70 - 1.00 */}
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-background/50 p-3.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground flex items-center gap-1.5">
                <Gauge className="size-3.5 text-primary" /> Power Factor (PF)
              </span>
              <span className="font-mono font-bold text-primary text-sm">
                {currentParams.powerFactor.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min={0.70}
              max={1.00}
              step={0.01}
              value={currentParams.powerFactor}
              onChange={(e) => handleParamChange({ powerFactor: parseFloat(e.target.value) })}
              className="w-full accent-primary h-2 rounded-lg bg-muted cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>0.70 (Penalty)</span>
              <span>0.85 (Base)</span>
              <span>1.00 (Unity)</span>
            </div>
          </div>

          {/* Renewable Power Usage: 0 - 100% */}
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-background/50 p-3.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground flex items-center gap-1.5">
                <Leaf className="size-3.5 text-emerald-400" /> Renewable Power Mix
              </span>
              <span className="font-mono font-bold text-emerald-400 text-sm">
                {currentParams.renewableSharePercent}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              step={1}
              value={currentParams.renewableSharePercent}
              onChange={(e) => handleParamChange({ renewableSharePercent: parseFloat(e.target.value) })}
              className="w-full accent-primary h-2 rounded-lg bg-muted cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>0% (Grid Only)</span>
              <span>50%</span>
              <span>100% (Net Zero)</span>
            </div>
          </div>
        </div>

        {/* Maintenance Condition Selector */}
        <div className="flex flex-col gap-2 pt-1 border-t border-border/50">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-foreground">Maintenance Asset Condition</span>
            <span className="text-muted-foreground">Governs Arrhenius degradation acceleration and RUL</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {conditionsList.map((cond) => (
              <button
                key={cond.key}
                type="button"
                onClick={() => handleParamChange({ maintenanceCondition: cond.key })}
                className={`rounded-xl border p-2.5 text-xs font-semibold transition-all ${
                  currentParams.maintenanceCondition === cond.key
                    ? 'border-primary bg-primary text-primary-foreground shadow-sm ring-1 ring-primary'
                    : 'border-border/60 bg-muted/20 text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                }`}
              >
                {cond.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* SECTION 3: Side-by-Side Analytics & AI Explanations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: 24-Hour Diurnal Load Profile Simulation Curve */}
        <div className="flex flex-col gap-4 rounded-xl border border-border/80 bg-card/60 p-5 shadow-xs">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/60 pb-3">
            <div>
              <h3 className="text-sm font-bold text-foreground">
                24-Hour Diurnal Load Profile Simulation
              </h3>
              <p className="text-xs text-muted-foreground">
                Contrasting factory baseline load (kW) with simulated machine operation.
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="size-2 rounded-full bg-muted-foreground/60" /> Baseline kW
              </span>
              <span className="flex items-center gap-1.5 text-primary font-semibold">
                <span className="size-2 rounded-full bg-primary" /> Simulated kW
              </span>
            </div>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={simulationResult.hourlyPowerProfile}
                margin={{ top: 10, right: 10, left: -15, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="simKwGradOnPage" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.45} />
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.4} />
                <XAxis dataKey="hour" stroke="var(--muted-foreground)" fontSize={11} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} unit=" kW" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--card)',
                    borderColor: 'var(--border)',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="baselineKw"
                  stroke="var(--muted-foreground)"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  fill="none"
                  name="Baseline (kW)"
                />
                <Area
                  type="monotone"
                  dataKey="simulatedKw"
                  stroke="var(--primary)"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#simKwGradOnPage)"
                  name="Simulated (kW)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-3 gap-2.5 border-t border-border/50 pt-3 text-xs">
            <div className="rounded-lg bg-background/50 p-2.5 text-center">
              <span className="text-[11px] text-muted-foreground">Daily Simulated Energy</span>
              <p className="text-sm font-bold text-foreground">
                {formatNumber(simulationResult.predictedEnergyKwh, 1)} kWh
              </p>
            </div>
            <div className="rounded-lg bg-background/50 p-2.5 text-center">
              <span className="text-[11px] text-muted-foreground">Peak Electrical Draw</span>
              <p className="text-sm font-bold text-primary">
                {simulationResult.peakDemandContributionKw} kW
              </p>
            </div>
            <div className="rounded-lg bg-background/50 p-2.5 text-center">
              <span className="text-[11px] text-muted-foreground">Estimated Tariff Expense</span>
              <p className="text-sm font-bold text-foreground">
                ₹{simulationResult.predictedCostInr.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        {/* Right: Causal AI Explanations & Prescriptive Insights */}
        <AiExplanationsPanel result={simulationResult} />
      </div>

      {/* Save Scenario Modal Dialog */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b pb-2">
              <h3 className="font-bold text-foreground text-base">Save Simulation Scenario</h3>
              <button
                onClick={() => setShowSaveModal(false)}
                className="text-muted-foreground hover:text-foreground text-sm"
              >
                ✕
              </button>
            </div>
            <p className="text-xs text-muted-foreground">
              Save this operating point configuration (e.g. "Scenario A - Eco Run") to compare it side-by-side with other machine profiles.
            </p>
            <input
              type="text"
              placeholder="Scenario Name (e.g. Scenario A: Peak Shaving)"
              value={scenarioNameInput}
              onChange={(e) => setScenarioNameInput(e.target.value)}
              className="h-9 w-full rounded-md border border-border bg-background px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setShowSaveModal(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleSaveScenario}>
                Save Scenario
              </Button>
            </div>
          </div>
        </div>
      )}
    </Surface>
  )
}
