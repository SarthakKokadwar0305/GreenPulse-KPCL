'use client'

import { useEffect, useState } from 'react'
import { LogOut, Settings, UserRound, Shield, Check } from 'lucide-react'
import { toast } from 'sonner'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Skeleton } from '@/components/ui/skeleton'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useAuthStore, EnterpriseRole } from '@/store/auth-store'

const ROLE_OPTIONS: { code: EnterpriseRole; label: string; desc: string }[] = [
  {
    code: 'PLANT_HEAD',
    label: 'Plant Head (Full Oversight)',
    desc: 'All 9 machines, users, audit, simulations',
  },
  {
    code: 'ENERGY_MANAGER',
    label: 'Energy Manager',
    desc: 'Energy, carbon, forecast, simulator, ECMs',
  },
  {
    code: 'MAINTENANCE_MANAGER',
    label: 'Maintenance Manager',
    desc: 'Digital twin, machine health, anomalies',
  },
  {
    code: 'OPERATOR',
    label: 'Lead Operator',
    desc: 'Assigned machines (COMP-01, CNC-01) only',
  },
]

export function ProfileMenu() {
  const user = useAuthStore((state) => state.user)
  const switchRole = useAuthStore((state) => state.switchRole)
  const logout = useAuthStore((state) => state.logout)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <Skeleton className="size-10 rounded-full" />
  }

  const handleRoleChange = (role: EnterpriseRole, label: string) => {
    switchRole(role)
    toast.success(`Role switched to ${label}`, {
      description: 'Sidebar and feature authorization updated dynamically.',
    })
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        aria-label="Open profile menu"
        className="rounded-full outline-none focus-visible:ring-3 focus-visible:ring-ring/40"
      >
        <Avatar className="size-10 border border-primary/30">
          <AvatarFallback className="bg-primary text-sm font-semibold text-primary-foreground">
            {user.initials}
          </AvatarFallback>
        </Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-72">
        <DropdownMenuGroup>
          <DropdownMenuLabel className="flex flex-col gap-0.5 py-2">
            <span className="text-sm font-semibold text-foreground">
              {user.name}
            </span>
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-primary">
              <Shield className="size-3" />
              {user.roleTitle}
            </span>
            <span className="text-xs font-normal text-muted-foreground truncate">
              {user.email}
            </span>
            {user.role === 'OPERATOR' && (
              <span className="mt-1 rounded bg-secondary/80 px-1.5 py-0.5 text-[10px] text-secondary-foreground font-mono">
                Assigned: {user.assignedMachines.join(', ')}
              </span>
            )}
          </DropdownMenuLabel>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuSub>
            <DropdownMenuSubTrigger>
              <Shield className="size-4" />
              <span>Switch Role (RBAC Demo)</span>
            </DropdownMenuSubTrigger>
            <DropdownMenuSubContent className="w-64">
              {ROLE_OPTIONS.map((opt) => (
                <DropdownMenuItem
                  key={opt.code}
                  onClick={() => handleRoleChange(opt.code, opt.label)}
                  className="flex items-center justify-between"
                >
                  <div className="flex flex-col">
                    <span className="text-xs font-medium">{opt.label}</span>
                    <span className="text-[10px] text-muted-foreground">{opt.desc}</span>
                  </div>
                  {user.role === opt.code && (
                    <Check className="size-4 text-primary shrink-0" />
                  )}
                </DropdownMenuItem>
              ))}
            </DropdownMenuSubContent>
          </DropdownMenuSub>
          <DropdownMenuItem onClick={() => toast.info(`Viewing profile for ${user.name}`)}>
            <UserRound aria-hidden="true" />
            Profile & Permissions
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => toast.info('System settings')}>
            <Settings aria-hidden="true" />
            Security Settings
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem
            variant="destructive"
            onClick={() => {
              logout()
              toast.info('Signed out of GreenPulse AI')
            }}
          >
            <LogOut aria-hidden="true" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
