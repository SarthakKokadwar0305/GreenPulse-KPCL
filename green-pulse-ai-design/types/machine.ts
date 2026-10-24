import type { IconKey } from './common'

export type MachineStatus = 'running' | 'idle' | 'warning' | 'maintenance'

export interface MachinePowerSample {
  time: string
  power: number
}

export interface Machine {
  id: string
  name: string
  shortName: string
  zone: string
  iconKey: IconKey
  status: MachineStatus
  powerKw: number
  ratedPowerKw: number
  temperatureC: number
  efficiency: number
  healthScore: number
  energyKwh: number
  energyTargetKwh: number
  uptimeHours: number
  lastMaintenance: string
  powerHistory: MachinePowerSample[]
}

export interface MachineEnergyComparison {
  machineId: string
  machine: string
  actual: number
  target: number
}
