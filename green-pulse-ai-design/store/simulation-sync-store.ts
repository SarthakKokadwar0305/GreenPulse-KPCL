import { create } from 'zustand'
import type {
  MachineSimulationParams,
  MachineSimulationResult,
  SimulationScenario,
  SimulationTimelineItem,
} from '@/types/digital-twin'
import {
  calculateLocalMachineSimulation,
  fetchSimulationHistory,
  logSimulationTimeline,
} from '@/services/digital-twin-service'
import type { MachineTelemetry } from '@/types/modules'

export interface PlantSimulatorSyncState {
  productionLoad: number // 50 - 150
  machineRuntime: number // 4 - 24
  shiftSchedule: '1-shift' | '2-shift' | '3-shift' | 'night-shift'
  baseTariff: number // 4 - 15
  renewablePercent: number // 0 - 100
  lastUpdatedFrom: 'plant' | 'machine' | null
}

interface SimulationSyncStore {
  // Plant-level parameters (synced with What-If simulator)
  plantState: PlantSimulatorSyncState
  setPlantState: (partial: Partial<PlantSimulatorSyncState>, source?: 'plant' | 'machine') => void

  // Machine simulation params per machine ID
  machineSimulations: Record<string, MachineSimulationParams>
  machineResults: Record<string, MachineSimulationResult>
  updateMachineParam: (
    machineId: string,
    params: Partial<MachineSimulationParams>,
    machineMeta?: MachineTelemetry,
  ) => void

  // Scenario management
  scenarios: SimulationScenario[]
  activeScenarioId: string | null
  saveScenario: (name: string, description: string, machineId: string) => void
  deleteScenario: (id: string) => void
  setActiveScenario: (id: string | null) => void

  // Simulation Timeline Audit
  timeline: SimulationTimelineItem[]
  loadTimeline: () => Promise<void>
  addTimelineEntry: (entry: Omit<SimulationTimelineItem, 'id'>) => Promise<void>

  // Reset helper
  resetMachineSimulation: (machineId: string, machineMeta?: MachineTelemetry) => void
}

