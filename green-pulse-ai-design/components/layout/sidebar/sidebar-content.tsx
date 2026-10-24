'use client'

import { useEffect, useState } from 'react'
import { ChevronsLeft, ChevronsRight, ShieldCheck } from 'lucide-react'
import { usePathname } from 'next/navigation'

import { BrandMark } from '@/components/shared/brand-mark'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { NAV_ITEMS } from '@/config/navigation'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/store/auth-store'

import { SidebarNavItem } from './sidebar-nav-item'

const UTILITY_ITEM_IDS = new Set(['reports', 'settings'])
const PRIMARY_ITEMS = NAV_ITEMS.filter((item) => !UTILITY_ITEM_IDS.has(item.id))
const UTILITY_ITEMS = NAV_ITEMS.filter((item) => UTILITY_ITEM_IDS.has(item.id))

interface SidebarContentProps {
  collapsed?: boolean
  onToggleCollapse?: () => void
  onNavigate?: () => void
}

export function SidebarContent({
  collapsed = false,
  onToggleCollapse,
  onNavigate,
}: SidebarContentProps) {
  const pathname = usePathname()
  const user = useAuthStore((state) => state.user)
  const canAccessRoute = useAuthStore((state) => state.canAccessRoute)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Dynamic RBAC filtering based on current user role
  const filteredPrimary = mounted
    ? PRIMARY_ITEMS.filter((item) => canAccessRoute(item.href))
    : PRIMARY_ITEMS
  const filteredUtility = mounted
    ? UTILITY_ITEMS.filter((item) => canAccessRoute(item.href))
    : UTILITY_ITEMS

  const renderItems = (items: typeof NAV_ITEMS) =>
    items.map((item) => (
      <li key={item.id}>
        <SidebarNavItem
          item={item}
          active={pathname === item.href}
          collapsed={collapsed}
          onNavigate={onNavigate}
        />
      </li>
    ))

  return (
    <div className="flex h-full flex-col bg-sidebar text-sidebar-foreground">
      <div
        className={cn(
          'flex h-[72px] shrink-0 items-center border-b border-sidebar-border px-5',
          collapsed && 'justify-center px-0',
        )}
      >
        <BrandMark collapsed={collapsed} />
      </div>

      {mounted && !collapsed && (
        <div className="mx-3 mt-3 flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/5 px-3 py-2 text-xs">
          <ShieldCheck className="size-4 shrink-0 text-primary" />
          <div className="min-w-0 flex-1 truncate">
            <p className="font-semibold text-foreground truncate">{user.roleTitle}</p>
            <p className="text-[10px] text-muted-foreground truncate">{user.department}</p>
          </div>
        </div>
      )}

      <nav
        aria-label="Primary"
        className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-3 py-4"
      >
        <div className="flex flex-col gap-1">
          {!collapsed && (
            <p className="px-3 pb-1 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
              Platform Modules
            </p>
          )}
          <ul className="flex flex-col gap-0.5">{renderItems(filteredPrimary)}</ul>
        </div>

        {filteredUtility.length > 0 && (
          <div className="mt-auto flex flex-col gap-3">
            <Separator />
            <ul className="flex flex-col gap-0.5">{renderItems(filteredUtility)}</ul>
          </div>
        )}
      </nav>

      {onToggleCollapse && (
        <div className="shrink-0 border-t border-sidebar-border p-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleCollapse}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className={cn(
              'h-9 w-full text-muted-foreground',
              collapsed ? 'justify-center' : 'justify-start px-3',
            )}
          >
            {collapsed ? (
              <ChevronsRight aria-hidden="true" />
            ) : (
              <>
                <ChevronsLeft data-icon="inline-start" aria-hidden="true" />
                Collapse
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  )
}
