'use client'

import { ShieldAlert, ArrowLeft, RefreshCw } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/auth-store'

interface AccessDeniedProps {
  modulePath: string
}

export function AccessDeniedView({ modulePath }: AccessDeniedProps) {
  const user = useAuthStore((state) => state.user)
  const switchRole = useAuthStore((state) => state.switchRole)

  return (
    <div className="flex min-h-[500px] flex-col items-center justify-center rounded-xl border border-dashed border-destructive/40 bg-destructive/5 p-8 text-center animate-in fade-in-50">
      <div className="flex size-16 items-center justify-center rounded-full bg-destructive/10 text-destructive mb-4">
        <ShieldAlert className="size-8" />
      </div>
      <h2 className="text-2xl font-bold tracking-tight text-foreground">
        Access Denied (403 Forbidden)
      </h2>
      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        Your current enterprise role <span className="font-semibold text-foreground">[{user.roleTitle}]</span> is not authorized to access module <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">{modulePath}</span>.
      </p>

      {user.role === 'OPERATOR' && (
        <div className="mt-4 rounded-md bg-background/80 p-3 text-xs text-muted-foreground border">
          <p className="font-medium text-foreground">Operator Clearance Restriction:</p>
          <p className="mt-1">
            Operators are restricted to assigned machinery (<span className="font-mono font-semibold">{user.assignedMachines.join(', ')}</span>), Live Machine Telemetry, and Current Alarms.
          </p>
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
        <Link href="/">
          <Button variant="default">
            <ArrowLeft className="size-4" />
            Return to Dashboard
          </Button>
        </Link>
        <Button
          variant="outline"
          onClick={() => switchRole('PLANT_HEAD')}
          className="border-primary/40 text-primary hover:bg-primary/10"
        >
          <RefreshCw className="size-4" />
          Switch to Plant Head (Demo Mode)
        </Button>
      </div>
    </div>
  )
}
