'use client'

import { useQuery } from '@tanstack/react-query'

import { useSelectedPlant } from './use-workspace'

interface PlantQueryOptions<TData, TSelected> {
  resource: string
  fetcher: (plantId: string) => Promise<TData>
  select?: (data: TData) => TSelected
  refetchInterval?: number
}

export function usePlantQuery<TData, TSelected = TData>({
  resource,
  fetcher,
  select,
  refetchInterval,
}: PlantQueryOptions<TData, TSelected>) {
  const plant = useSelectedPlant()
  const plantId = plant?.id

  return useQuery({
    queryKey: [resource, plantId],
    queryFn: () => fetcher(plantId as string),
    enabled: Boolean(plantId),
    select,
    refetchInterval,
  })
}
