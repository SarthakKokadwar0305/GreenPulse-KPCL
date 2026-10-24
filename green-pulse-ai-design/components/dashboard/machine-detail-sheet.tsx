'use client'

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts'

import { IconTile } from '@/components/shared/icon-tile'
import { MeterBar } from '@/components/shared/meter-bar'
import { ToneBadge } from '@/components/shared/tone-badge'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { formatNumber } from '@/lib/format'
import { resolveIcon } from '@/lib/icons'
import { MACHINE_STATUS_META } from '@/lib/status'
import { getScoreTone } from '@/lib/tone'
import type { Machine } from '@/types'

const powerChartConfig = {
  power: { label: 'Power (kW)', color: 'var(--chart-1)' },
} satisfies ChartConfig

interface MachineDetailSheetProps {
  machine?: Machine
  onClose: () => void
}

interface DetailRowProps {
  label: string
  value: string
}

function DetailRow({ label, value }: DetailRowProps) {
  return (
    <div className="flex items-center justify-between gap-4 py-2.5 text-sm">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="font-medium text-foreground tabular-nums">{value}</dd>
    </div>
  )
}

function MeterRow({
  label,
  value,
  display,
  tone,
}: {
  label: string
  value: number
  display: string
  tone: ReturnType<typeof getScoreTone>
}) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between text-[13px]">
        <span className="font-medium text-muted-foreground">{label}</span>
        <span className="font-semibold text-foreground tabular-nums">
          {display}
        </span>
      </div>
      <MeterBar value={value} label={label} tone={tone} />
    </div>
  )
}

export function MachineDetailSheet({ machine, onClose }: MachineDetailSheetProps) {
  const Icon = machine ? resolveIcon(machine.iconKey) : null
  const status = machine ? MACHINE_STATUS_META[machine.status] : null

  return (
    <Sheet open={Boolean(machine)} onOpenChange={(open) => !open && onClose()}>
      <SheetContent
        side="right"
        className="w-full gap-0 overflow-y-auto sm:max-w-md"
      >
        {machine && Icon && status && (
          <>
            <SheetHeader className="gap-3 border-b p-6">
              <div className="flex items-center gap-3">
                <IconTile icon={Icon} tone={status.tone} />
                <div className="min-w-0">
                  <SheetTitle className="text-lg font-semibold">
                    {machine.name}
                  </SheetTitle>
                  <SheetDescription>{machine.zone}</SheetDescription>
                </div>
              </div>
              <ToneBadge
                tone={status.tone}
                pulse={machine.status === 'running'}
                className="w-fit"
              >
                {status.label}
              </ToneBadge>
            </SheetHeader>

            <div className="flex flex-col gap-6 p-6">
              <section aria-label="Power draw" className="flex flex-col gap-3">
                <h3 className="text-sm font-semibold text-foreground">
                  Power draw, last 90 minutes
                </h3>
                <ChartContainer
                  config={powerChartConfig}
                  className="aspect-auto h-44 w-full"
                >
                  <AreaChart
                    data={machine.powerHistory}
                    margin={{ left: 0, right: 8, top: 8 }}
                  >
                    <defs>
                      <linearGradient id="power-fill" x1="0" y1="0" x2="0" y2="1">
                        <stop
                          offset="0%"
                          stopColor="var(--color-power)"
                          stopOpacity={0.28}
                        />
                        <stop
                          offset="100%"
                          stopColor="var(--color-power)"
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>
                    <CartesianGrid vertical={false} strokeDasharray="3 3" />
                    <XAxis
                      dataKey="time"
                      tickLine={false}
                      axisLine={false}
                      tickMargin={8}
                      minTickGap={24}
                    />
                    <YAxis
                      tickLine={false}
                      axisLine={false}
                      width={40}
                      domain={['dataMin - 20', 'dataMax + 20']}
                      tickFormatter={(value: number) => Math.round(value).toString()}
                    />
                    <ChartTooltip content={<ChartTooltipContent indicator="line" />} />
                    <Area
                      dataKey="power"
                      type="monotone"
                      stroke="var(--color-power)"
                      strokeWidth={2}
                      fill="url(#power-fill)"
                    />
                  </AreaChart>
                </ChartContainer>
              </section>

              <section aria-label="Condition" className="flex flex-col gap-4">
                <h3 className="text-sm font-semibold text-foreground">Condition</h3>
                <MeterRow
                  label="Load"
                  value={(machine.powerKw / machine.ratedPowerKw) * 100}
                  display={`${formatNumber(machine.powerKw)} / ${formatNumber(machine.ratedPowerKw)} kW`}
                  tone="info"
                />
                <MeterRow
                  label="Efficiency"
                  value={machine.efficiency}
                  display={`${machine.efficiency}%`}
                  tone={getScoreTone(machine.efficiency)}
                />
                <MeterRow
                  label="Health score"
                  value={machine.healthScore}
                  display={`${machine.healthScore}/100`}
                  tone={getScoreTone(machine.healthScore)}
                />
              </section>

              <dl className="divide-y rounded-tile border px-4">
                <DetailRow
                  label="Temperature"
                  value={`${machine.temperatureC}°C`}
                />
                <DetailRow
                  label="Energy today"
                  value={`${formatNumber(machine.energyKwh)} kWh`}
                />
                <DetailRow
                  label="Energy target"
                  value={`${formatNumber(machine.energyTargetKwh)} kWh`}
                />
                <DetailRow
                  label="Runtime this shift"
                  value={`${machine.uptimeHours.toFixed(1)} h`}
                />
                <DetailRow
                  label="Last maintenance"
                  value={machine.lastMaintenance}
                />
              </dl>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  )
}
