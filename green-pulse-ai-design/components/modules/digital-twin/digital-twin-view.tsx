'use client'

import {
  Activity,
  Boxes,
  CircleDot,
  Cpu,
  Flame,
  Gauge,
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

import { MachineDetailDrawer } from './machine-detail-drawer'

type StatusFilter = 'all' | 'running' | 'warning' | 'fault' | 'idle'

export function DigitalTwinView() {
  const { data: machines, isLoading, isError, refetch } = useDigitalTwinData()
  const [selectedMachineId, setSelectedMachineId] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showPowerLines, setShowPowerLines] = useState(true)
  const [selectedFloorZone, setSelectedFloorZone] = useState<string>('all')

  const selectedMachine = machines?.find((m) => m.id === selectedMachineId)

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

  // Filter machines
  const filteredMachines = machines.filter((m) => {
    if (statusFilter !== 'all' && m.status !== statusFilter) return false
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

  // Machine status colors requirement:
  // Green = Healthy
  // Yellow = Warning
  // Red = Fault
  // Blue = Idle
  const getMachineColorConfig = (status: MachineTelemetry['status']) => {
    switch (status) {
      case 'running':
        return {
          bg: 'bg-emerald-500/10 dark:bg-emerald-500/20',
          border: 'border-emerald-500/50 hover:border-emerald-500',
          indicator: 'bg-emerald-500',
          text: 'text-emerald-600 dark:text-emerald-400',
          badgeTone: 'success' as const,
          label: 'Healthy (Running)',
          glow: 'shadow-[0_0_20px_-3px_rgba(16,185,129,0.35)]',
        }
      case 'warning':
        return {
          bg: 'bg-amber-500/10 dark:bg-amber-500/20',
          border: 'border-amber-500/60 hover:border-amber-500',
          indicator: 'bg-amber-500 animate-status-pulse',
          text: 'text-amber-600 dark:text-amber-400',
          badgeTone: 'warning' as const,
          label: 'Warning (Anomaly)',
          glow: 'shadow-[0_0_20px_-3px_rgba(245,158,11,0.45)]',
        }
      case 'fault':
        return {
          bg: 'bg-rose-500/10 dark:bg-rose-500/20',
          border: 'border-rose-500/70 hover:border-rose-500',
          indicator: 'bg-rose-500 animate-status-pulse',
          text: 'text-rose-600 dark:text-rose-400',
          badgeTone: 'danger' as const,
          label: 'Fault (Critical)',
          glow: 'shadow-[0_0_20px_-3px_rgba(244,63,94,0.45)]',
        }
      case 'idle':
        return {
          bg: 'bg-sky-500/10 dark:bg-sky-500/20',
          border: 'border-sky-500/50 hover:border-sky-500',
          indicator: 'bg-sky-500',
          text: 'text-sky-600 dark:text-sky-400',
          badgeTone: 'info' as const,
          label: 'Idle (Standby)',
          glow: 'shadow-[0_0_20px_-3px_rgba(14,165,233,0.3)]',
        }
    }
  }

  const getMachineIcon = (id: string) => {
    switch (id) {
      case 'air-compressor':
        return Wind
      case 'heat-furnace':
        return Flame
      case 'cnc-machine':
        return Cpu
      case 'cooling-pump':
        return Waves
      case 'paint-booth':
        return PaintRoller
      case 'assembly-line':
        return Boxes
      default:
        return Activity
    }
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="Flagship Cyber-Physical System"
        title="Digital Twin Factory Floor"
        description="Interactive 2D/2.5D factory floor visualization. Inspect live telemetry, thermal gradients, phase voltages, and AI failure probabilities by selecting any asset."
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
          </div>
        }
        actions={
          <div className="flex items-center gap-2">
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
                  description: 'All 6 machine telemetry streams updated in real time.',
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
              { value: 'all', label: 'All Machines', count: machines.length },
              { value: 'running', label: 'Healthy (Green)' },
              { value: 'warning', label: 'Warning (Yellow)' },
              { value: 'idle', label: 'Idle (Blue)' },
            ]}
            onChange={setStatusFilter}
            ariaLabel="Status filter"
          />

          <div className="relative w-48 sm:w-64">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
            <Input
              placeholder="Search machine or code..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 pl-8 text-xs"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Click any machine to inspect comprehensive SCADA telemetry drawer.</span>
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
            <span className="text-sm font-semibold text-foreground">Main Production Floor Plan · Bay 1 to 5</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="rounded bg-muted px-2 py-1 font-mono text-[11px]">Substation: 33kV TR-01 (1,556 kW Active)</span>
          </div>
        </div>

        {/* Floor Plan Layout */}
        <div className="relative min-h-[520px] rounded-xl border border-dashed border-border/80 bg-background/50 p-6">
          {/* Substation Busway Routing Lines (SVG Overlay) */}
          {showPowerLines && (
            <svg className="absolute inset-0 size-full pointer-events-none z-0" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="busway-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="var(--chart-3)" stopOpacity="0.4" />
                </linearGradient>
              </defs>
              {/* Main Substation trunk feeder */}
              <line x1="50%" y1="20" x2="50%" y2="100%" stroke="var(--primary)" strokeWidth="2" strokeDasharray="6 4" opacity="0.35" />
              <line x1="20" y1="50%" x2="100%" y2="50%" stroke="var(--primary)" strokeWidth="2" strokeDasharray="6 4" opacity="0.35" />
              {/* Radial branches to equipment cells */}
              <circle cx="50%" cy="50%" r="6" fill="var(--primary)" />
            </svg>
          )}

          {/* Machine Floor Grid */}
          <div className="relative z-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredMachines.map((machine, index) => {
              const color = getMachineColorConfig(machine.status)
              const Icon = getMachineIcon(machine.id)
              const isSelected = selectedMachineId === machine.id

              return (
                <Reveal key={machine.id} index={index}>
                  <div
                    onClick={() => setSelectedMachineId(machine.id)}
                    className={`group relative cursor-pointer rounded-card border-2 p-5 transition-all duration-200 ${color.bg} ${color.border} ${
                      isSelected ? `ring-2 ring-primary ${color.glow}` : 'hover:-translate-y-1 hover:shadow-card-hover'
                    }`}
                  >
                    {/* Machine Header */}
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className={`size-11 rounded-tile flex items-center justify-center border ${color.border} bg-card text-foreground shadow-sm`}>
                          <Icon className={`size-5 ${color.text}`} />
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

                      <div className="flex flex-col items-end gap-1">
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${color.border} ${color.bg} ${color.text}`}>
                          <span className={`size-2 rounded-full ${color.indicator}`} />
                          {machine.status.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {/* Machine Core Telemetry Badges */}
                    <div className="mt-4 grid grid-cols-3 gap-2 rounded-lg border bg-card/80 backdrop-blur p-2.5 text-center shadow-xs">
                      <div>
                        <span className="text-[10px] text-muted-foreground uppercase font-medium">Power</span>
                        <p className="text-sm font-bold text-foreground tabular-nums">
                          {formatNumber(machine.powerKw)} <span className="text-[10px] font-normal text-muted-foreground">kW</span>
                        </p>
                      </div>
                      <div>
                        <span className="text-[10px] text-muted-foreground uppercase font-medium">Temp</span>
                        <p className={`text-sm font-bold tabular-nums ${machine.temperatureC > 80 ? 'text-amber-500' : 'text-foreground'}`}>
                          {machine.temperatureC}°C
                        </p>
                      </div>
                      <div>
                        <span className="text-[10px] text-muted-foreground uppercase font-medium">Health</span>
                        <p className={`text-sm font-bold tabular-nums ${color.text}`}>
                          {machine.healthScore}%
                        </p>
                      </div>
                    </div>

                    {/* Quick Specs & Status Ticker */}
                    <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground pt-1 border-t border-border/50">
                      <span>Shift Runtime: <strong className="text-foreground">{machine.runtimeHoursShift}h</strong></span>
                      <span className="font-medium text-primary flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                        Inspect Telemetry →
                      </span>
                    </div>

                    {/* Ambient Glow Aura */}
                    <div className={`absolute -inset-0.5 -z-10 rounded-card opacity-0 group-hover:opacity-100 transition-opacity blur-xs ${color.bg}`} />
                  </div>
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

      {/* Fleet Telemetry Summary Table */}
      <Surface className="flex flex-col gap-4 p-5">
        <SectionHeader
          title="Factory Fleet Telemetry & Degradation Register"
          description="Detailed multi-phase electrical and AI predictive condition parameters for all 6 core assets."
          icon={Layers}
        />

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b bg-muted/30 text-muted-foreground font-semibold">
              <tr>
                <th className="py-3 px-4">Asset Code</th>
                <th className="py-3 px-4">Machine Name</th>
                <th className="py-3 px-4">Zone</th>
                <th className="py-3 px-4">Status & Color</th>
                <th className="py-3 px-4 text-right">Power Draw</th>
                <th className="py-3 px-4 text-right">3-Phase Line V</th>
                <th className="py-3 px-4 text-right">Phase Current</th>
                <th className="py-3 px-4 text-right">Degradation</th>
                <th className="py-3 px-4 text-right">72h Risk</th>
                <th className="py-3 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {machines.map((m) => {
                const color = getMachineColorConfig(m.status)
                return (
                  <tr key={m.id} className="hover:bg-muted/20 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-foreground">{m.code}</td>
                    <td className="py-3 px-4 font-semibold text-foreground">{m.name}</td>
                    <td className="py-3 px-4 text-muted-foreground">{m.zone}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full font-medium ${color.bg} ${color.text}`}>
                        <span className={`size-1.5 rounded-full ${color.indicator}`} />
                        {color.label}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-foreground tabular-nums">{formatNumber(m.powerKw)} kW</td>
                    <td className="py-3 px-4 text-right text-muted-foreground tabular-nums">{m.voltage.lineToLine} V</td>
                    <td className="py-3 px-4 text-right text-muted-foreground tabular-nums">{m.current.l1} A</td>
                    <td className="py-3 px-4 text-right text-muted-foreground tabular-nums">{m.degradationRatePercent}%/mo</td>
                    <td className="py-3 px-4 text-right tabular-nums">
                      <span className={m.failureProbability72h > 20 ? 'font-bold text-amber-500' : 'text-emerald-500'}>
                        {m.failureProbability72h}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 text-xs text-primary"
                        onClick={() => setSelectedMachineId(m.id)}
                      >
                        Inspect Drawer
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Surface>

      {/* Right-Side Telemetry Drawer */}
      <MachineDetailDrawer
        machine={selectedMachine}
        onClose={() => setSelectedMachineId(null)}
      />
    </div>
  )
}
