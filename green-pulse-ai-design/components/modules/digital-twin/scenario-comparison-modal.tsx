'use client'

import {
  Activity,
  ArrowRight,
  BarChart3,
  Check,
  CheckCircle2,
  Cpu,
  Download,
  Gauge,
  IndianRupee,
  Layers,
  Leaf,
  Plus,
  ShieldAlert,
  Sparkles,
  Trash2,
  TrendingDown,
  X,
  Zap,
} from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Surface } from '@/components/shared/surface'
import { ToneBadge } from '@/components/shared/tone-badge'
import { formatNumber } from '@/lib/format'
import { useSimulationSyncStore } from '@/store/simulation-sync-store'

interface ScenarioComparisonModalProps {
  isOpen: boolean
  onClose: () => void
}

export function ScenarioComparisonModal({
  isOpen,
  onClose,
}: ScenarioComparisonModalProps) {
  const { scenarios, deleteScenario } = useSimulationSyncStore()
  const [selectedMetric, setSelectedMetric] = useState<'energy' | 'cost' | 'carbon' | 'health'>('energy')

  if (!isOpen) return null

  // Transform scenarios into chart data
  const chartData = scenarios.map((s) => {
    const res = s.result
    return {
      name: s.name.length > 20 ? s.name.slice(0, 18) + '...' : s.name,
      fullName: s.name,
      energyKwh: res.predictedEnergyKwh,
      costInr: res.predictedCostInr,
      carbonKg: res.predictedCarbonKg,
      failureRisk: res.failureProbabilityPercent,
      efficiency: res.equipmentEfficiencyPercent,
      oee: res.oeePercent,
      health: res.machineHealthPercent,
      savingsInr: Math.max(0, res.baselineCostInr - res.predictedCostInr),
    }
  })

  // Colors for scenarios
  const barColors = ['var(--primary)', '#10b981', '#f59e0b', '#38bdf8', '#a855f7']

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="w-full max-w-5xl rounded-2xl border border-border bg-card p-6 shadow-2xl flex flex-col gap-6 my-8">
        {/* Header */}
        <div className="flex items-start justify-between border-b pb-4">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-tile flex items-center justify-center bg-primary/10 border border-primary/30 text-primary">
              <Layers className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold tracking-tight text-foreground">
                  Multi-Scenario Industrial Comparison
                </h2>
                <Badge variant="outline" className="text-xs font-mono">
                  {scenarios.length} Scenarios Loaded
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Contrast Energy, Cost, Carbon, Failure Risk, Equipment Efficiency, and OEE across operational permutations.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <X className="size-5" />
          </button>
        </div>

        {/* Metric Selector Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 bg-muted/20 p-2 rounded-xl border border-border/60">
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setSelectedMetric('energy')}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                selectedMetric === 'energy'
                  ? 'bg-primary text-primary-foreground font-semibold shadow-sm'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
              }`}
            >
              Energy & Cost
            </button>
            <button
              onClick={() => setSelectedMetric('cost')}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                selectedMetric === 'cost'
                  ? 'bg-primary text-primary-foreground font-semibold shadow-sm'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
              }`}
            >
              Carbon & Scope 2
            </button>
            <button
              onClick={() => setSelectedMetric('health')}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                selectedMetric === 'health'
                  ? 'bg-primary text-primary-foreground font-semibold shadow-sm'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
              }`}
            >
              Reliability, Efficiency & OEE
            </button>
          </div>

          <span className="text-xs text-muted-foreground">
            Synchronized with plant energy model
          </span>
        </div>

        {/* Comparative Chart */}
        <div className="rounded-xl border border-border/80 bg-background/50 p-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-3">
            {selectedMetric === 'energy' && 'Energy (kWh) & Tariff Cost (₹) Side-by-Side'}
            {selectedMetric === 'cost' && 'Carbon Emissions (kg CO₂e) & Daily Net Savings (₹)'}
            {selectedMetric === 'health' && 'Failure Risk (%), Efficiency (%), and OEE Index (%)'}
          </h4>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              {selectedMetric === 'energy' ? (
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.4} />
                  <XAxis dataKey="name" stroke="var(--muted-foreground)" fontSize={11} />
                  <YAxis stroke="var(--muted-foreground)" fontSize={11} unit=" kWh" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--card)',
                      borderColor: 'var(--border)',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Bar dataKey="energyKwh" name="Energy (kWh/day)" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="costInr" name="Electricity Cost (₹/day)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              ) : selectedMetric === 'cost' ? (
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.4} />
                  <XAxis dataKey="name" stroke="var(--muted-foreground)" fontSize={11} />
                  <YAxis stroke="var(--muted-foreground)" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--card)',
                      borderColor: 'var(--border)',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Bar dataKey="carbonKg" name="Carbon (kg CO₂e/day)" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="savingsInr" name="Daily Net Savings (₹)" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              ) : (
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.4} />
                  <XAxis dataKey="name" stroke="var(--muted-foreground)" fontSize={11} />
                  <YAxis stroke="var(--muted-foreground)" fontSize={11} unit="%" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--card)',
                      borderColor: 'var(--border)',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Bar dataKey="efficiency" name="Efficiency (%)" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="oee" name="OEE Index (%)" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="failureRisk" name="Failure Risk (%)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>

        {/* Detailed Scenario Matrix Table */}
        <div className="overflow-x-auto rounded-xl border border-border/80">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b bg-muted/40 text-muted-foreground font-semibold">
                <th className="p-3">Scenario</th>
                <th className="p-3">Machine</th>
                <th className="p-3 text-right">Energy (kWh)</th>
                <th className="p-3 text-right">Cost (₹/day)</th>
                <th className="p-3 text-right">Carbon (kg)</th>
                <th className="p-3 text-right">Failure Risk</th>
                <th className="p-3 text-right">Efficiency</th>
                <th className="p-3 text-right">OEE</th>
                <th className="p-3 text-right">Projected Savings</th>
                <th className="p-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {scenarios.map((scen, idx) => {
                const res = scen.result
                const savings = res.baselineCostInr - res.predictedCostInr

                return (
                  <tr key={scen.id} className="hover:bg-muted/20 transition-colors">
                    <td className="p-3 font-semibold text-foreground">
                      <div className="flex items-center gap-2">
                        <span
                          className="size-2.5 rounded-full shrink-0"
                          style={{ backgroundColor: barColors[idx % barColors.length] }}
                        />
                        <span>{scen.name}</span>
                      </div>
                    </td>
                    <td className="p-3 font-mono text-muted-foreground">{res.machineCode}</td>
                    <td className="p-3 text-right font-mono font-bold text-foreground">
                      {formatNumber(res.predictedEnergyKwh, 1)}
                    </td>
                    <td className="p-3 text-right font-mono text-foreground">
                      ₹{res.predictedCostInr.toLocaleString()}
                    </td>
                    <td className="p-3 text-right font-mono text-foreground">
                      {formatNumber(res.predictedCarbonKg, 1)}
                    </td>
                    <td className="p-3 text-right font-mono font-bold">
                      <span className={res.failureProbabilityPercent > 20 ? 'text-rose-400' : 'text-emerald-400'}>
                        {res.failureProbabilityPercent}%
                      </span>
                    </td>
                    <td className="p-3 text-right font-mono text-foreground">
                      {res.equipmentEfficiencyPercent}%
                    </td>
                    <td className="p-3 text-right font-mono text-foreground font-semibold">
                      {res.oeePercent}%
                    </td>
                    <td className="p-3 text-right font-mono font-bold">
                      <span className={savings >= 0 ? 'text-emerald-400' : 'text-amber-400'}>
                        {savings >= 0 ? `+₹${savings.toLocaleString()}` : `-₹${Math.abs(savings).toLocaleString()}`}
                      </span>
                    </td>
                    <td className="p-3 text-center">
                      {scenarios.length > 1 && (
                        <button
                          onClick={() => {
                            deleteScenario(scen.id)
                            toast.info(`Deleted "${scen.name}"`)
                          }}
                          className="p-1 text-muted-foreground hover:text-destructive transition-colors rounded"
                          title="Delete scenario"
                        >
                          <Trash2 className="size-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t pt-4">
          <div className="text-xs text-muted-foreground">
            Scenarios reflect real-time physical equations and multi-target XGBoost inferences.
          </div>
          <Button size="sm" onClick={onClose}>
            Done
          </Button>
        </div>
      </div>
    </div>
  )
}
