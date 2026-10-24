'use client'

import {
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  Check,
  CheckCircle2,
  Clock,
  Cpu,
  Download,
  IndianRupee,
  Layers,
  Leaf,
  Lightbulb,
  PiggyBank,
  Play,
  RotateCcw,
  Sparkles,
  TrendingUp,
  Zap,
} from 'lucide-react'
import Link from 'next/link'
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
import { Button, buttonVariants } from '@/components/ui/button'
import { ROUTES } from '@/config/routes'
import { useRecommendationsData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'
import { exportAuditDocument } from '@/lib/export-utils'
import type { AiRecommendation } from '@/types'

type CategoryFilter = 'all' | 'Load Shifting' | 'Asset Tuning' | 'Automation' | 'Maintenance' | 'Renewables'

export function RecommendationCenterView() {
  const { data: recommendations, isLoading, isError, refetch } = useRecommendationsData()
  const [selectedCategory, setSelectedCategory] = useState<CategoryFilter>('all')
  const [appliedMap, setAppliedMap] = useState<Record<string, boolean>>({})

  if (isLoading) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Energy Conservation Measures (ECMs)"
          title="Recommendation Center"
          description="AI-driven energy saving strategies, load shifting, and asset optimization measures."
        />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <LoadingPanel key={i} className="min-h-64" />
          ))}
        </div>
      </div>
    )
  }

  if (isError || !recommendations) {
    return (
      <Surface className="flex min-h-96 flex-col items-center justify-center gap-4 p-8 text-center">
        <Lightbulb className="size-12 text-destructive" />
        <h2 className="text-xl font-semibold text-foreground">Failed to Load AI Recommendations</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Autonomous energy conservation reasoning agent did not return recommendations.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Retry Agent Pass
        </Button>
      </Surface>
    )
  }

  // Filter recommendations
  const filteredRecs = recommendations.filter((r) => {
    if (selectedCategory !== 'all' && r.category !== selectedCategory) return false
    return true
  })

  // Cumulative potential calculations
  const totalKwhSavings = recommendations.reduce((sum, r) => sum + r.estimatedSavingsKwhPerMonth, 0)
  const totalCurrencySavings = recommendations.reduce((sum, r) => sum + r.estimatedSavingsCurrencyPerMonth, 0)
  const totalCarbonReduction = recommendations.reduce((sum, r) => sum + r.estimatedCarbonReductionTonsPerMonth, 0)

  const handleApply = (id: string, title: string) => {
    setAppliedMap((prev) => ({ ...prev, [id]: true }))
    toast.success('Recommendation Applied', {
      description: `Optimized schedule and PLC parameter adjustment queued for: "${title}".`,
    })
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="AI-Powered Optimization"
        title="Recommendation Center"
        description="Prescriptive Energy Conservation Measures (ECMs) calculated using neural reinforcement learning models, tariff schedules, and thermodynamic efficiency baselines."
        meta={
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Identified ECMs: <strong className="text-foreground">{recommendations.length} Active</strong></span>
            <span>•</span>
            <span>Monthly Potential: <strong className="text-success">₹{formatNumber(totalCurrencySavings)} / mo</strong></span>
            <span>•</span>
            <span>Carbon Reduction: <strong className="text-success">{totalCarbonReduction.toFixed(1)} t CO₂e / mo</strong></span>
          </div>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                exportAuditDocument(
                  'Energy Conservation Measures (ECM) Prescriptive Action Plan',
                  'Recommendations',
                  'PDF',
                  {
                    'Total Measures': recommendations.length,
                    'Identified Monthly Savings': `₹${formatNumber(totalCurrencySavings)}/mo`,
                    'Annualized Savings': `₹${formatNumber(totalCurrencySavings * 12)}/yr`,
                    'Energy Avoidance': `${formatNumber(recommendations.reduce((acc, r) => acc + r.monthlyEnergySavingsKwh, 0))} kWh/mo`,
                    'Carbon Abatement': `${recommendations.reduce((acc, r) => acc + r.monthlyCarbonSavingsTons, 0).toFixed(1)} tCO2e/mo`,
                    'Prioritization Methodology': 'Multi-Criteria Decision Analysis (MCDA) + ROI',
                  },
                  [
                    { label: 'Monthly Savings', value: `₹${formatNumber(totalCurrencySavings)}` },
                    { label: 'Total Measures', value: `${recommendations.length}` },
                    { label: 'Implemented Count', value: `${implementedIds.size}` },
                  ],
                  {
                    headers: ['Title', 'Category', 'Target Asset', 'Payback', 'Monthly Savings (INR)', 'Difficulty'],
                    rows: recommendations.map(r => [
                      r.title,
                      r.category,
                      r.targetAsset,
                      r.paybackPeriod,
                      `₹${formatNumber(r.monthlySavingsInr)}`,
                      r.implementationDifficulty.toUpperCase()
                    ])
                  }
                )
                toast.success('Action Plan Exported', {
                  description: 'Exported comprehensive ECM prescriptive ledger as audit document.',
                })
              }}
            >
              <Download className="size-3.5" />
              Export Action Plan
            </Button>
            <Link
              href={ROUTES.whatIfSimulator}
              className={buttonVariants({ variant: 'outline', size: 'sm', className: 'text-xs gap-1.5' })}
            >
              <Play className="size-3.5" />
              Simulate in What-If
            </Link>
            <Button
              size="sm"
              className="text-xs gap-1.5"
              onClick={() => {
                refetch()
                toast.success('Recommendations Recalculated', {
                  description: 'Queried latest equipment telemetry and tariff rates.',
                })
              }}
            >
              <Sparkles className="size-3.5" />
              Re-evaluate ECMs
            </Button>
          </div>
        }
      />

      {/* Cumulative Impact Banner */}
      <section aria-label="Cumulative Potential Banner" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Surface className="flex flex-col gap-2 p-5 border-primary/20 bg-primary/5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-primary uppercase">Total Monthly Savings</span>
            <PiggyBank className="size-5 text-primary" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            ₹{formatNumber(totalCurrencySavings)} <span className="text-xs font-normal text-muted-foreground">/ month</span>
          </p>
          <span className="text-xs text-muted-foreground border-t pt-2 border-primary/20">
            Across {recommendations.length} identified measures
          </span>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Energy Avoidance</span>
            <Zap className="size-5 text-primary" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            {formatNumber(totalKwhSavings)} <span className="text-xs font-normal text-muted-foreground">kWh / mo</span>
          </p>
          <span className="text-xs text-muted-foreground border-t pt-2">
            ~7.2% of total plant energy budget
          </span>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Carbon Abatement</span>
            <Leaf className="size-5 text-success" />
          </div>
          <p className="text-2xl font-bold text-success tabular-nums">
            {totalCarbonReduction.toFixed(1)} <span className="text-xs font-normal text-muted-foreground">t CO₂e / mo</span>
          </p>
          <span className="text-xs text-muted-foreground border-t pt-2">
            Equivalent to planting ~3,200 urban trees
          </span>
        </Surface>

        <Surface className="flex flex-col gap-2 p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Average Payback</span>
            <TrendingUp className="size-5 text-primary" />
          </div>
          <p className="text-2xl font-bold text-foreground tabular-nums">
            3.8 <span className="text-xs font-normal text-muted-foreground">months</span>
          </p>
          <span className="text-xs text-muted-foreground border-t pt-2">
            High ROI with low capital expenditure
          </span>
        </Surface>
      </section>

      {/* Control Bar: Category Filters */}
      <Surface className="flex flex-wrap items-center justify-between gap-4 p-4">
        <SegmentedControl
          value={selectedCategory}
          options={[
            { value: 'all', label: 'All Measures', count: recommendations.length },
            { value: 'Load Shifting', label: 'Load Shifting' },
            { value: 'Asset Tuning', label: 'Asset Tuning' },
            { value: 'Automation', label: 'Automation' },
            { value: 'Renewables', label: 'Renewables' },
          ]}
          onChange={setSelectedCategory}
          ariaLabel="Category filter"
        />

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Click "Apply" to queue automated parameter optimization directly into SCADA.</span>
        </div>
      </Surface>

      {/* Recommendations Cards Grid */}
      <section aria-label="Recommendation Cards" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {filteredRecs.map((rec, index) => {
          const isApplied = appliedMap[rec.id] || rec.applied
          const isHigh = rec.priority === 'High'

          return (
            <Reveal key={rec.id} index={index}>
              <Surface className={`flex flex-col justify-between gap-5 p-6 transition-all duration-200 ${
                isApplied ? 'border-success/40 bg-success/5' : isHigh ? 'border-primary/40 hover:border-primary' : 'border-border'
              }`}>
                {/* Header: Title, Machine, Priority */}
                <div className="flex flex-col gap-2 border-b pb-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[11px] text-muted-foreground">
                        {rec.machineName}
                      </Badge>
                      <Badge variant="secondary" className="text-[11px]">
                        {rec.category}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-2">
                      <ToneBadge tone={rec.priority === 'High' ? 'danger' : rec.priority === 'Medium' ? 'warning' : 'neutral'}>
                        {rec.priority} Priority
                      </ToneBadge>
                      <ToneBadge tone="info" className="text-[10px]">
                        {rec.confidencePercent}% Confidence
                      </ToneBadge>
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-foreground leading-snug">
                    {rec.title}
                  </h3>
                </div>

                {/* Rationale Body */}
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {rec.rationale}
                </p>

                {/* Key Metrics Grid: Savings, Carbon, ROI */}
                <div className="grid grid-cols-3 gap-3 rounded-lg border bg-muted/20 p-3 text-center text-xs">
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase font-medium">Monthly Savings</span>
                    <p className="text-sm font-bold text-success tabular-nums">
                      ₹{formatNumber(rec.estimatedSavingsCurrencyPerMonth)}
                    </p>
                    <span className="text-[10px] text-muted-foreground">{formatNumber(rec.estimatedSavingsKwhPerMonth)} kWh</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase font-medium">Carbon Reduction</span>
                    <p className="text-sm font-bold text-success tabular-nums">
                      {rec.estimatedCarbonReductionTonsPerMonth} t
                    </p>
                    <span className="text-[10px] text-muted-foreground">CO₂e / mo</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase font-medium">Payback / ROI</span>
                    <p className="text-sm font-bold text-foreground tabular-nums">
                      {rec.paybackPeriodMonths === 0 ? 'Instant' : `${rec.paybackPeriodMonths} mos`}
                    </p>
                    <span className="text-[10px] text-primary">{rec.roiPercent}% ROI</span>
                  </div>
                </div>

                {/* Action Checklist */}
                <div className="flex flex-col gap-1.5 rounded-lg border bg-card p-3 text-xs">
                  <span className="font-semibold text-foreground">Action Implementation Steps:</span>
                  <ul className="list-disc pl-4 text-muted-foreground space-y-0.5">
                    {rec.actionSteps.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                </div>

                {/* Card Footer: Apply Button */}
                <div className="flex items-center justify-between gap-3 border-t pt-3">
                  <div className="text-xs text-muted-foreground">
                    {isApplied ? (
                      <span className="font-semibold text-success flex items-center gap-1.5">
                        <CheckCircle2 className="size-4" /> Optimization Active in SCADA
                      </span>
                    ) : (
                      <span>Ready for supervisory deployment</span>
                    )}
                  </div>

                  <Button
                    size="sm"
                    variant={isApplied ? 'outline' : 'default'}
                    className={`text-xs gap-1.5 ${isApplied ? 'text-success border-success/30' : ''}`}
                    onClick={() => handleApply(rec.id, rec.title)}
                  >
                    {isApplied ? (
                      <>
                        <Check className="size-3.5" />
                        Applied
                      </>
                    ) : (
                      <>
                        <Sparkles className="size-3.5" />
                        Apply Recommendation
                      </>
                    )}
                  </Button>
                </div>
              </Surface>
            </Reveal>
          )
        })}
      </section>
    </div>
  )
}