export const useSimulationSyncStore = create<SimulationSyncStore>((set, get) => ({
  plantState: {
    productionLoad: 100,
    machineRuntime: 16,
    shiftSchedule: '2-shift',
    baseTariff: 7.2,
    renewablePercent: 22,
    lastUpdatedFrom: null,
  },

  setPlantState: (partial, source = 'plant') => {
    set((state) => {
      const nextPlantState: PlantSimulatorSyncState = {
        ...state.plantState,
        ...partial,
        lastUpdatedFrom: source,
      }

      // If plant state was changed from What-If, proportionally synchronize machines!
      if (source === 'plant') {
        const nextMachineSims = { ...state.machineSimulations }
        const nextMachineResults = { ...state.machineResults }

        Object.keys(nextMachineSims).forEach((mId) => {
          const current = nextMachineSims[mId]
          const updatedParams: MachineSimulationParams = {
            ...current,
            productionLoadPercent: Math.min(100, Math.max(10, Math.round(nextPlantState.productionLoad * 0.9))),
            runtimeHours: Math.min(24, Math.max(0, nextPlantState.machineRuntime)),
            renewableSharePercent: nextPlantState.renewablePercent,
          }
          nextMachineSims[mId] = updatedParams
          nextMachineResults[mId] = calculateLocalMachineSimulation(updatedParams)
        })

        return {
          plantState: nextPlantState,
          machineSimulations: nextMachineSims,
          machineResults: nextMachineResults,
        }
      }

      return { plantState: nextPlantState }
    })
  },

  machineSimulations: {},
  machineResults: {},

  updateMachineParam: (machineId, partial, machineMeta) => {
    set((state) => {
      const existing = state.machineSimulations[machineId] || {
        machineId,
        machineState: machineMeta?.status === 'idle' ? 'idle' : machineMeta?.status === 'warning' ? 'running' : 'running',
        runtimeHours: machineMeta?.runtimeHoursShift || 16,
        productionLoadPercent: 85,
        motorSpeedPercent: 85,
        temperatureC: machineMeta?.temperatureC || 65,
        voltageV: machineMeta?.voltage?.lineToLine || 400,
        currentA: machineMeta?.current?.l1 || 35,
        powerFactor: machineMeta?.powerFactor || 0.92,
        renewableSharePercent: state.plantState.renewablePercent || 22,
        maintenanceCondition: (machineMeta?.healthScore && machineMeta.healthScore > 90) ? 'excellent' : 'good',
      }

      const nextParams: MachineSimulationParams = {
        ...existing,
        ...partial,
      }

      const result = calculateLocalMachineSimulation(nextParams, machineMeta)

      // Synchronize back to plant level if runtime or load was adjusted!
      const currentPlant = state.plantState
      let nextPlantLoad = currentPlant.productionLoad
      let nextPlantRuntime = currentPlant.machineRuntime
      let nextPlantRenewable = currentPlant.renewablePercent

      if (partial.productionLoadPercent !== undefined) {
        nextPlantLoad = Math.round(nextParams.productionLoadPercent * 1.05)
      }
      if (partial.runtimeHours !== undefined) {
        nextPlantRuntime = Math.round(nextParams.runtimeHours)
      }
      if (partial.renewableSharePercent !== undefined) {
        nextPlantRenewable = Math.round(nextParams.renewableSharePercent)
      }

      return {
        machineSimulations: {
          ...state.machineSimulations,
          [machineId]: nextParams,
        },
        machineResults: {
          ...state.machineResults,
          [machineId]: result,
        },
        plantState: {
          ...currentPlant,
          productionLoad: nextPlantLoad,
          machineRuntime: nextPlantRuntime,
          renewablePercent: nextPlantRenewable,
          lastUpdatedFrom: 'machine',
        },
      }
    })
  },

  scenarios: [
    {
      id: 'scenario-baseline',
      name: 'Baseline Operating Point',
      description: 'Factory nominal design specifications (16h shift, 100% load, 22% grid-tied solar).',
      machineId: 'air-compressor',
      machineName: 'Air Compressor 01 (Lead)',
      params: {
        machineId: 'air-compressor',
        machineState: 'running',
        runtimeHours: 16,
        productionLoadPercent: 100,
        motorSpeedPercent: 95,
        temperatureC: 86,
        voltageV: 401,
        currentA: 595,
        powerFactor: 0.88,
        renewableSharePercent: 22,
        maintenanceCondition: 'good',
      },
      result: calculateLocalMachineSimulation({
        machineId: 'air-compressor',
        machineState: 'running',
        runtimeHours: 16,
        productionLoadPercent: 100,
        motorSpeedPercent: 95,
        temperatureC: 86,
        voltageV: 401,
        currentA: 595,
        powerFactor: 0.88,
        renewableSharePercent: 22,
        maintenanceCondition: 'good',
      }),
      savedAt: '2026-10-25T08:00:00.000Z',
    },
    {
      id: 'scenario-a',
      name: 'Scenario A: Eco Lean Optimization',
      description: '85% load, 14h runtime, 45% solar mix with tuned power factor 0.95.',
      machineId: 'air-compressor',
      machineName: 'Air Compressor 01 (Lead)',
      params: {
        machineId: 'air-compressor',
        machineState: 'running',
        runtimeHours: 14,
        productionLoadPercent: 85,
        motorSpeedPercent: 82,
        temperatureC: 78,
        voltageV: 400,
        currentA: 510,
        powerFactor: 0.95,
        renewableSharePercent: 45,
        maintenanceCondition: 'excellent',
      },
      result: calculateLocalMachineSimulation({
        machineId: 'air-compressor',
        machineState: 'running',
        runtimeHours: 14,
        productionLoadPercent: 85,
        motorSpeedPercent: 82,
        temperatureC: 78,
        voltageV: 400,
        currentA: 510,
        powerFactor: 0.95,
        renewableSharePercent: 45,
        maintenanceCondition: 'excellent',
      }),
      savedAt: '2026-10-25T08:30:00.000Z',
    },
    {
      id: 'scenario-b',
      name: 'Scenario B: High Throughput Surge',
      description: 'Max 100% speed, 22h runtime, critical thermal check.',
      machineId: 'air-compressor',
      machineName: 'Air Compressor 01 (Lead)',
      params: {
        machineId: 'air-compressor',
        machineState: 'running',
        runtimeHours: 22,
        productionLoadPercent: 100,
        motorSpeedPercent: 100,
        temperatureC: 94,
        voltageV: 395,
        currentA: 620,
        powerFactor: 0.86,
        renewableSharePercent: 22,
        maintenanceCondition: 'warning',
      },
      result: calculateLocalMachineSimulation({
        machineId: 'air-compressor',
        machineState: 'running',
        runtimeHours: 22,
        productionLoadPercent: 100,
        motorSpeedPercent: 100,
        temperatureC: 94,
        voltageV: 395,
        currentA: 620,
        powerFactor: 0.86,
        renewableSharePercent: 22,
        maintenanceCondition: 'warning',
      }),
      savedAt: '2026-10-25T09:15:00.000Z',
    },
  ],

  activeScenarioId: null,

  saveScenario: (name, description, machineId) => {
    const currentParams = get().machineSimulations[machineId]
    const currentResult = get().machineResults[machineId]
    if (!currentParams || !currentResult) return

    const newScenario: SimulationScenario = {
      id: `scen-${Date.now()}`,
      name,
      description,
      machineId,
      machineName: currentResult.machineName,
      params: { ...currentParams },
      result: { ...currentResult },
      savedAt: new Date().toISOString(),
    }

    set((state) => ({
      scenarios: [newScenario, ...state.scenarios],
      activeScenarioId: newScenario.id,
    }))
  },

  deleteScenario: (id) => {
    set((state) => ({
      scenarios: state.scenarios.filter((s) => s.id !== id),
      activeScenarioId: state.activeScenarioId === id ? null : state.activeScenarioId,
    }))
  },

  setActiveScenario: (id) => {
    set({ activeScenarioId: id })
  },

  timeline: [],

  loadTimeline: async () => {
    const items = await fetchSimulationHistory()
    set({ timeline: items })
  },

  addTimelineEntry: async (entry) => {
    const saved = await logSimulationTimeline(entry)
    set((state) => ({
      timeline: [saved, ...state.timeline].slice(0, 50),
    }))
  },

  resetMachineSimulation: (machineId, machineMeta) => {
    set((state) => {
      const resetParams: MachineSimulationParams = {
        machineId,
        machineState: machineMeta?.status === 'idle' ? 'idle' : 'running',
        runtimeHours: machineMeta?.runtimeHoursShift || 16,
        productionLoadPercent: 85,
        motorSpeedPercent: 85,
        temperatureC: machineMeta?.temperatureC || 65,
        voltageV: machineMeta?.voltage?.lineToLine || 400,
        currentA: machineMeta?.current?.l1 || 35,
        powerFactor: machineMeta?.powerFactor || 0.92,
        renewableSharePercent: state.plantState.renewablePercent || 22,
        maintenanceCondition: 'good',
      }
      const resetResult = calculateLocalMachineSimulation(resetParams, machineMeta)

      return {
        machineSimulations: {
          ...state.machineSimulations,
          [machineId]: resetParams,
        },
        machineResults: {
          ...state.machineResults,
          [machineId]: resetResult,
        },
      }
    })
  },
}))
