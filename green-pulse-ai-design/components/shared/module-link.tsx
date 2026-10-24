'use client'

import Link from 'next/link'
import type { ComponentProps } from 'react'
import { toast } from 'sonner'

import { getNavItemByPath } from '@/config/navigation'
import { isRouteEnabled } from '@/config/routes'

interface ModuleLinkProps extends Omit<ComponentProps<'a'>, 'href'> {
  href: string
}

export function ModuleLink({
  href,
  children,
  onClick,
  ...props
}: ModuleLinkProps) {
  if (isRouteEnabled(href)) {
    return (
      <Link href={href} onClick={onClick} {...props}>
        {children}
      </Link>
    )
  }

  const moduleName = getNavItemByPath(href)?.label ?? 'This module'

  return (
    <button
      type="button"
      className={props.className}
      aria-label={props['aria-label']}
      onClick={() =>
        toast.info(`${moduleName} is coming soon`, {
          description:
            'This module is scheduled for an upcoming release of GreenPulse AI.',
        })
      }
    >
      {children}
    </button>
  )
}
