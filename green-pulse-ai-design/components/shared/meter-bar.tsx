'use client'

import { motion } from 'framer-motion'

import { TONE_STYLES } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { Tone } from '@/types'

interface MeterBarProps {
  value: number
  label: string
  tone?: Tone
  className?: string
}

export function MeterBar({
  value,
  label,
  tone = 'info',
  className,
}: MeterBarProps) {
  const clamped = Math.min(100, Math.max(0, value))

  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={clamped}
      className={cn(
        'h-1.5 w-full overflow-hidden rounded-full bg-muted',
        className,
      )}
    >
      <motion.div
        className={cn('h-full rounded-full', TONE_STYLES[tone].bar)}
        initial={{ width: 0 }}
        animate={{ width: `${clamped}%` }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      />
    </div>
  )
}
