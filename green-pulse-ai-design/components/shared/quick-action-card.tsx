import { ArrowUpRight } from 'lucide-react'

import { resolveIcon } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type { QuickActionItem } from '@/types'

import { IconTile } from './icon-tile'
import { ModuleLink } from './module-link'

interface QuickActionCardProps {
  action: QuickActionItem
}

export function QuickActionCard({ action }: QuickActionCardProps) {
  const Icon = resolveIcon(action.iconKey)

  return (
    <ModuleLink
      href={action.href}
      className={cn(
        'group flex h-full w-full flex-col gap-4 rounded-card border bg-card p-4 text-left shadow-card outline-none',
        'transition-[box-shadow,transform,border-color] duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-card-hover',
        'focus-visible:ring-3 focus-visible:ring-ring/40',
      )}
    >
      <span className="flex items-start justify-between">
        <IconTile icon={Icon} tone="info" />
        <ArrowUpRight
          className="size-4 text-muted-foreground transition-[transform,color] duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-primary"
          aria-hidden="true"
        />
      </span>
      <span className="flex flex-col gap-1">
        <span className="text-sm font-semibold text-foreground">
          {action.title}
        </span>
        <span className="text-xs leading-relaxed text-muted-foreground">
          {action.description}
        </span>
      </span>
    </ModuleLink>
  )
}
