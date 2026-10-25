'use client'

import {
  Clock,
  Cpu,
  History,
  RotateCcw,
  Sparkles,
  User,
  Zap,
} from 'lucide-react'
import { useEffect } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Surface } from '@/components/shared/surface'
import { useSimulationSyncStore } from '@/store/simulation-sync-store'

interface SimulationTimelineProps {
  isOpen: boolean
  onClose: () => void
}

export function SimulationTimeline({ isOpen, onClose }: SimulationTimelineProps) {
  const { timeline, loadTimeline } = useSimulationSyncStore()

  useEffect(() => {
    if (isOpen) {
      loadTimeline()
    }
  }, [isOpen, loadTimeline])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="w-full max-w-4xl rounded-2xl border border-border bg-card p-6 shadow-2xl flex flex-col gap-6 my-8 max-h-[85vh]">
        {/* Header */}
        <div className="flex items-start justify-between border-b pb-4">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-tile flex items-center justify-center bg-primary/10 border border-primary/30 text-primary">
              <History className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold tracking-tight text-foreground">
                  Digital Twin Simulation Audit Timeline
                </h2>
                <Badge variant="outline" className="text-xs font-mono">
                  {timeline.length} Events Logged
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Chronological ledger of parameter permutations, operational counterfactuals, and predicted outcomes.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Timeline Content Stream */}
        <div className="overflow-y-auto flex flex-col gap-3 pr-2">
          {timeline.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              No simulation timeline events recorded yet. Adjust machine parameters in the Digital Twin Control Panel to log runs.
            </div>
          ) : (
            timeline.map((item, idx) => (
              <div
                key={item.id || idx}
                className="relative rounded-xl border border-border/80 bg-background/50 p-4 transition-all hover:border-primary/50"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/40 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="size-2 rounded-full bg-primary" />
                    <span className="font-bold text-foreground text-sm">{item.machineName}</span>
                    <Badge variant="outline" className="font-mono text-[10px]">
                      {item.machineId}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1 font-mono">
                      <Clock className="size-3" /> {item.timestamp}
                    </span>
                    <span className="flex items-center gap-1 text-foreground font-medium">
                      <User className="size-3 text-primary" /> {item.user}
                    </span>
                  </div>
                </div>

                <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  {/* Changed Levers */}
                  <div className="rounded-lg bg-card/60 p-2.5 border border-border/50">
                    <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                      Adjusted Parameters
                    </span>
                    <ul className="mt-1.5 space-y-1">
                      {item.changedParameters.map((param, pIdx) => (
                        <li key={pIdx} className="font-mono font-medium text-primary">
                          • {param}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Previous Values */}
                  <div className="rounded-lg bg-card/60 p-2.5 border border-border/50">
                    <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                      Previous Values
                    </span>
                    <div className="mt-1.5 space-y-1 font-mono text-muted-foreground">
                      {Object.entries(item.previousValues).map(([k, v]) => (
                        <div key={k} className="flex justify-between">
                          <span>{k}:</span>
                          <span className="text-foreground">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Predicted Values */}
                  <div className="rounded-lg bg-emerald-500/5 p-2.5 border border-emerald-500/30">
                    <span className="text-[11px] font-semibold text-emerald-500 uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="size-3" /> Predicted Impact
                    </span>
                    <div className="mt-1.5 space-y-1 font-mono">
                      {Object.entries(item.predictedValues).map(([k, v]) => (
                        <div key={k} className="flex justify-between">
                          <span className="text-muted-foreground">{k}:</span>
                          <span className="font-bold text-emerald-400">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t pt-4">
          <span className="text-xs text-muted-foreground">
            Audit logs conform to ISO 50001 energy baseline change tracking requirements.
          </span>
          <Button size="sm" onClick={onClose}>
            Close Timeline
          </Button>
        </div>
      </div>
    </div>
  )
}
