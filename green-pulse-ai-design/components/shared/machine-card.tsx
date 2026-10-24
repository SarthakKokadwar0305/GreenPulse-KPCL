'use client'

import { motion } from 'framer-motion'
import {
  ChevronRight,
  Gauge,
  Thermometer,
  Zap,
  Activity,
  type LucideIcon,
} from 'lucide-react'

import { formatNumber } from '@/lib/format'
import { resolveIcon } from '@/lib/icons'
import { MACHINE_STATUS_META } from '@/lib/status'
import { getScoreTone } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { Machine } from '@/types'

import { IconTile } from './icon-tile'
import { MeterBar } from './meter-bar'
import { ToneBadge } from './tone-badge'

interface MachineMetricProps {
  icon: LucideIcon
  label: string
  value: string
  unit: string
}

function MachineMetric({ icon: Icon, label, value, unit }: MachineMetricProps) {
  return (
    <span className="flex flex-col gap-1 rounded-tile bg-muted/60 px-3 py-2.5">
      <span className="flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
        <Icon className="size-3.5" aria-hidden="true" />
        {label}
      </span>
      <span className="text-[15px] font-semibold text-foreground tabular-nums">
        {value}
        <span className="ml-1 text-xs font-medium text-muted-foreground">
          {unit}
        </span>
      </span>
    </span>
  )
}

interface MachineCardProps {
  machine: Machine
  selected?: boolean
  onSelect: (machine: Machine) => void
}

export function MachineCard({ machine, selected, onSelect }: MachineCardProps) {
  const Icon = resolveIcon(machine.iconKey)
  const status = MACHINE_STATUS_META[machine.status]
  const healthTone = getScoreTone(machine.healthScore)
  const isLive = machine.status === 'running'

  return (
    <motion.button
      type="button"
      onClick={() => onSelect(machine)}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.99 }}
      transition={{ type: 'spring', stiffness: 380, damping: 28 }}
      aria-label={`${machine.name}, ${status.label}. Open details`}
      aria-pressed={selected}
      className={cn(
        'group flex h-full w-full flex-col gap-4 rounded-card border bg-card p-5 text-left shadow-card outline-none',
        'transition-[box-shadow,border-color] duration-200 hover:border-primary/30 hover:shadow-card-hover',
        'focus-visible:ring-3 focus-visible:ring-ring/40',
        selected && 'border-primary/40',
      )}
    >
      <span className="flex items-start justify-between gap-3">
        <span className="flex min-w-0 items-center gap-3">
          <IconTile icon={Icon} tone={status.tone} />
          <span className="flex min-w-0 flex-col">
            <span className="truncate text-[15px] font-semibold text-foreground">
              {machine.name}
            </span>
            <span className="truncate text-xs text-muted-foreground">
              {machine.zone}
            </span>
          </span>
        </span>
        <ToneBadge tone={status.tone} pulse={isLive}>
          {status.label}
        </ToneBadge>
      </span>

      <span className="grid grid-cols-2 gap-2">
        <MachineMetric
          icon={Zap}
          label="Power"
          value={formatNumber(machine.powerKw, 1)}
          unit="kW"
        />
        <MachineMetric
          icon={Thermometer}
          label="Temperature"
          value={formatNumber(machine.temperatureC)}
          unit="°C"
        />
        <MachineMetric
          icon={Gauge}
          label="Efficiency"
          value={formatNumber(machine.efficiency, 1)}
          unit="%"
        />
        <MachineMetric
          icon={Activity}
          label="Energy today"
          value={formatNumber(machine.energyKwh)}
          unit="kWh"
        />
      </span>

      <span className="mt-auto flex flex-col gap-2">
        <span className="flex items-center justify-between text-xs">
          <span className="font-medium text-muted-foreground">Health score</span>
          <span className="flex items-center gap-1 font-semibold text-foreground tabular-nums">
            {machine.healthScore}
            <span className="font-medium text-muted-foreground">/ 100</span>
          </span>
        </span>
        <MeterBar
          value={machine.healthScore}
          tone={healthTone}
          label={`${machine.name} health score`}
        />
        <span className="flex items-center justify-end gap-0.5 text-xs font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
          View details
          <ChevronRight className="size-3.5" aria-hidden="true" />
        </span>
      </span>
    </motion.button>
  )
}
