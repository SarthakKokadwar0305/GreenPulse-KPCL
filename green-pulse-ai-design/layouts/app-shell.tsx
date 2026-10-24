'use client'

import { useEffect, useState, type ReactNode } from 'react'
import { usePathname } from 'next/navigation'

import { AppFooter } from '@/components/layout/app-footer'
import { Navbar } from '@/components/layout/navbar/navbar'
import { Sidebar } from '@/components/layout/sidebar/sidebar'
import { AccessDeniedView } from '@/components/shared/access-denied'
import { CopilotFloatingWidget } from '@/components/shared/copilot-floating-widget'
import { useAuthStore } from '@/store/auth-store'

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  const canAccessRoute = useAuthStore((state) => state.canAccessRoute)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const isAllowed = mounted ? canAccessRoute(pathname) : true

  return (
    <div className="flex min-h-dvh bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />
        <main
          id="main-content"
          className="mx-auto w-full max-w-[1600px] flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8"
        >
          {isAllowed ? children : <AccessDeniedView modulePath={pathname} />}
        </main>
        <AppFooter />
        {mounted && pathname !== '/copilot' && <CopilotFloatingWidget />}
      </div>
    </div>
  )
}
