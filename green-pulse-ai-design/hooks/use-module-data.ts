'use client'

import {
  getAiForecast,
  getAnomalies,
  getCarbonAccounting,
  getDigitalTwin,
  getEnergyExplorer,
  getPlantOverview,
  getRecommendations,
  getReportsData,
  getSettingsData,
  getSimulatorBaseline,
} from '@/services/plant-service'

import { usePlantQuery } from './use-plant-query'

const REFRESH_INTERVAL_MS = 30_000

export function usePlantOverviewData() {
  return usePlantQuery({
    resource: 'overview',
    fetcher: getPlantOverview,
    refetchInterval: REFRESH_INTERVAL_MS,
  })
}

export function useDigitalTwinData() {
  return usePlantQuery({
    resource: 'digital-twin',
    fetcher: getDigitalTwin,
    refetchInterval: REFRESH_INTERVAL_MS,
  })
}

export function useEnergyExplorerData() {
  return usePlantQuery({
    resource: 'energy-explorer',
    fetcher: getEnergyExplorer,
    refetchInterval: REFRESH_INTERVAL_MS,
  })
}

export function useCarbonAccountingData() {
  return usePlantQuery({
    resource: 'carbon-accounting',
    fetcher: getCarbonAccounting,
    refetchInterval: REFRESH_INTERVAL_MS,
  })
}

export function useAiForecastData() {
  return usePlantQuery({
    resource: 'ai-forecast',
    fetcher: getAiForecast,
    refetchInterval: REFRESH_INTERVAL_MS,
  })
}

export function useAnomaliesData() {
  return usePlantQuery({
    resource: 'anomalies',
    fetcher: getAnomalies,
    refetchInterval: REFRESH_INTERVAL_MS,
  })
}

export function useRecommendationsData() {
  return usePlantQuery({
    resource: 'recommendations',
    fetcher: getRecommendations,
    refetchInterval: REFRESH_INTERVAL_MS,
  })
}

export function useSimulatorBaselineData() {
  return usePlantQuery({
    resource: 'simulator',
    fetcher: getSimulatorBaseline,
  })
}

export function useReportsData() {
  return usePlantQuery({
    resource: 'reports',
    fetcher: getReportsData,
  })
}

export function useSettingsData() {
  return usePlantQuery({
    resource: 'settings',
    fetcher: getSettingsData,
  })
}
