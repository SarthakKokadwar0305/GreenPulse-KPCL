'use client'

import { ModuleLink } from '@/components/shared/module-link'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import type { NavItem } from '@/types'

interface SidebarNavItemProps {
  item: NavItem
  active: boolean
  collapsed: boolean
  onNavigate?: () => void
}

export function SidebarNavItem({
  item,
  active,
  collapsed,
  onNavigate,
}: SidebarNavItemProps) {
  const Icon = item.icon

  const link = (
    <ModuleLink
      href={item.href}
      aria-label={item.label}
      aria-current={active ? 'page' : undefined}
      onClick={onNavigate}
      className={cn(
        'group relative flex h-10 w-full items-center gap-3 rounded-lg px-3 text-sm font-medium outline-none',
        'transition-colors duration-150 focus-visible:ring-3 focus-visible:ring-sidebar-ring/40',
        collapsed && 'justify-center px-0',
        active
          ? 'bg-sidebar-accent text-sidebar-accent-foreground'
          : 'text-sidebar-foreground/75 hover:bg-sidebar-accent/60 hover:text-sidebar-foreground',
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          'absolute top-1/2 left-0 h-6 w-[3px] -translate-y-1/2 rounded-r-full bg-sidebar-primary transition-opacity duration-150',
          active ? 'opacity-100' : 'opacity-0',
        )}
      />
      <Icon
        className={cn(
          'size-[18px] shrink-0 transition-colors',
          active
            ? 'text-sidebar-primary'
            : 'text-sidebar-foreground/60 group-hover:text-sidebar-foreground',
        )}
        aria-hidden="true"
      />
      {!collapsed && (
        <>
          <span className="flex-1 truncate text-left">{item.label}</span>
          {!item.enabled && (
            <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-semibold tracking-wide text-muted-foreground uppercase">
              Soon
            </span>
          )}
        </>
      )}
    </ModuleLink>
  )

  if (!collapsed) return link

  return (
    <Tooltip>
      <TooltipTrigger render={<div className="w-full" />}>{link}</TooltipTrigger>
      <TooltipContent side="right" sideOffset={10}>
        {item.label}
      </TooltipContent>
    </Tooltip>
  )
}
