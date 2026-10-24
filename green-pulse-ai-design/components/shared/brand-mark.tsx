import { Activity } from 'lucide-react'

import { cn } from '@/lib/utils'

interface BrandMarkProps {
  collapsed?: boolean
  className?: string
}

export function BrandMark({ collapsed = false, className }: BrandMarkProps) {
  return (
    <div className={cn('flex items-center gap-3', className)}>
      <span
        aria-hidden="true"
        className="flex size-10 shrink-0 items-center justify-center rounded-tile bg-linear-to-br from-primary to-[#0d47a1] text-primary-foreground shadow-card"
      >
        <Activity className="size-5" strokeWidth={2.25} />
      </span>
      {!collapsed && (
        <div className="flex min-w-0 flex-col">
          <span className="truncate text-[17px] leading-5 font-bold tracking-tight text-foreground">
            GreenPulse AI
          </span>
          <span className="truncate text-[11px] leading-4 font-medium text-muted-foreground">
            Energy Intelligence Platform
          </span>
        </div>
      )}
    </div>
  )
}
