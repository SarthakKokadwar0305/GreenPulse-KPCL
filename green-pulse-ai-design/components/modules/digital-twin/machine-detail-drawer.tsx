'use client'

import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Clock,
  Cpu,
  Download,
  Gauge,
  History,
  Info,
  Leaf,
  Power,
  ShieldAlert,
  Thermometer,
  Wrench,
  Zap,
} from 'lucide-react'
import { useState } from 'react'
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

import { IconTile } from '@/components/shared/icon-tile'
import { MeterBar } from '@/components/shared/meter-bar'
import { ToneBadge } from '@/components/shared/tone-badge'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
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
import { exportToCsv } from '@/lib/export-utils'
import { getScoreTone } from '@/lib/tone'
import type { MachineTelemetry } from '@/types'

const powerChartConfig = {
  power: { label: 'Active Power (kW)', color: 'var(--chart-1)' },
} satisfies ChartConfig

interface MachineDetailDrawerProps {
  machine?: MachineTelemetry
  onClose: () => void
}

function TelemetryTile({
  label,
  value,
  subvalue,
  tone = 'neutral',
}: {
  label: string
  value: string
  subvalue?: string
  tone?: 'success' | 'warning' | 'danger' | 'info' | 'neutral'
}) {
  const borderTone =
    tone === 'danger'
      ? 'border-destructive/30 bg-destructive/5'
      : tone === 'warning'
        ? 'border-warning/30 bg-warning/5'
        : tone === 'success'
          ? 'border-success/30 bg-success/5'
          : tone === 'info'
            ? 'border-primary/30 bg-primary/5'
            : 'border-border bg-muted/20'

  return (
    <div className={`flex flex-col gap-1 rounded-lg border p-3 ${borderTone}`}>
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <p className="text-lg font-bold text-foreground tabular-nums">{value}</p>
      {subvalue && <span className="text-[11px] text-muted-foreground">{subvalue}</span>}
    </div>
  )
}

