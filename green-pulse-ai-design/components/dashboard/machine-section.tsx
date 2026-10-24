'use client'

import { Cpu } from 'lucide-react'
import { useState } from 'react'

import { Reveal } from '@/components/motion/reveal'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { MachineCard } from '@/components/shared/machine-card'
import { SectionHeader } from '@/components/shared/section-header'
import { ToneBadge } from '@/components/shared/tone-badge'
import { useMachines } from '@/hooks/use-dashboard-data'
import type { Machine } from '@/types'

import { MachineDetailSheet } from './machine-detail-sheet'

const MACHINE_PLACEHOLDER_COUNT = 6

export function MachineSection() {
  const { data: machines } = useMachines()
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const selectedMachine = machines?.find((machine) => machine.id === selectedId)
  const runningCount =
    machines?.filter((machine) => machine.status === 'running').length ?? 0

  return (
    <section aria-label="Live machine status" className="flex flex-col gap-4">
      <SectionHeader
        title="Live Machine Status"
        description="Select a machine to inspect its power draw and condition."
        icon={Cpu}
        action={
          machines && (
            <ToneBadge tone="success" pulse>
              {runningCount} of {machines.length} running
            </ToneBadge>
          )
        }
      />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {machines
          ? machines.map((machine, index) => (
              <Reveal key={machine.id} index={index} className="h-full">
                <MachineCard
                  machine={machine}
                  selected={machine.id === selectedId}
                  onSelect={(next: Machine) => setSelectedId(next.id)}
                />
              </Reveal>
            ))
          : Array.from({ length: MACHINE_PLACEHOLDER_COUNT }, (_, index) => (
              <LoadingPanel key={index} className="min-h-56" />
            ))}
      </div>
      <MachineDetailSheet
        machine={selectedMachine}
        onClose={() => setSelectedId(null)}
      />
    </section>
  )
}
