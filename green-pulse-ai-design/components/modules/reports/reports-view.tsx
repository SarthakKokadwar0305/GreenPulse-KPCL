'use client'

import {
  AlertTriangle,
  Calendar,
  CheckCircle2,
  Clock,
  Download,
  Eye,
  FileCheck,
  FileSpreadsheet,
  FileText,
  Filter,
  Layers,
  Leaf,
  Mail,
  Play,
  Printer,
  Search,
  Sparkles,
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
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { useReportsData } from '@/hooks/use-module-data'
import type { IndustrialReport, ScheduledReportConfig } from '@/types'
import { exportAuditDocument } from '@/lib/export-utils'

type ReportCategoryFilter = 'all' | 'energy' | 'carbon' | 'forecast' | 'anomaly'

export function ReportsView() {
  const { data, isLoading, isError, refetch } = useReportsData()
  const [categoryFilter, setCategoryFilter] = useState<ReportCategoryFilter>('all')
  const [selectedReportForPreview, setSelectedReportForPreview] = useState<IndustrialReport | null>(null)
  const [scheduledReportsList, setScheduledReportsList] = useState<ScheduledReportConfig[]>([])

  // initialize scheduled reports state when data loads
  useState(() => {
    if (data?.scheduledReports) {
      setScheduledReportsList(data.scheduledReports)
    }
  })

  if (isLoading) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Compliance & Governance"
          title="Industrial Reporting Suite"
          description="Automated energy audits, carbon disclosure filings, and scheduled reporting pipelines."
        />
        <LoadingPanel className="min-h-96" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <Surface className="flex min-h-96 flex-col items-center justify-center gap-4 p-8 text-center">
        <FileText className="size-12 text-destructive" />
        <h2 className="text-xl font-semibold text-foreground">Report Repository Unavailable</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Document generation queue service is temporarily unreachable.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Reconnect Report Service
        </Button>
      </Surface>
    )
  }

  const reports = data.recentReports
  const scheduled = data.scheduledReports

  const filteredReports = reports.filter((r) => {
    if (categoryFilter !== 'all' && r.category !== categoryFilter) return false
    return true
  })

  const handleExport = (format: 'PDF' | 'CSV' | 'Excel' | 'JSON', reportTitle: string) => {
    const matched = reports.find(r => r.title === reportTitle)
    const stats = matched?.summaryStats || [
      { label: 'Energy Total', value: '218,450 kWh' },
      { label: 'Peak Demand', value: '1,810 kW' },
      { label: 'Compliance Score', value: '99.4%' }
    ]
    exportAuditDocument(
      reportTitle,
      matched?.category || 'Compliance Audit',
      format,
      {
        'Report ID': matched?.id || 'REP-EXP-2026',
        'Reporting Period': matched?.period || 'October 2026',
        'Author Authority': matched?.author || 'GreenPulse Certified Compliance System',
        'File Format': format,
        'Compliance Verification': 'ISO 50001 & GHG Scope 1/2 Certified',
      },
      stats
    )
    toast.success(`Exporting ${format}`, {
      description: `Downloaded "${reportTitle}" formatted as enterprise ${format}.`,
    })
  }

  const handleToggleSchedule = (id: string, name: string) => {
    toast.info('Schedule Updated', {
      description: `Automated dispatch cadence updated for "${name}".`,
    })
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="Compliance & Audit Trail"
        title="Industrial Reports & ESG Filings"
        description="Comprehensive audit-grade report generator for Energy Audits (ISO 50001), GHG Disclosures (Scope 1/2), AI Peak Forecasts, and Equipment RCA Incident logs."
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => handleExport('PDF', 'Consolidated Plant Energy & Carbon Pack')}
            >
              <Download className="size-3.5" />
              Batch Download All
            </Button>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                toast.success('Custom Report Compiled', {
                  description: 'Compiled real-time plant snapshot into newly generated PDF.',
                })
              }}
            >
              <Sparkles className="size-3.5" />
              Compile New Report
            </Button>
          </div>
        }
      />

      {/* Control Bar: Categories & Quick Export */}
      <Surface className="flex flex-wrap items-center justify-between gap-4 p-4">
        <SegmentedControl
          value={categoryFilter}
          options={[
            { value: 'all', label: 'All Reports', count: reports.length },
            { value: 'energy', label: 'Energy Audits' },
            { value: 'carbon', label: 'Carbon / ESG' },
            { value: 'forecast', label: 'Forecasts' },
            { value: 'anomaly', label: 'Anomaly Logs' },
          ]}
          onChange={setCategoryFilter}
          ariaLabel="Report category filter"
        />

        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Direct Formats:</span>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 text-xs text-primary"
            onClick={() => handleExport('PDF', 'Latest Report')}
          >
            PDF
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 text-xs text-primary"
            onClick={() => handleExport('CSV', 'Telemetry CSV')}
          >
            CSV
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 text-xs text-primary"
            onClick={() => handleExport('Excel', 'Worksheet XLSX')}
          >
            Excel
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 text-xs text-primary"
            onClick={() => handleExport('JSON', 'Raw Telemetry JSON')}
          >
            JSON
          </Button>
        </div>
      </Surface>

      {/* Reports Library Grid */}
      <section aria-label="Generated Industrial Reports" className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {filteredReports.map((report, index) => {
          const isEnergy = report.category === 'energy'
          const isCarbon = report.category === 'carbon'
          const isForecast = report.category === 'forecast'

          return (
            <Reveal key={report.id} index={index}>
              <Surface className="flex flex-col justify-between gap-4 p-5 hover:border-primary/40 transition-all">
                <div className="flex flex-col gap-2">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <div
                        className={`size-8 rounded-tile flex items-center justify-center ${
                          isEnergy
                            ? 'bg-primary/10 text-primary'
                            : isCarbon
                              ? 'bg-success/10 text-success'
                              : isForecast
                                ? 'bg-indigo-500/10 text-indigo-500'
                                : 'bg-warning/15 text-warning-ink'
                        }`}
                      >
                        {isEnergy ? <Zap className="size-4" /> : isCarbon ? <Leaf className="size-4" /> : <FileText className="size-4" />}
                      </div>
                      <Badge variant="outline" className="text-[10px] uppercase font-mono">
                        {report.category}
                      </Badge>
                    </div>

                    <ToneBadge tone="success">
                      {report.status.toUpperCase()}
                    </ToneBadge>
                  </div>

                  <h3 className="text-base font-bold text-foreground leading-snug mt-1">
                    {report.title}
                  </h3>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    <span>Period: <strong className="text-foreground">{report.period}</strong></span>
                    <span>•</span>
                    <span>Size: {report.fileSize}</span>
                    <span>•</span>
                    <span>Author: {report.author}</span>
                  </div>
                </div>

                {/* Key Summary Stats in Report */}
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 rounded-lg border bg-muted/20 p-2.5 text-center text-xs">
                  {report.summaryStats.map((st, idx) => (
                    <div key={idx}>
                      <span className="text-[10px] text-muted-foreground">{st.label}</span>
                      <p className="font-bold text-foreground tabular-nums mt-0.5">{st.value}</p>
                    </div>
                  ))}
                </div>

                {/* Action Buttons: Preview & Export */}
                <div className="flex items-center justify-between gap-2 border-t pt-3">
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs gap-1.5"
                    onClick={() => setSelectedReportForPreview(report)}
                  >
                    <Eye className="size-3.5" />
                    PDF Preview
                  </Button>

                  <div className="flex items-center gap-1.5">
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-xs"
                      onClick={() => handleExport('CSV', report.title)}
                    >
                      CSV
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-xs"
                      onClick={() => handleExport('Excel', report.title)}
                    >
                      Excel
                    </Button>
                    <Button
                      size="sm"
                      className="text-xs gap-1.5"
                      onClick={() => handleExport('PDF', report.title)}
                    >
                      <Download className="size-3.5" />
                      PDF
                    </Button>
                  </div>
                </div>
              </Surface>
            </Reveal>
          )
        })}
      </section>

      {/* Scheduled Automated Reports Table */}
      <Surface className="flex flex-col gap-4 p-5">
        <SectionHeader
          title="Automated Scheduled Report Pipelines"
          description="Standing automated email digests and regulatory filings dispatched on shift, weekly, and monthly schedules."
          icon={Clock}
        />

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b bg-muted/30 text-muted-foreground font-semibold">
              <tr>
                <th className="py-3 px-4">Report Name</th>
                <th className="py-3 px-4">Cadence</th>
                <th className="py-3 px-4">Dispatch Time</th>
                <th className="py-3 px-4">Recipients</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {scheduled.map((sch) => (
                <tr key={sch.id} className="hover:bg-muted/20">
                  <td className="py-3 px-4 font-semibold text-foreground">{sch.name}</td>
                  <td className="py-3 px-4 text-muted-foreground">{sch.frequency}</td>
                  <td className="py-3 px-4 font-mono text-muted-foreground">{sch.sendTime}</td>
                  <td className="py-3 px-4 text-muted-foreground">{sch.recipients.join(', ')}</td>
                  <td className="py-3 px-4">
                    <Badge variant="outline" className="font-mono text-[10px]">{sch.format}</Badge>
                  </td>
                  <td className="py-3 px-4">
                    <ToneBadge tone={sch.active ? 'success' : 'neutral'}>
                      {sch.active ? 'Active' : 'Paused'}
                    </ToneBadge>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-7 text-xs text-primary"
                      onClick={() => {
                        toast.success('Report Dispatched Now', {
                          description: `Triggered manual test dispatch for "${sch.name}".`,
                        })
                      }}
                    >
                      Run Now
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Surface>

      {/* PDF Interactive Preview Sheet / Modal */}
      <Sheet open={Boolean(selectedReportForPreview)} onOpenChange={(open) => !open && setSelectedReportForPreview(null)}>
        <SheetContent side="right" className="w-full gap-0 overflow-y-auto sm:max-w-2xl p-0">
          {selectedReportForPreview && (
            <>
              <SheetHeader className="gap-2 border-b p-6 bg-card">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="font-mono uppercase text-[10px]">
                    {selectedReportForPreview.category} Document Preview
                  </Badge>
                  <ToneBadge tone="success">Verified Audit Grade</ToneBadge>
                </div>
                <SheetTitle className="text-xl font-bold text-foreground">
                  {selectedReportForPreview.title}
                </SheetTitle>
                <SheetDescription className="text-xs text-muted-foreground">
                  Reporting Period: {selectedReportForPreview.period} · Generated by {selectedReportForPreview.author}
                </SheetDescription>
              </SheetHeader>

              {/* Realistic Enterprise PDF Document Paper Preview */}
              <div className="flex flex-col gap-6 p-6 bg-muted/10">
                <div className="rounded-lg border bg-card p-6 shadow-card flex flex-col gap-6">
                  {/* Document Letterhead */}
                  <div className="flex items-center justify-between border-b pb-4">
                    <div>
                      <h2 className="text-lg font-black tracking-tight text-foreground">GREENPULSE AI</h2>
                      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Industrial Energy Intelligence Platform</p>
                    </div>
                    <div className="text-right text-xs text-muted-foreground">
                      <p className="font-semibold text-foreground">Plant #4 - Chakan, Pune</p>
                      <p>Doc Ref: GP-{selectedReportForPreview.id.toUpperCase()}-2026</p>
                      <p>{new Date(selectedReportForPreview.generatedAt).toLocaleString()}</p>
                    </div>
                  </div>

                  {/* Document Abstract & Scope */}
                  <div className="flex flex-col gap-2">
                    <h4 className="text-xs font-bold uppercase tracking-wide text-foreground">1. Executive Summary & Audit Scope</h4>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      This official compliance audit report documents electrical power demand, volumetric fluid consumption, and calculated carbon emissions for the manufacturing facility. All telemetry records are cryptographically timestamped and aligned with Bureau of Energy Efficiency (BEE) and ISO 50001 supervisory energy standards.
                    </p>
                  </div>

                  {/* Summary Metric Table */}
                  <div className="flex flex-col gap-2">
                    <h4 className="text-xs font-bold uppercase tracking-wide text-foreground">2. Supervisory Metrics Summary</h4>
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 rounded-md border p-3 text-center">
                      {selectedReportForPreview.summaryStats.map((st, i) => (
                        <div key={i} className="flex flex-col">
                          <span className="text-[10px] text-muted-foreground">{st.label}</span>
                          <span className="text-sm font-bold text-foreground tabular-nums">{st.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Regulatory Compliance Sign-off Block */}
                  <div className="flex flex-col gap-2 border-t pt-4">
                    <h4 className="text-xs font-bold uppercase tracking-wide text-foreground">3. Certified Sign-off & Verification</h4>
                    <div className="grid grid-cols-2 gap-4 text-xs pt-2">
                      <div className="rounded-md border p-3 bg-muted/20">
                        <span className="text-[10px] text-muted-foreground">Certified Energy Auditor</span>
                        <p className="font-semibold text-foreground mt-1">Elena Vance, CEM</p>
                        <p className="text-[10px] text-success font-medium">BEE Reg: EA-94821 / Valid</p>
                      </div>
                      <div className="rounded-md border p-3 bg-muted/20">
                        <span className="text-[10px] text-muted-foreground">Plant Lead Engineer</span>
                        <p className="font-semibold text-foreground mt-1">Vikramaditya Sharma</p>
                        <p className="text-[10px] text-muted-foreground">Cryptographic Hash: 8f4c12...OK</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Preview Footer Actions */}
              <div className="sticky bottom-0 border-t bg-card/95 backdrop-blur p-4 flex items-center justify-between gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs gap-1.5"
                  onClick={() => {
                    window.print()
                  }}
                >
                  <Printer className="size-3.5" />
                  Print Document
                </Button>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-xs"
                    onClick={() => setSelectedReportForPreview(null)}
                  >
                    Close Preview
                  </Button>
                  <Button
                    size="sm"
                    className="text-xs gap-1.5"
                    onClick={() => handleExport('PDF', selectedReportForPreview.title)}
                  >
                    <Download className="size-3.5" />
                    Download PDF
                  </Button>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  )
}
