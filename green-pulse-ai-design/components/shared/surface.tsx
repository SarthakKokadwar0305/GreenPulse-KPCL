import type { ComponentProps } from 'react'

import { cn } from '@/lib/utils'

interface SurfaceProps extends ComponentProps<'div'> {
  interactive?: boolean
}

export function Surface({ interactive, className, ...props }: SurfaceProps) {
  return (
    <div
      data-slot="surface"
      className={cn(
        'rounded-card border bg-card text-card-foreground shadow-card',
        interactive &&
          'transition-[box-shadow,transform,border-color] duration-200 hover:border-primary/25 hover:shadow-card-hover',
        className,
      )}
      {...props}
    />
  )
}
