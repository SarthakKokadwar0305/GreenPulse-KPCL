import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

import { SectionHeader } from './section-header'
import { Surface } from './surface'

interface ChartContainerProps {
  title: string
  description?: string
  icon?: LucideIcon
  action?: ReactNode
  footer?: ReactNode
  children: ReactNode
  className?: string
}

export function ChartPanel({
  title,
  description,
  icon,
  action,
  footer,
  children,
  className,
}: ChartContainerProps) {
  return (
    <Surface className={cn('flex h-full flex-col gap-5 p-5', className)}>
      <SectionHeader
        title={title}
        description={description}
        icon={icon}
        action={action}
      />
      <div className="min-h-0 flex-1">{children}</div>
      {footer && <div className="border-t pt-4">{footer}</div>}
    </Surface>
  )
}
