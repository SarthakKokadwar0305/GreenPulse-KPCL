'use client'

import {
  Activity,
  Boxes,
  CircleDot,
  Cpu,
  Flame,
  Gauge,
  History,
  Info,
  Layers,
  Maximize2,
  Minimize2,
  PaintRoller,
  Power,
  RefreshCw,
  Search,
  SlidersHorizontal,
  Sparkles,
  Waves,
  Wind,
  Wrench,
  Zap,
} from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { Reveal } from '@/components/motion/reveal'
import { IconTile } from '@/components/shared/icon-tile'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { PageHeader } from '@/components/shared/page-header'
import { SectionHeader } from '@/components/shared/section-header'
import { SegmentedControl } from '@/components/shared/segmented-control'
import { Surface } from '@/components/shared/surface'
import { ToneBadge } from '@/components/shared/tone-badge'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useDigitalTwinData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'
import type { MachineTelemetry } from '@/types'
import { useSimulationSyncStore } from '@/store/simulation-sync-store'

import { MachineCard } from './machine-card'
import { DigitalTwinControlPanel } from './digital-twin-control-panel'
import { ScenarioComparisonModal } from './scenario-comparison-modal'
import { SimulationTimeline } from './simulation-timeline'

type StatusFilter = 'all' | 'running' | 'warning' | 'fault' | 'idle'