export function MachineDetailDrawer({ machine, onClose }: MachineDetailDrawerProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'electrical' | 'health' | 'history'>('overview')

  if (!machine) return null

  const getStatusColor = (status: MachineTelemetry['status']) => {
    switch (status) {
      case 'running':
        return { label: 'Healthy & Running', tone: 'success' as const, dotClass: 'bg-success' }
      case 'warning':
        return { label: 'Warning / Anomaly', tone: 'warning' as const, dotClass: 'bg-warning animate-status-pulse' }
      case 'fault':
        return { label: 'Faulted', tone: 'danger' as const, dotClass: 'bg-destructive animate-status-pulse' }
      case 'idle':
        return { label: 'Idle Standby', tone: 'info' as const, dotClass: 'bg-primary' }
    }
  }

  const statusMeta = getStatusColor(machine.status)

  return (
    <Sheet open={Boolean(machine)} onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="right" className="w-full gap-0 overflow-y-auto sm:max-w-xl p-0">
        {/* Drawer Header */}
        <SheetHeader className="gap-3 border-b p-6 bg-card">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-tile bg-primary/10 flex items-center justify-center text-primary">
                <Cpu className="size-5" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <SheetTitle className="text-xl font-bold tracking-tight text-foreground">
                    {machine.name}
                  </SheetTitle>
                  <Badge variant="outline" className="font-mono text-xs">
                    {machine.code}
                  </Badge>
                </div>
                <SheetDescription className="text-xs text-muted-foreground">
                  {machine.zone} · {machine.category} · {machine.specs.model}
                </SheetDescription>
              </div>
            </div>

            <ToneBadge tone={statusMeta.tone} pulse={machine.status === 'warning' || machine.status === 'fault'}>
              {statusMeta.label}
            </ToneBadge>
          </div>

          {/* Quick Tabs */}
          <div className="mt-2 flex border-b border-border text-xs font-medium">
            <button
              type="button"
              onClick={() => setActiveTab('overview')}
              className={`pb-2 px-3 transition-colors ${
                activeTab === 'overview'
                  ? 'border-b-2 border-primary text-primary font-semibold'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Telemetry & Energy
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('electrical')}
              className={`pb-2 px-3 transition-colors ${
                activeTab === 'electrical'
                  ? 'border-b-2 border-primary text-primary font-semibold'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              3-Phase Electrical
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('health')}
              className={`pb-2 px-3 transition-colors ${
                activeTab === 'health'
                  ? 'border-b-2 border-primary text-primary font-semibold'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              AI Insights & Risk
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('history')}
              className={`pb-2 px-3 transition-colors ${
                activeTab === 'history'
                  ? 'border-b-2 border-primary text-primary font-semibold'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Maintenance History
            </button>
          </div>
        </SheetHeader>

        {/* Drawer Body */}
        <div className="flex flex-col gap-6 p-6">
          {activeTab === 'overview' && (
            <>
              {/* Primary Telemetry Grid */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <TelemetryTile
                  label="Current Energy"
                  value={`${formatNumber(machine.powerKw)} kW`}
                  subvalue={`Rated: ${machine.ratedPowerKw} kW`}
                  tone={machine.powerKw > machine.ratedPowerKw * 0.9 ? 'warning' : 'info'}
                />
                <TelemetryTile
                  label="Temperature"
                  value={`${machine.temperatureC}°C`}
                  subvalue={`Limit: ${machine.thermalThresholdC}°C`}
                  tone={machine.temperatureC > machine.thermalThresholdC - 10 ? 'warning' : 'success'}
                />
                <TelemetryTile
                  label="Carbon Rate"
                  value={`${machine.carbonKgPerHour.toFixed(1)}`}
                  subvalue="kg CO₂e/hr"
                  tone="neutral"
                />
                <TelemetryTile
                  label="Health Score"
                  value={`${machine.healthScore}/100`}
                  subvalue={`Risk: ${machine.failureProbability72h}%`}
                  tone={getScoreTone(machine.healthScore)}
                />
              </div>

              {/* Real-time 24h Power Curve */}
              <section className="flex flex-col gap-3 rounded-lg border bg-card p-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-foreground">Active Power Curve (Past 24h)</h4>
                  <Badge variant="outline" className="text-[11px]">
                    Today: {formatNumber(machine.energyTodayKwh)} kWh
                  </Badge>
                </div>
                <ChartContainer config={powerChartConfig} className="aspect-auto h-44 w-full">
                  <AreaChart data={machine.timeline24h} margin={{ left: -15, right: 10, top: 10 }}>
                    <defs>
                      <linearGradient id="drawer-power-grad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid vertical={false} strokeDasharray="3 3" />
                    <XAxis dataKey="time" tickLine={false} axisLine={false} tickMargin={8} />
                    <YAxis tickLine={false} axisLine={false} tickMargin={8} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Area
                      type="monotone"
                      dataKey="power"
                      stroke="var(--chart-1)"
                      strokeWidth={2}
                      fill="url(#drawer-power-grad)"
                    />
                  </AreaChart>
                </ChartContainer>
              </section>

              {/* Machine Timeline (24h State Bar) */}
              <section className="flex flex-col gap-2 rounded-lg border bg-card p-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-foreground">Operational States (Last 24 Hours)</span>
                  <span className="text-muted-foreground">Continuous SCADA log</span>
                </div>
                <div className="flex h-5 w-full overflow-hidden rounded-md border">
                  {machine.timeline24h.map((sample, idx) => (
                    <div
                      key={idx}
                      title={`${sample.time}: ${sample.state.toUpperCase()} (${sample.power} kW)`}
                      className={`flex-1 transition-opacity hover:opacity-80 ${
                        sample.state === 'running'
                          ? 'bg-success'
                          : sample.state === 'warning'
                            ? 'bg-warning'
                            : sample.state === 'fault'
                              ? 'bg-destructive'
                              : 'bg-primary'
                      }`}
                    />
                  ))}
                </div>
                <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
                  <span className="flex items-center gap-1">
                    <span className="size-2 rounded-full bg-success" /> Healthy
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="size-2 rounded-full bg-warning" /> Warning
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="size-2 rounded-full bg-destructive" /> Fault
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="size-2 rounded-full bg-primary" /> Idle
                  </span>
                </div>
              </section>

              {/* Asset Technical Specifications */}
              <section className="flex flex-col gap-2 rounded-lg border bg-muted/20 p-4 text-xs">
                <h4 className="font-semibold text-foreground">Asset Specifications & Ownership</h4>
                <div className="grid grid-cols-2 gap-y-2 pt-2 text-muted-foreground">
                  <span>Serial Number</span>
                  <span className="font-mono font-medium text-foreground">{machine.specs.serial}</span>
                  <span>Commission Date</span>
                  <span className="font-medium text-foreground">{machine.specs.commissionDate}</span>
                  <span>Lead Operator</span>
                  <span className="font-medium text-foreground">{machine.specs.operatorInCharge}</span>
                  <span>Electrical Feeder</span>
                  <span className="font-medium text-foreground">{machine.specs.electricalSubstation}</span>
                </div>
              </section>
            </>
          )}

          {activeTab === 'electrical' && (
            <div className="flex flex-col gap-4">
              <div className="rounded-lg border bg-card p-4">
                <h4 className="text-sm font-semibold text-foreground mb-3">3-Phase Voltage Balance</h4>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="rounded-md border bg-muted/30 p-2.5">
                    <span className="text-[11px] text-muted-foreground">L1 - Neutral</span>
                    <p className="text-base font-bold text-foreground tabular-nums">{machine.voltage.l1} V</p>
                  </div>
                  <div className="rounded-md border bg-muted/30 p-2.5">
                    <span className="text-[11px] text-muted-foreground">L2 - Neutral</span>
                    <p className="text-base font-bold text-foreground tabular-nums">{machine.voltage.l2} V</p>
                  </div>
                  <div className="rounded-md border bg-muted/30 p-2.5">
                    <span className="text-[11px] text-muted-foreground">L3 - Neutral</span>
                    <p className="text-base font-bold text-foreground tabular-nums">{machine.voltage.l3} V</p>
                  </div>
                </div>
                <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
                  <span>Line-to-Line Voltage: <strong className="text-foreground">{machine.voltage.lineToLine} V</strong></span>
                  <span>Voltage Unbalance: <strong className="text-success">{machine.voltage.unbalancePercent}%</strong></span>
                </div>
              </div>

              <div className="rounded-lg border bg-card p-4">
                <h4 className="text-sm font-semibold text-foreground mb-3">Phase Currents & Power Factor</h4>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="rounded-md border bg-muted/30 p-2.5">
                    <span className="text-[11px] text-muted-foreground">Phase 1 (A)</span>
                    <p className="text-base font-bold text-foreground tabular-nums">{machine.current.l1} A</p>
                  </div>
                  <div className="rounded-md border bg-muted/30 p-2.5">
                    <span className="text-[11px] text-muted-foreground">Phase 2 (A)</span>
                    <p className="text-base font-bold text-foreground tabular-nums">{machine.current.l2} A</p>
                  </div>
                  <div className="rounded-md border bg-muted/30 p-2.5">
                    <span className="text-[11px] text-muted-foreground">Phase 3 (A)</span>
                    <p className="text-base font-bold text-foreground tabular-nums">{machine.current.l3} A</p>
                  </div>
                </div>
                <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground border-t pt-2">
                  <span>Operating Power Factor: <strong className="text-foreground">{machine.powerFactor}</strong></span>
                  <span>Reactive Load: <strong className="text-foreground">{(machine.powerKw * 0.32).toFixed(0)} kVAR</strong></span>
                </div>
              </div>

              <div className="rounded-lg border bg-card p-4">
                <h4 className="text-sm font-semibold text-foreground mb-2">Operational Runtimes & Reliability</h4>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="flex justify-between border-b py-2">
                    <span className="text-muted-foreground">Shift Runtime</span>
                    <span className="font-semibold text-foreground">{machine.runtimeHoursShift} h</span>
                  </div>
                  <div className="flex justify-between border-b py-2">
                    <span className="text-muted-foreground">Total Operating Hours</span>
                    <span className="font-semibold text-foreground">{formatNumber(machine.runtimeHoursTotal)} h</span>
                  </div>
                  <div className="flex justify-between border-b py-2">
                    <span className="text-muted-foreground">Mean Time Between Failures (MTBF)</span>
                    <span className="font-semibold text-foreground">{machine.mtbfHours} h</span>
                  </div>
                  <div className="flex justify-between border-b py-2">
                    <span className="text-muted-foreground">Mean Time to Repair (MTTR)</span>
                    <span className="font-semibold text-foreground">{machine.mttrHours} h</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'health' && (
            <div className="flex flex-col gap-4">
              {/* AI Insight Card */}
              <div className="rounded-lg border border-primary/30 bg-primary/5 p-4 flex flex-col gap-3">
                <div className="flex items-center gap-2">
                  <BrainCircuit className="size-5 text-primary" />
                  <h4 className="text-sm font-semibold text-foreground">{machine.aiInsight.title}</h4>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {machine.aiInsight.explanation}
                </p>
                <div className="rounded-md border bg-card p-3 text-xs">
                  <p className="font-medium text-foreground">Suggested Engineering Action:</p>
                  <p className="mt-1 text-muted-foreground">{machine.aiInsight.suggestedRemedy}</p>
                  {machine.aiInsight.potentialSavingsKw > 0 && (
                    <p className="mt-2 text-primary font-semibold">
                      Potential Power Recovery: {machine.aiInsight.potentialSavingsKw} kW
                    </p>
                  )}
                </div>
              </div>

              {/* Failure Risk Prediction */}
              <div className="rounded-lg border bg-card p-4 flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-foreground">72-Hour Failure Probability</h4>
                  <ToneBadge tone={machine.failureProbability72h > 20 ? 'warning' : 'success'}>
                    {machine.failureProbability72h}% Risk
                  </ToneBadge>
                </div>
                <MeterBar
                  value={machine.failureProbability72h}
                  label="Failure Probability"
                  tone={machine.failureProbability72h > 20 ? 'warning' : 'success'}
                />
                <div className="rounded-md bg-muted/30 p-2.5 text-xs text-muted-foreground">
                  <span className="font-medium text-foreground">Primary Predictive Mode: </span>
                  {machine.likelyFailureMode}
                </div>
              </div>

              {/* Carbon Contribution */}
              <div className="rounded-lg border bg-card p-4 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Total Plant Carbon Share</span>
                  <span className="text-sm font-bold text-foreground">{machine.carbonSharePercent}%</span>
                </div>
                <Progress value={machine.carbonSharePercent} className="h-2" />
                <p className="text-[11px] text-muted-foreground">
                  Emits {formatNumber(machine.carbonTodayKg)} kg CO₂e today based on 0.82 kg CO₂/kWh grid factor.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Last Maintenance: <strong>{machine.lastMaintenanceDate}</strong></span>
                <span className="text-muted-foreground">Next Scheduled PM: <strong>{machine.nextScheduledPm}</strong></span>
              </div>

              <div className="flex flex-col divide-y rounded-lg border bg-card">
                {machine.maintenanceHistory.map((item, idx) => (
                  <div key={idx} className="flex flex-col gap-1 p-3.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-foreground">{item.type}</span>
                      <span className="text-muted-foreground font-mono">{item.date}</span>
                    </div>
                    <p className="text-muted-foreground">{item.notes}</p>
                    <span className="text-[11px] text-primary">Certified Tech: {item.technician}</span>
                  </div>
                ))}
              </div>

              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs gap-1.5"
                onClick={() => {
                  toast.success('Work order created', {
                    description: `Maintenance ticket WO-${machine.code}-109 dispatched to plant maintenance group.`,
                  })
                }}
              >
                <Wrench className="size-3.5" />
                Dispatch Scheduled Maintenance Order
              </Button>
            </div>
          )}
        </div>

        {/* Drawer Actions Footer */}
        <div className="sticky bottom-0 border-t bg-card/95 backdrop-blur p-4 flex items-center justify-between gap-3">
          <Button
            variant="outline"
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => {
              const headers = ['Register Tag', 'Parameter', 'Value', 'Unit', 'Engineering Status']
              const rows = [
                ['MODBUS_REG_40001', 'Active Power', machine.powerKw, 'kW', machine.status.toUpperCase()],
                ['MODBUS_REG_40002', 'Rated Power', machine.ratedPowerKw, 'kW', 'SPEC'],
                ['MODBUS_REG_40003', 'Operating Temperature', machine.temperatureC, '°C', machine.temperatureC > machine.thermalThresholdC ? 'ALARM' : 'NORMAL'],
                ['MODBUS_REG_40004', 'Thermal Threshold', machine.thermalThresholdC, '°C', 'THRESHOLD'],
                ['MODBUS_REG_40005', 'Voltage L1', machine.voltage.l1, 'V', 'NOMINAL'],
                ['MODBUS_REG_40006', 'Voltage L2', machine.voltage.l2, 'V', 'NOMINAL'],
                ['MODBUS_REG_40007', 'Voltage L3', machine.voltage.l3, 'V', 'NOMINAL'],
                ['MODBUS_REG_40008', 'Voltage Line-to-Line', machine.voltage.lineToLine, 'V', 'NOMINAL'],
                ['MODBUS_REG_40009', 'Voltage Unbalance', `${machine.voltage.unbalancePercent}%`, '%', 'BALANCED'],
                ['MODBUS_REG_40010', 'Current Phase L1', machine.current.l1, 'A', 'NORMAL'],
                ['MODBUS_REG_40011', 'Current Phase L2', machine.current.l2, 'A', 'NORMAL'],
                ['MODBUS_REG_40012', 'Current Phase L3', machine.current.l3, 'A', 'NORMAL'],
                ['MODBUS_REG_40013', 'Power Factor', machine.powerFactor, 'cos φ', machine.powerFactor >= 0.9 ? 'COMPLIANT' : 'LOW_PF'],
                ['MODBUS_REG_40014', 'Total Lifetime Runtime', machine.runtimeHoursTotal, 'hours', 'CUMULATIVE'],
                ['MODBUS_REG_40015', 'Shift Runtime', machine.runtimeHoursShift, 'hours', 'CURRENT_SHIFT'],
                ['MODBUS_REG_40016', 'MTBF Metric', machine.mtbfHours, 'hours', 'RELIABILITY'],
                ['MODBUS_REG_40017', 'MTTR Metric', machine.mttrHours, 'hours', 'MAINTAINABILITY'],
                ['MODBUS_REG_40018', 'Component Health Score', `${machine.healthScore}/100`, 'score', 'INDEX'],
                ['MODBUS_REG_40019', 'Failure Probability (72h)', `${(machine.failureProbability72h * 100).toFixed(1)}%`, 'risk', 'PREDICTIVE'],
                ['MODBUS_REG_40020', 'Energy Consumption Today', machine.energyTodayKwh, 'kWh', 'METERED'],
                ['MODBUS_REG_40021', 'Carbon Footprint Today', machine.carbonTodayKg, 'kg CO2e', 'GHG_SCOPE2'],
              ]
              exportToCsv(`greenpulse_scada_${machine.code.toLowerCase()}_tags`, headers, rows)
              toast.info('Raw SCADA register dump', {
                description: `Exported 21 Modbus telemetry registers for ${machine.name} as CSV.`,
              })
            }}
          >
            <Download className="size-3.5" />
            Download Tags
          </Button>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs"
              onClick={onClose}
            >
              Close
            </Button>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                toast.success('Diagnostic initiated', {
                  description: `Edge gateway executing high-speed sampling diagnostic on ${machine.name}.`,
                })
              }}
            >
              <Activity className="size-3.5" />
              Run Diagnostics
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
