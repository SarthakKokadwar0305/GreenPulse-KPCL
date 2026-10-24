import type { ReactNode } from 'react'

import { Badge } from '@/components/ui/badge'
import { TONE_STYLES } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { Tone } from '@/types'

import { StatusDot } from './status-dot'

interface ToneBadgeProps {
  tone: Tone
  children: ReactNode
  withDot?: boolean
  pulse?: boolean
  className?: string
}

export function ToneBadge({
  tone,
  children,
  withDot = true,
  pulse = false,
  className,
}: ToneBadgeProps) {
  const styles = TONE_STYLES[tone]

  return (
    <Badge
      variant="outline"
      className={cn(
        'h-6 gap-1.5 border-transparent px-2.5 font-medium',
        styles.soft,
        styles.text,
        className,
      )}
    >
      {withDot && <StatusDot tone={tone} pulse={pulse} />}
      {children}
    </Badge>
  )
}
