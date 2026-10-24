'use client'

import { usePathname } from 'next/navigation'
import { Fragment } from 'react'

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { getBreadcrumb } from '@/config/navigation'

export function NavbarBreadcrumb() {
  const pathname = usePathname()
  const segments = getBreadcrumb(pathname)

  return (
    <Breadcrumb>
      <BreadcrumbList className="gap-1.5 text-xs sm:gap-1.5">
        {segments.map((segment, index) => {
          const isLast = index === segments.length - 1

          return (
            <Fragment key={segment}>
              <BreadcrumbItem>
                {isLast ? (
                  <BreadcrumbPage className="font-semibold">{segment}</BreadcrumbPage>
                ) : (
                  <span className="text-muted-foreground">{segment}</span>
                )}
              </BreadcrumbItem>
              {!isLast && <BreadcrumbSeparator />}
            </Fragment>
          )
        })}
      </BreadcrumbList>
    </Breadcrumb>
  )
}
