'use client'

import { ChevronsUpDown, Factory } from 'lucide-react'

import { Skeleton } from '@/components/ui/skeleton'
import { buttonVariants } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useSelectedPlant, useWorkspace } from '@/hooks/use-workspace'
import { cn } from '@/lib/utils'
import { useUiStore } from '@/store/ui-store'

export function PlantSelector() {
  const { data: workspace } = useWorkspace()
  const selectedPlant = useSelectedPlant()
  const selectPlant = useUiStore((state) => state.selectPlant)

  if (!workspace || !selectedPlant) {
    return <Skeleton className="h-10 w-44 rounded-tile" />
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        aria-label="Select plant"
        className={cn(
          buttonVariants({ variant: 'outline' }),
          'h-10 max-w-[220px] gap-2.5 rounded-tile bg-card px-3',
        )}
      >
        <span className="flex size-6 shrink-0 items-center justify-center rounded-md bg-accent text-accent-foreground">
          <Factory className="size-3.5" aria-hidden="true" />
        </span>
        <span className="hidden min-w-0 flex-col items-start text-left sm:flex">
          <span className="w-full truncate text-[13px] leading-4 font-semibold">
            {selectedPlant.name}
          </span>
          <span className="w-full truncate text-[11px] leading-3.5 font-normal text-muted-foreground">
            {selectedPlant.location}
          </span>
        </span>
        <ChevronsUpDown
          className="size-3.5 shrink-0 text-muted-foreground"
          aria-hidden="true"
        />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-64">
        <DropdownMenuGroup>
          <DropdownMenuLabel>Current plant</DropdownMenuLabel>
          <DropdownMenuRadioGroup
            value={selectedPlant.id}
            onValueChange={(plantId) => selectPlant(plantId)}
          >
            {workspace.plants.map((plant) => (
              <DropdownMenuRadioItem key={plant.id} value={plant.id}>
                <span className="flex flex-col">
                  <span className="text-[13px] font-medium">{plant.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {plant.location}
                  </span>
                </span>
              </DropdownMenuRadioItem>
            ))}
          </DropdownMenuRadioGroup>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