export function DigitalTwinView() {
  const { data: machines, isLoading, isError, refetch } = useDigitalTwinData()
  const { machineResults } = useSimulationSyncStore()

  // Default to first machine (Air Compressor 01) so simulation is always immediately visible on-page
  const [selectedMachineId, setSelectedMachineId] = useState<string | null>('air-compressor')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showPowerLines, setShowPowerLines] = useState(true)
  const [selectedFloorZone, setSelectedFloorZone] = useState<string>('all')

  // Modals for scenario comparison and simulation timeline
  const [showScenarioComparison, setShowScenarioComparison] = useState(false)
  const [showTimeline, setShowTimeline] = useState(false)

  const effectiveSelectedId = selectedMachineId || (machines && machines.length > 0 ? machines[0].id : null)
  const selectedMachine = machines?.find((m) => m.id === effectiveSelectedId)

  const handleSelectMachine = (id: string) => {
    setSelectedMachineId(id)
    setTimeout(() => {
      document.getElementById('simulation-studio')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }, 50)
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Flagship Cyber-Physical System"
          title="Digital Twin: Smart Factory Floor"
          description="Interactive real-time spatial digital twin of the manufacturing plant."
        />
        <LoadingPanel className="min-h-[500px]" />
      </div>
    )
  }

  if (isError || !machines) {
    return (
      <Surface className="flex min-h-96 flex-col items-center justify-center gap-4 p-8 text-center">
        <Cpu className="size-12 text-destructive" />
        <h2 className="text-xl font-semibold text-foreground">Digital Twin Stream Offline</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Unable to bind to the 3D SCADA spatial mapping bus. Check Edge Gateway telemetry bridge.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Reconnect Digital Twin
        </Button>
      </Surface>
    )
  }

  // Filter machines dynamically
  const filteredMachines = machines.filter((m) => {
    const sim = machineResults[m.id]
    const effectiveStatus = sim ? (sim.machineState === 'emergency_stop' ? 'fault' : sim.machineState) : m.status

    if (statusFilter !== 'all' && effectiveStatus !== statusFilter) return false
    if (selectedFloorZone !== 'all' && m.zone !== selectedFloorZone) return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      return (
        m.name.toLowerCase().includes(q) ||
        m.code.toLowerCase().includes(q) ||
        m.zone.toLowerCase().includes(q)
      )
    }
    return true
  })

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="Flagship Cyber-Physical System"
        title="Digital Twin Factory Floor"
        description="Interactive industrial machine simulator. Adjust machine operating states, runtime, motor speed, temperature, and electrical parameters in the on-page simulation studio below to inspect live predictions and floor card animations in real time."
        meta={
          <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5 font-medium text-emerald-600 dark:text-emerald-400">
              <span className="size-2 rounded-full bg-emerald-500" />
              Green = Healthy
            </span>
            <span className="flex items-center gap-1.5 font-medium text-amber-600 dark:text-amber-400">
              <span className="size-2 rounded-full bg-amber-500" />
              Yellow = Warning
            </span>
            <span className="flex items-center gap-1.5 font-medium text-rose-600 dark:text-rose-400">
              <span className="size-2 rounded-full bg-rose-500" />
              Red = Fault
            </span>
            <span className="flex items-center gap-1.5 font-medium text-sky-600 dark:text-sky-400">
              <span className="size-2 rounded-full bg-sky-500" />
              Blue = Idle
            </span>
            <span className="flex items-center gap-1.5 font-medium text-zinc-400">
              <span className="size-2 rounded-full bg-zinc-600" />
              Grey = E-Stop
            </span>
          </div>
        }
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => setShowScenarioComparison(true)}
            >
              <Layers className="size-3.5 text-primary" />
              Compare Scenarios
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => setShowTimeline(true)}
            >
              <History className="size-3.5" />
              Simulation Audit
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => setShowPowerLines((v) => !v)}
            >
              <Zap className="size-3.5" />
              {showPowerLines ? 'Hide Busway Lines' : 'Show Busway Lines'}
            </Button>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                refetch()
                toast.success('Digital Twin Synchronized', {
                  description: `All ${machines.length} machine telemetry streams refreshed from backend database.`,
                })
              }}
            >
              <RefreshCw className="size-3.5" />
              Live Refresh
            </Button>
          </div>
        }
      />

      {/* Control Bar: Filters & Search */}
      <Surface className="flex flex-wrap items-center justify-between gap-4 p-4">
        <div className="flex flex-wrap items-center gap-3">
          <SegmentedControl
            value={statusFilter}
            options={[
              { value: 'all', label: 'All Fleet', count: machines.length },
              { value: 'running', label: 'Healthy (Green)' },
              { value: 'warning', label: 'Warning (Yellow)' },
              { value: 'idle', label: 'Idle (Blue)' },
              { value: 'fault', label: 'Fault (Red)' },
            ]}
            onChange={setStatusFilter}
            ariaLabel="Status filter"
          />

          <div className="relative w-48 sm:w-64">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
            <Input
              placeholder="Search machine or bay..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 pl-8 text-xs"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5 font-mono text-emerald-400">
            <Sparkles className="size-3.5 animate-pulse" />
            Simulating on same page · Select any asset to inspect live animations
          </span>
        </div>
      </Surface>

      {/* Main Interactive Factory Floor Canvas */}
      <Surface className="relative overflow-hidden border p-6 bg-card/50">
        {/* Floor Schematic Grid Background */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)] bg-[size:40px_40px] opacity-25 pointer-events-none" />

        {/* Floor Zones Header Bar */}
        <div className="relative mb-6 flex flex-wrap items-center justify-between gap-3 border-b pb-3">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs font-mono">FAC-IND-PUN-004</Badge>
            <span className="text-sm font-semibold text-foreground">
              Main Production Floor Plan · Bays 1 to 5 ({machines.length} Total Monitored Machines)
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="rounded bg-muted px-2 py-1 font-mono text-[11px]">
              Substation: 33kV TR-01 (1,556 kW Active Bus)
            </span>
          </div>
        </div>

        {/* Floor Plan Layout */}
        <div className="relative min-h-[520px] rounded-xl border border-dashed border-border/80 bg-background/50 p-6">
          {/* Substation Busway Routing Lines (SVG Overlay) */}
          {showPowerLines && (
            <svg className="absolute inset-0 size-full pointer-events-none z-0" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="busway-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.8} />
                  <stop offset="100%" stopColor="var(--chart-3)" stopOpacity={0.4} />
                </linearGradient>
              </defs>
              {/* Main Substation trunk feeder */}
              <line x1="50%" y1="20" x2="50%" y2="100%" stroke="var(--primary)" strokeWidth="2" strokeDasharray="6 4" opacity="0.35" />
              <line x1="20" y1="50%" x2="100%" y2="50%" stroke="var(--primary)" strokeWidth="2" strokeDasharray="6 4" opacity="0.35" />
              {/* Radial branches to equipment cells */}
              <circle cx="50%" cy="50%" r="6" fill="var(--primary)" />
            </svg>
          )}

          {/* Machine Floor Grid - Fully Dynamic from Backend / Database */}
          <div className="relative z-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredMachines.map((machine, index) => {
              const simResult = machineResults[machine.id]
              const isSelected = effectiveSelectedId === machine.id

              return (
                <Reveal key={machine.id} index={index}>
                  <MachineCard
                    machine={machine}
                    simulationResult={simResult}
                    isSelected={isSelected}
                    onClick={() => handleSelectMachine(machine.id)}
                  />
                </Reveal>
              )
            })}
          </div>

          {filteredMachines.length === 0 && (
            <div className="flex min-h-[300px] flex-col items-center justify-center gap-3 text-center">
              <Cpu className="size-10 text-muted-foreground" />
              <p className="text-sm font-medium text-foreground">No machines match the selected filter criteria.</p>
              <Button size="sm" variant="outline" onClick={() => { setStatusFilter('all'); setSearchQuery('') }}>
                Reset Filters
              </Button>
            </div>
          )}
        </div>
      </Surface>

      {/* ON-PAGE INTERACTIVE DIGITAL TWIN SIMULATION STUDIO */}
      {selectedMachine && (
        <DigitalTwinControlPanel
          machine={selectedMachine}
          allMachines={machines}
          onSelectMachine={(id) => handleSelectMachine(id)}
          onClose={() => setSelectedMachineId(null)}
          onOpenScenarioComparison={() => setShowScenarioComparison(true)}
          onOpenTimeline={() => setShowTimeline(true)}
        />
      )}

      {/* Fleet Telemetry Summary Table */}
      <Surface className="flex flex-col gap-4 p-5">
        <SectionHeader
          title={`Factory Fleet Telemetry & Simulation Register (${machines.length} Assets)`}
          description="Detailed multi-phase electrical parameters, real-time thermodynamic status, and AI failure risk."
          icon={Layers}
        />

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b bg-muted/30 text-muted-foreground font-semibold">
              <tr>
                <th className="py-3 px-4">Asset Code</th>
                <th className="py-3 px-4">Machine Name</th>
                <th className="py-3 px-4">Zone</th>
                <th className="py-3 px-4">State</th>
                <th className="py-3 px-4 text-right">Power Draw</th>
                <th className="py-3 px-4 text-right">Core Temp</th>
                <th className="py-3 px-4 text-right">Health Score</th>
                <th className="py-3 px-4 text-right">72h Risk</th>
                <th className="py-3 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {machines.map((m) => {
                const sim = machineResults[m.id]
                const power = sim ? sim.predictedPowerKw : m.powerKw
                const temp = sim ? sim.temperatureC : m.temperatureC
                const health = sim ? sim.machineHealthPercent : m.healthScore
                const risk = sim ? sim.failureProbabilityPercent : m.failureProbability72h
                const state = sim ? sim.machineState : m.status
                const isSelected = effectiveSelectedId === m.id

                return (
                  <tr
                    key={m.id}
                    className={`transition-colors cursor-pointer ${
                      isSelected ? 'bg-primary/10 font-medium' : 'hover:bg-muted/20'
                    }`}
                    onClick={() => handleSelectMachine(m.id)}
                  >
                    <td className="py-3 px-4 font-mono font-medium text-foreground">{m.code}</td>
                    <td className="py-3 px-4 font-semibold text-foreground">
                      <div className="flex items-center gap-1.5">
                        <span>{m.name}</span>
                        {sim && (
                          <span className="text-[10px] text-primary font-mono font-bold">• SIM</span>
                        )}
                        {isSelected && (
                          <span className="text-[10px] bg-primary text-primary-foreground font-bold px-1.5 py-0.2 rounded font-mono">
                            ACTIVE
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-muted-foreground">{m.zone}</td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full font-mono text-[11px] font-medium bg-muted text-foreground">
                        <span className={`size-1.5 rounded-full ${
                          state === 'running'
                            ? 'bg-emerald-400'
                            : state === 'idle'
                              ? 'bg-sky-400'
                              : state === 'maintenance'
                                ? 'bg-amber-400'
                                : state === 'emergency_stop'
                                  ? 'bg-zinc-400'
                                  : 'bg-rose-400'
                        }`} />
                        {state.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-foreground tabular-nums">
                      {formatNumber(power, 1)} kW
                    </td>
                    <td className="py-3 px-4 text-right tabular-nums">
                      <span className={temp > (m.thermalThresholdC || 85) ? 'text-rose-400 font-bold' : 'text-muted-foreground'}>
                        {Math.round(temp)}°C
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-muted-foreground tabular-nums font-mono font-semibold">
                      {health}%
                    </td>
                    <td className="py-3 px-4 text-right tabular-nums">
                      <span className={risk > 20 ? 'font-bold text-rose-400' : 'text-emerald-400'}>
                        {risk}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Button
                        size="sm"
                        variant={isSelected ? 'default' : 'ghost'}
                        className="h-7 text-xs gap-1"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleSelectMachine(m.id)
                        }}
                      >
                        <SlidersHorizontal className="size-3" />
                        {isSelected ? 'Simulating' : 'Simulate'}
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Surface>

      {/* Scenario Comparison Modal */}
      <ScenarioComparisonModal
        isOpen={showScenarioComparison}
        onClose={() => setShowScenarioComparison(false)}
      />

      {/* Simulation Timeline Audit Modal */}
      <SimulationTimeline
        isOpen={showTimeline}
        onClose={() => setShowTimeline(false)}
      />
    </div>
  )
}
