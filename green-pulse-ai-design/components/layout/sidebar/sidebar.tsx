'use client'

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetTitle,
} from '@/components/ui/sheet'
import { cn } from '@/lib/utils'
import { useUiStore } from '@/store/ui-store'

import { SidebarContent } from './sidebar-content'

export function Sidebar() {
  const collapsed = useUiStore((state) => state.sidebarCollapsed)
  const toggleSidebar = useUiStore((state) => state.toggleSidebar)
  const mobileNavOpen = useUiStore((state) => state.mobileNavOpen)
  const setMobileNavOpen = useUiStore((state) => state.setMobileNavOpen)

  return (
    <>
      <aside
        className={cn(
          'sticky top-0 hidden h-dvh shrink-0 border-r border-sidebar-border lg:block',
          'transition-[width] duration-300 ease-out',
          collapsed ? 'w-[76px]' : 'w-[264px]',
        )}
      >
        <SidebarContent collapsed={collapsed} onToggleCollapse={toggleSidebar} />
      </aside>

      <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
        <SheetContent
          side="left"
          showCloseButton={false}
          className="w-[280px] gap-0 p-0 data-[side=left]:max-w-[280px]"
        >
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <SheetDescription className="sr-only">
            Browse GreenPulse AI modules
          </SheetDescription>
          <SidebarContent onNavigate={() => setMobileNavOpen(false)} />
        </SheetContent>
      </Sheet>
    </>
  )
}
