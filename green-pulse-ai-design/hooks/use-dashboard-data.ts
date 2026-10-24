'use client'

import {
  getAlerts,
  getDashboardOverview,
  getInsights,
  getMachines,
  getTimeline,
} from '@/services/plant-service'
import type { MachineEnergyComparison, PlantAlert } from '@/types'

import { usePlantQuery } from './use-plant-query'

const LIVE_REFRESH_MS = 30_000

export function useDashboardOverview() {
  return usePlantQuery({
    resource: 'dashboard',
    fetcher: getDashboardOverview,
    refetchInterval: LIVE_REFRESH_MS,
  })
}

export function useSystemStatus() {
  return usePlantQuery({
    resource: 'dashboard',
    fetcher: getDashboardOverview,
    select: (overview) => overview.system,
    refetchInterval: LIVE_REFRESH_MS,
  })
}

export function useMachines() {
  return usePlantQuery({
    resource: 'machines',
    fetcher: getMachines,
    refetchInterval: LIVE_REFRESH_MS,
  })
}

export function useMachineEnergyComparison() {
  return usePlantQuery({
    resource: 'machines',
    fetcher: getMachines,
    select: (machines): MachineEnergyComparison[] =>
      machines.map((machine) => ({
        machineId: machine.id,
        machine: machine.shortName,
        actual: machine.energyKwh,
        target: machine.energyTargetKwh,
      })),
    refetchInterval: LIVE_REFRESH_MS,
  })
}

export function useAlerts() {
  return usePlantQuery({
    resource: 'alerts',
    fetcher: getAlerts,
    select: (alerts): PlantAlert[] =>
      [...alerts].sort(
        (a, b) =>
          new Date(b.occurredAt).getTime() - new Date(a.occurredAt).getTime(),
      ),
    refetchInterval: LIVE_REFRESH_MS,
  })
}

export function useInsights() {
  return usePlantQuery({
    resource: 'insights',
    fetcher: getInsights,
  })
}

export function useTimeline() {
  return usePlantQuery({
    resource: 'timeline',
    fetcher: getTimeline,
    refetchInterval: LIVE_REFRESH_MS,
  })
}
