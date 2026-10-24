import { TONE_STYLES } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { Tone } from '@/types'

interface StatusDotProps {
  tone: Tone
  pulse?: boolean
  className?: string
}

export function StatusDot({ tone, pulse = false, className }: StatusDotProps) {
  const { dot } = TONE_STYLES[tone]

  return (
    <span
      aria-hidden="true"
      className={cn('relative flex size-2 shrink-0', className)}
    >
      {pulse && (
        <span
          className={cn(
            'absolute inset-0 rounded-full animate-status-pulse',
            dot,
          )}
        />
      )}
      <span className={cn('relative size-2 rounded-full', dot)} />
    </span>
  )
}
