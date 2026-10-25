export type MachineState = 'running' | 'idle' | 'maintenance' | 'fault' | 'emergency_stop'

export type MaintenanceCondition = 'excellent' | 'good' | 'warning' | 'critical'

export interface MachineSimulationParams {
  machineId: string
  machineState: MachineState
  runtimeHours: number // 0 - 24
  productionLoadPercent: number // 0 - 100
  motorSpeedPercent: number // 0 - 100
  temperatureC: number
  voltageV: number // 360 - 440
  currentA: number
  powerFactor: number // 0.70 - 1.00
  renewableSharePercent: number // 0 - 100
  maintenanceCondition: MaintenanceCondition
}

export interface MachineSimulationResult {
  machineId: string
  machineName: string
  machineCode: string
  machineState: MachineState
  runtimeHours: number
  productionLoadPercent: number
  motorSpeedPercent: number
  temperatureC: number
  voltageV: number
  currentA: number
  powerFactor: number
  renewableSharePercent: number
  maintenanceCondition: MaintenanceCondition

  // 12 Live AI Predictions
  predictedPowerKw: number
  predictedEnergyKwh: number
  predictedCostInr: number
  predictedCarbonKg: number
  machineHealthPercent: number
  equipmentEfficiencyPercent: number
  failureProbabilityPercent: number
  peakDemandContributionKw: number
  expectedDowntimeHours: number
  remainingUsefulLifeDays: number
  operationalRisk: 'Low' | 'Moderate' | 'High' | 'Severe'
  oeePercent: number
  confidenceScore: number

  // AI Explanations and Prescriptive Insights
  explanations: string[]
  prescriptiveInsights: string[]

  // Deltas compared to baseline telemetry
  baselineEnergyKwh: number
  deltaEnergyPercent: number
  baselineCostInr: number
  deltaCostPercent: number
  baselineCarbonKg: number
  deltaCarbonPercent: number
  baselineHealthScore: number
  deltaHealthPercent: number

  // 24h Profile
  hourlyPowerProfile: { hour: string; baselineKw: number; simulatedKw: number }[]
  timestamp: string
  modelVersion: string
}

export interface SimulationScenario {
  id: string
  name: string
  description?: string
  machineId: string
  machineName: string
  params: MachineSimulationParams
  result: MachineSimulationResult
  savedAt: string
}

export interface SimulationTimelineItem {
  id: string
  timestamp: string
  machineId: string
  machineName: string
  changedParameters: string[]
  previousValues: Record<string, string | number>
  predictedValues: Record<string, string | number>
  user: string
}
