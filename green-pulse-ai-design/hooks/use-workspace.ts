'use client'

import { useQuery } from '@tanstack/react-query'

import { getWorkspace } from '@/services/plant-service'
import { useUiStore } from '@/store/ui-store'

export function useWorkspace() {
  return useQuery({
    queryKey: ['workspace'],
    queryFn: getWorkspace,
    staleTime: Infinity,
  })
}

export function useSelectedPlant() {
  const { data: workspace } = useWorkspace()
  const selectedPlantId = useUiStore((state) => state.selectedPlantId)

  if (!workspace) return undefined

  const activeId = selectedPlantId ?? workspace.defaultPlantId
  return (
    workspace.plants.find((plant) => plant.id === activeId) ??
    workspace.plants.find((plant) => plant.id === workspace.defaultPlantId)
  )
}
