'use client'

import {
  BrainCircuit,
  CheckCircle2,
  Info,
  Lightbulb,
  ShieldAlert,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Zap,
} from 'lucide-react'

import { Surface } from '@/components/shared/surface'
import type { MachineSimulationResult } from '@/types/digital-twin'

interface AiExplanationsPanelProps {
  result: MachineSimulationResult
}

export function AiExplanationsPanel({ result }: AiExplanationsPanelProps) {
  return (
    <div className="flex flex-col gap-4">
      {/* Dynamic AI Explanations */}
      <Surface className="flex flex-col gap-3 p-4 border border-border/80 bg-card/60">
        <div className="flex items-center gap-2 text-foreground font-semibold text-xs uppercase tracking-wider">
          <BrainCircuit className="size-4 text-primary" />
          <span>AI Prediction Causal Explanations</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {result.explanations.map((exp, idx) => (
            <div
              key={idx}
              className="flex items-start gap-2.5 rounded-lg border border-border/50 bg-background/50 p-3 text-xs leading-relaxed"
            >
              <Info className="size-4 text-primary shrink-0 mt-0.5" />
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{exp.split(':')[0]}:</span>{' '}
                {exp.split(':').slice(1).join(':') || exp}
              </p>
            </div>
          ))}
        </div>
      </Surface>

      {/* Prescriptive Actionable Insights */}
      <Surface className="flex flex-col gap-3 p-4 border border-emerald-500/30 bg-emerald-500/5 dark:bg-emerald-950/15">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-semibold text-xs uppercase tracking-wider">
            <Lightbulb className="size-4 text-emerald-500" />
            <span>Prescriptive AI Recommendations & ROI Actions</span>
          </div>
          <span className="text-[11px] font-mono text-emerald-600 dark:text-emerald-400">
            Real-Time Synthesis
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {result.prescriptiveInsights.map((insight, idx) => (
            <div
              key={idx}
              className="flex items-start gap-2.5 rounded-lg border border-emerald-500/20 bg-background/60 p-3 text-xs leading-relaxed text-foreground"
            >
              <Sparkles className="size-4 text-emerald-500 shrink-0 mt-0.5" />
              <p className="text-muted-foreground">
                <span className="font-semibold text-foreground">Action {idx + 1}: </span>
                {insight}
              </p>
            </div>
          ))}
        </div>
      </Surface>
    </div>
  )
}
