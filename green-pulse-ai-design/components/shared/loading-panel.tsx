import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

import { Surface } from './surface'

interface LoadingPanelProps {
  className?: string
}

export function LoadingPanel({ className }: LoadingPanelProps) {
  return (
    <Surface
      className={cn('flex h-full min-h-40 flex-col gap-4 p-5', className)}
      aria-busy="true"
    >
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-8 w-1/2" />
      <Skeleton className="mt-auto h-12 w-full" />
    </Surface>
  )
}
