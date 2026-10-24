import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

interface PageHeaderProps {
  eyebrow?: ReactNode
  title: ReactNode
  description?: string
  meta?: ReactNode
  actions?: ReactNode
  className?: string
}

export function PageHeader({
  eyebrow,
  title,
  description,
  meta,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <header
      className={cn(
        'flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between',
        className,
      )}
    >
      <div className="flex min-w-0 flex-col gap-1.5">
        {eyebrow && (
          <div className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            {eyebrow}
          </div>
        )}
        <h1 className="text-2xl font-semibold tracking-tight text-balance text-foreground sm:text-[28px] sm:leading-9">
          {title}
        </h1>
        {description && (
          <p className="max-w-2xl text-sm text-muted-foreground">
            {description}
          </p>
        )}
        {meta && <div className="mt-1 flex flex-wrap items-center gap-2">{meta}</div>}
      </div>
      {actions && (
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          {actions}
        </div>
      )}
    </header>
  )
}
