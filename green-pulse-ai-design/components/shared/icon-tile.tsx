import type { LucideIcon } from 'lucide-react'

import { TONE_STYLES } from '@/lib/tone'
import { cn } from '@/lib/utils'
import type { Tone } from '@/types'

type IconTileSize = 'sm' | 'md' | 'lg'

const SIZE_CLASSES: Record<IconTileSize, string> = {
  sm: 'size-7 rounded-lg [&_svg]:size-3.5',
  md: 'size-10 rounded-tile [&_svg]:size-5',
  lg: 'size-12 rounded-tile [&_svg]:size-6',
}

interface IconTileProps {
  icon: LucideIcon
  tone?: Tone
  size?: IconTileSize
  className?: string
}

export function IconTile({
  icon: Icon,
  tone = 'info',
  size = 'md',
  className,
}: IconTileProps) {
  const styles = TONE_STYLES[tone]

  return (
    <span
      aria-hidden="true"
      className={cn(
        'flex shrink-0 items-center justify-center',
        styles.soft,
        styles.text,
        SIZE_CLASSES[size],
        className,
      )}
    >
      <Icon />
    </span>
  )
}
