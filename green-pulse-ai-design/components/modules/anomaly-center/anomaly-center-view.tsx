'use client'

import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Clock,
  Cpu,
  Download,
  Filter,
  IndianRupee,
  Info,
  Layers,
  Search,
  ShieldAlert,
  Siren,
  Sparkles,
  Wrench,
  Zap,
} from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { Reveal } from '@/components/motion/reveal'
import { IconTile } from '@/components/shared/icon-tile'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { MeterBar } from '@/components/shared/meter-bar'
import { PageHeader } from '@/components/shared/page-header'
import { SectionHeader } from '@/components/shared/section-header'
import { SegmentedControl } from '@/components/shared/segmented-control'
import { Surface } from '@/components/shared/surface'
import { ToneBadge } from '@/components/shared/tone-badge'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAnomaliesData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'
import { exportToCsv } from '@/lib/export-utils'
import type { AnomalyIncident } from '@/types'

type SeverityFilter = 'all' | 'critical' | 'warning' | 'info'
type StatusFilter = 'all' | 'open' | 'investigating' | 'acknowledged' | 'resolved'

export function AnomalyCenterView() {
  const { data: anomalies, isLoading, isError, refetch } = useAnomaliesData()
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('all')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [acknowledgedIds, setAcknowledgedIds] = useState<Set<string>>(new Set())

  if (isLoading) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Fault Detection & Diagnostics (FDD)"
          title="Anomaly Center"
          description="Industrial AI anomaly detection, root cause failure analysis, and remediation incident tracking."
        />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <LoadingPanel key={i} className="min-h-64" />
          ))}
        </div>
      </div>
    )
  }

  if (isError || !anomalies) {
    return (
      <Surface className="flex min-h-96 flex-col items-center justify-center gap-4 p-8 text-center">
        <Siren className="size-12 text-destructive" />
        <h2 className="text-xl font-semibold text-foreground">Failed to Load Anomaly Incident Stream</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Real-time unsupervised autoencoder telemetry pipeline disconnected.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Reconnect Pipeline
        </Button>
      </Surface>
    )
  }

  // Filter anomalies
  const filteredAnomalies = anomalies.filter((a) => {
    if (severityFilter !== 'all' && a.severity !== severityFilter) return false
    if (statusFilter !== 'all' && a.status !== statusFilter) return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      return (
        a.machineName.toLowerCase().includes(q) ||
        a.rootCause.toLowerCase().includes(q) ||
        a.suggestedAction.toLowerCase().includes(q) ||
        a.zone.toLowerCase().includes(q)
      )
    }
    return true
  })

  const openCount = anomalies.filter((a) => a.status === 'open' || a.status === 'investigating').length
  const totalCostRate = anomalies
    .filter((a) => a.status !== 'resolved')
    .reduce((sum, a) => sum + a.estimatedCostImpactPerHour, 0)

  const handleAcknowledge = (id: string, machineName: string) => {
    setAcknowledgedIds((prev) => new Set(prev).add(id))
    toast.success('Incident Acknowledged', {
      description: `Anomaly on ${machineName} marked acknowledged. Maintenance tech alerted.`,
    })
  }

  const handleDispatchWorkOrder = (a: AnomalyIncident) => {
    toast.success('Work Order Created', {
      description: `Dispatched work order WO-2026-${a.id.slice(-3)} for ${a.machineName}. Assigned to ${a.assignedEngineer ?? 'Lead Tech'}.`,
    })
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="Automated Fault Detection & Diagnostics"
        title="Anomaly Center"
        description="Real-time multi-variate machine learning detection of equipment degradation, acoustic ultrasound valve leakage, cavitation, and thermal refractory losses."
        meta={
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Active Incidents: <strong className="text-warning-ink">{openCount} Unresolved</strong></span>
            <span>•</span>
            <span>Cumulative Risk Rate: <strong className="text-destructive">${totalCostRate}/hr (~₹{formatNumber(totalCostRate * 82)}/hr)</strong></span>
            <span>•</span>
            <span>Mean Time to Detect (MTTD): <strong className="text-foreground">3.4 mins</strong></span>
          </div>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                const headers = ['Incident ID', 'Machine ID', 'Machine Name', 'Severity', 'Root Cause', 'Confidence', 'Estimated Impact (INR)', 'Status']
                const rows = anomalies.map(a => [
                  a.id,
                  a.machineId,
                  a.machineName,
                  a.severity,
                  a.rootCause,
                  `${(a.confidenceScore * 100).toFixed(0)}%`,
                  a.estimatedCostImpactInr,
                  acknowledgedIds.has(a.id) ? 'acknowledged' : a.status
                ])
                exportToCsv('greenpulse_anomaly_incidents_audit', headers, rows)
                toast.success('Incident Log Exported', {
                  description: 'Exported active incident table with raw telemetry evidence as CSV.',
                })
              }}
            >
              <Download className="size-3.5" />
              Export Incident Log
            </Button>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                refetch()
                toast.success('Anomaly Scans Refreshed', {
                  description: 'Unsupervised Autoencoder completed pass on 4,200 sensor channels.',
                })
              }}
            >
              <Sparkles className="size-3.5" />
              Re-scan Telemetry
            </Button>
          </div>
        }
      />

      {/* Control Bar: Filters & Search */}
      <Surface className="flex flex-wrap items-center justify-between gap-4 p-4">
        <div className="flex flex-wrap items-center gap-3">
          <SegmentedControl
            value={severityFilter}
            options={[
              { value: 'all', label: 'All Severities', count: anomalies.length },
              { value: 'critical', label: 'Critical' },
              { value: 'warning', label: 'Warning' },
              { value: 'info', label: 'Advisory' },
            ]}
            onChange={setSeverityFilter}
            ariaLabel="Severity filter"
          />

          <div className="relative w-48 sm:w-64">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
            <Input
              placeholder="Filter by machine, root cause, action..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 pl-8 text-xs"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs font-mono">
            Showing {filteredAnomalies.length} of {anomalies.length} Incidents
          </Badge>
        </div>
      </Surface>

      {/* Professional Incident Cards Grid */}
      <section aria-label="Incident Cards" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {filteredAnomalies.map((anomaly, index) => {
          const isAcked = acknowledgedIds.has(anomaly.id) || anomaly.status === 'acknowledged' || anomaly.status === 'resolved'
          const isCritical = anomaly.severity === 'critical'
          const isWarning = anomaly.severity === 'warning'

          const borderStyle = isCritical
            ? 'border-destructive/40 hover:border-destructive'
            : isWarning
              ? 'border-warning/50 hover:border-warning'
              : 'border-border hover:border-primary/40'

          return (
            <Reveal key={anomaly.id} index={index}>
              <Surface className={`flex flex-col justify-between gap-4 p-5 transition-all duration-200 ${borderStyle}`}>
                {/* Incident Card Header */}
                <div className="flex items-start justify-between gap-3 border-b pb-3">
                  <div className="flex items-center gap-3">
                    <div
                      className={`size-10 rounded-tile flex items-center justify-center ${
                        isCritical
                          ? 'bg-destructive/10 text-destructive'
                          : isWarning
                            ? 'bg-warning/15 text-warning-ink'
                            : 'bg-primary/10 text-primary'
                      }`}
                    >
                      {isCritical ? <ShieldAlert className="size-5" /> : isWarning ? <AlertTriangle className="size-5" /> : <Info className="size-5" />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-base font-bold text-foreground">{anomaly.machineName}</h3>
                        <Badge variant="outline" className="font-mono text-[10px]">{anomaly.zone}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Detected: {new Date(anomaly.detectedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} ({anomaly.durationMinutes} mins active)
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-1">
                    <ToneBadge
                      tone={isCritical ? 'danger' : isWarning ? 'warning' : 'info'}
                      pulse={anomaly.status === 'open' && (isCritical || isWarning)}
                    >
                      {anomaly.severity.toUpperCase()}
                    </ToneBadge>
                    <span className="text-[10px] font-mono text-muted-foreground uppercase">{anomaly.status}</span>
                  </div>
                </div>

                {/* Root Cause & Confidence */}
                <div className="flex flex-col gap-2">
                  <div className="flex items-baseline justify-between">
                    <span className="text-xs font-semibold text-foreground uppercase tracking-wide">Root Cause Failure Hypothesis</span>
                    <span className="text-xs font-semibold text-primary">
                      AI Confidence: {anomaly.confidencePercent}%
                    </span>
                  </div>
                  <p className="text-sm font-medium text-foreground bg-muted/20 rounded-md p-2.5 border">
                    {anomaly.rootCause}
                  </p>
                </div>

                {/* Evidence Telemetry Badges */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Sensor Telemetry Evidence</span>
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                    {anomaly.evidence.map((ev, i) => (
                      <div key={i} className="flex flex-col rounded-md border bg-card p-2 text-xs">
                        <span className="text-[10px] text-muted-foreground truncate">{ev.metric}</span>
                        <span className="font-bold text-foreground tabular-nums">{ev.measured}</span>
                        <span className="text-[10px] text-muted-foreground">Normal: {ev.expected}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Suggested Action */}
                <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs flex flex-col gap-1">
                  <span className="font-bold text-primary flex items-center gap-1.5">
                    <Wrench className="size-3.5" />
                    Prescribed Maintenance Action:
                  </span>
                  <p className="text-muted-foreground leading-relaxed">
                    {anomaly.suggestedAction}
                  </p>
                </div>

                {/* Cost Impact & Card Actions */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-t pt-3">
                  <div className="flex flex-col">
                    <span className="text-[11px] text-muted-foreground">Estimated Financial Impact</span>
                    <span className="text-sm font-bold text-destructive tabular-nums">
                      ${anomaly.estimatedCostImpactPerHour}/hr <span className="text-xs font-normal text-muted-foreground">({anomaly.currency})</span>
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {!isAcked && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs"
                        onClick={() => handleAcknowledge(anomaly.id, anomaly.machineName)}
                      >
                        Acknowledge
                      </Button>
                    )}
                    <Button
                      size="sm"
                      className="text-xs gap-1.5"
                      onClick={() => handleDispatchWorkOrder(anomaly)}
                    >
                      <Wrench className="size-3.5" />
                      Create Work Order
                    </Button>
                  </div>
                </div>
              </Surface>
            </Reveal>
          )
        })}
      </section>

      {filteredAnomalies.length === 0 && (
        <Surface className="flex min-h-[300px] flex-col items-center justify-center gap-3 p-8 text-center">
          <CheckCircle2 className="size-12 text-success" />
          <h3 className="text-base font-semibold text-foreground">Zero Anomaly Incidents in Filter</h3>
          <p className="text-xs text-muted-foreground max-w-sm">
            All equipment operates within nominal statistical process control (SPC) bands.
          </p>
          <Button size="sm" variant="outline" onClick={() => { setSeverityFilter('all'); setSearchQuery('') }}>
            Reset Filters
          </Button>
        </Surface>
      )}
    </div>
  )
}
