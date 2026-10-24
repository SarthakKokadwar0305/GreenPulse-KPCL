'use client'

import { BellRing, CircleCheck } from 'lucide-react'
import { useMemo, useState } from 'react'

import { AlertCard } from '@/components/shared/alert-card'
import { LoadingPanel } from '@/components/shared/loading-panel'
import {
  SegmentedControl,
  type SegmentedOption,
} from '@/components/shared/segmented-control'
import { SectionHeader } from '@/components/shared/section-header'
import { Surface } from '@/components/shared/surface'
import { useAlerts } from '@/hooks/use-dashboard-data'
import { useSelectedPlant } from '@/hooks/use-workspace'
import type { AlertFilter } from '@/types'

const FILTERS: { value: AlertFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'critical', label: 'Critical' },
  { value: 'warning', label: 'Warning' },
  { value: 'info', label: 'Info' },
]

export function AlertsPanel() {
  const { data: alerts } = useAlerts()
  const plant = useSelectedPlant()
  const [filter, setFilter] = useState<AlertFilter>('all')

  const options = useMemo<SegmentedOption<AlertFilter>[]>(
    () =>
      FILTERS.map((item) => ({
        ...item,
        count:
          item.value === 'all'
            ? alerts?.length
            : alerts?.filter((alert) => alert.severity === item.value).length,
      })),
    [alerts],
  )

  if (!alerts || !plant) return <LoadingPanel className="min-h-80" />

  const visibleAlerts =
    filter === 'all' ? alerts : alerts.filter((alert) => alert.severity === filter)

  return (
    <Surface className="flex h-full flex-col gap-5 p-5" aria-label="Recent alerts">
      <SectionHeader
        title="Recent Alerts"
        description="Latest signals raised by monitoring and anomaly detection."
        icon={BellRing}
        action={
          <SegmentedControl
            ariaLabel="Filter alerts by severity"
            value={filter}
            options={options}
            onChange={setFilter}
          />
        }
      />
      {visibleAlerts.length > 0 ? (
        <ul className="grid grid-cols-1 gap-3 xl:grid-cols-2">
          {visibleAlerts.map((alert) => (
            <li key={alert.id}>
              <AlertCard alert={alert} timeZone={plant.timezone} />
            </li>
          ))}
        </ul>
      ) : (
        <div className="flex flex-1 flex-col items-center justify-center gap-2 py-10 text-center">
          <CircleCheck className="size-8 text-success" aria-hidden="true" />
          <p className="text-sm font-medium text-foreground">
            No alerts match this filter
          </p>
          <p className="text-[13px] text-muted-foreground">
            Everything in this category is clear.
          </p>
        </div>
      )}
    </Surface>
  )
}
