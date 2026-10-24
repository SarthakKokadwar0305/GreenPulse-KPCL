import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

interface SectionHeaderProps {
  title: string
  description?: string
  icon?: LucideIcon
  action?: ReactNode
  className?: string
}

export function SectionHeader({
  title,
  description,
  icon: Icon,
  action,
  className,
}: SectionHeaderProps) {
  return (
    <div
      className={cn(
        'flex flex-wrap items-start justify-between gap-x-4 gap-y-3',
        className,
      )}
    >
      <div className="flex min-w-0 items-start gap-2.5">
        {Icon && (
          <Icon
            className="mt-0.5 size-4.5 shrink-0 text-primary"
            aria-hidden="true"
          />
        )}
        <div className="min-w-0">
          <h2 className="text-base leading-6 font-semibold tracking-tight text-foreground">
            {title}
          </h2>
          {description && (
            <p className="mt-0.5 text-[13px] text-muted-foreground">
              {description}
            </p>
          )}
        </div>
      </div>
      {action && <div className="flex shrink-0 items-center gap-2">{action}</div>}
    </div>
  )
}
