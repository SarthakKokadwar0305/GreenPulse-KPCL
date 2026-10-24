'use client'

import { Menu } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useUiStore } from '@/store/ui-store'

import { ConnectionStatus } from './connection-status'
import { GlobalSearch } from './global-search'
import { NavbarBreadcrumb } from './navbar-breadcrumb'
import { NavbarClock } from './navbar-clock'
import { NotificationMenu } from './notification-menu'
import { PlantSelector } from './plant-selector'
import { ProfileMenu } from './profile-menu'
import { ThemeToggle } from './theme-toggle'

export function Navbar() {
  const setMobileNavOpen = useUiStore((state) => state.setMobileNavOpen)

  return (
    <header className="sticky top-0 z-30 border-b bg-background/85 backdrop-blur-md">
      <div className="flex h-[72px] items-center gap-3 px-4 sm:px-6 lg:px-8">
        <Button
          variant="ghost"
          size="icon"
          className="size-10 rounded-tile lg:hidden"
          aria-label="Open navigation"
          onClick={() => setMobileNavOpen(true)}
        >
          <Menu aria-hidden="true" />
        </Button>

        <div className="flex min-w-0 flex-1 flex-col justify-center gap-1.5">
          <NavbarBreadcrumb />
          <div className="flex items-center gap-3">
            <PlantSelector />
            <div className="hidden min-w-0 flex-1 md:block">
              <GlobalSearch />
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 sm:gap-2">
          <div className="hidden xl:block">
            <NavbarClock />
          </div>
          <Separator orientation="vertical" className="mx-2 hidden h-6 xl:block" />
          <div className="hidden sm:block">
            <ConnectionStatus />
          </div>
          <NotificationMenu />
          <ThemeToggle />
          <ProfileMenu />
        </div>
      </div>
    </header>
  )
}
