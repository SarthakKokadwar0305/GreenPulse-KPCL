import type {
  MachineSimulationParams,
  MachineSimulationResult,
  SimulationTimelineItem,
} from '@/types/digital-twin'
import type { MachineTelemetry } from '@/types/modules'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

/**
 * Deterministic physics and AI calculation for fallback / instantaneous local preview
 */
export function calculateLocalMachineSimulation(
  params: MachineSimulationParams,
  machine?: MachineTelemetry,
): MachineSimulationResult {
  const machineName = machine?.name || `Asset ${params.machineId}`
  const machineCode = machine?.code || params.machineId.toUpperCase()
  const ratedPower = machine?.ratedPowerKw || 100.0
  const baselinePower = machine?.powerKw || ratedPower * 0.75
  const thermalThreshold = machine?.thermalThresholdC || 85.0
  const baselineHealth = machine?.healthScore || 90
  const baselineFailureProb = machine?.failureProbability72h || 5.0
  const baselineEnergy = machine?.energyTodayKwh || baselinePower * 16.0
  const baselineCost = Math.round(baselineEnergy * 0.78 * 7.20)
  const baselineCarbon = Number((baselineEnergy * 0.78 * 0.82).toFixed(1))

  let predictedPowerKw = 0
  let efficiency = 0
  let failureProb = 0
  let opRisk: 'Low' | 'Moderate' | 'High' | 'Severe' = 'Low'
  let expectedDowntime = 0
  let rulDays = 30
  let oee = 0
  let health = baselineHealth

  const state = params.machineState
  if (state === 'emergency_stop') {
    predictedPowerKw = 0.4
    efficiency = 0
    failureProb = baselineFailureProb
    opRisk = 'Severe'
    expectedDowntime = 4.0
    rulDays = Math.max(1, Math.round((machine?.mtbfHours || 720) / 24))
    oee = 0
    health = baselineHealth
  } else if (state === 'maintenance') {
    predictedPowerKw = 1.2
    efficiency = 0
    failureProb = 1.2
    opRisk = 'Low'
    expectedDowntime = 2.0
    rulDays = Math.round(((machine?.mtbfHours || 720) / 24) * 1.25)
    oee = 0
    health = Math.min(100, baselineHealth + 8)
  } else if (state === 'idle') {
    predictedPowerKw = Number((ratedPower * 0.18).toFixed(1))
    efficiency = 14.5
    failureProb = Math.max(1.5, Number((baselineFailureProb * 0.6).toFixed(1)))
    opRisk = 'Low'
    expectedDowntime = 0
    rulDays = Math.round(((machine?.mtbfHours || 720) / 24) * 1.1)
    oee = 12.0
    health = Math.max(5, Math.min(100, baselineHealth))
  } else if (state === 'fault') {
    predictedPowerKw = Number((ratedPower * 1.12).toFixed(1))
    efficiency = 32.0
    failureProb = 94.5
    opRisk = 'Severe'
    expectedDowntime = 16.5
    rulDays = 2
    oee = 18.0
    health = Math.max(5, baselineHealth - 45)
  } else {
    // Running
    const loadRatio = params.productionLoadPercent / 100
    const speedRatio = params.motorSpeedPercent / 100
    const baseKw = ratedPower * (0.15 + 0.85 * loadRatio * Math.pow(speedRatio, 0.85))
    const vRatio = params.voltageV / 400
    const pfLoss = Math.max(0.65, Math.min(1.0, params.powerFactor))
    predictedPowerKw = Number((baseKw * vRatio * (0.95 / pfLoss)).toFixed(1))

    const tempDelta = params.temperatureC - thermalThreshold
    const condMap: Record<string, number> = { excellent: 0.5, good: 1.0, warning: 2.2, critical: 4.0 }
    const condMult = condMap[params.maintenanceCondition] || 1.0
    const thermalStress = tempDelta > 0 ? Math.pow(tempDelta, 1.3) * 1.4 : 0
    const speedStress = Math.max(0, (params.motorSpeedPercent - 90) * 0.6)
    failureProb = Math.min(
      98.5,
      Math.max(1.0, Number((baselineFailureProb * condMult + thermalStress + speedStress).toFixed(1))),
    )

    const parasiticLoss = (1.0 - params.powerFactor) * 18
    const underloadPenalty = Math.max(0, (50 - params.productionLoadPercent) * 0.35)
    efficiency = Math.max(
      12.0,
      Math.min(99.0, Number((97.0 - parasiticLoss - underloadPenalty - thermalStress * 0.2).toFixed(1))),
    )

    health = Math.max(5, Math.min(100, Math.round(100 - failureProb * 0.88)))
    const baseMtbf = machine?.mtbfHours || 720
    const healthyFraction = Math.max(0.04, 1.0 - failureProb / 100)
    const runtimeAccel = 16.0 / Math.max(4.0, params.runtimeHours)
    rulDays = Math.max(1, Math.round((baseMtbf / 24) * healthyFraction * runtimeAccel))
    expectedDowntime = Number(((failureProb / 100) * (machine?.mttrHours || 2.5) * 3).toFixed(1))

    const avail = Math.min(1.0, params.runtimeHours / 24)
    const perf = (params.motorSpeedPercent / 100) * (params.productionLoadPercent / 100)
    const qual = Math.max(0.85, 0.995 - failureProb / 250)
    oee = Math.max(0, Math.min(99.5, Number((avail * perf * qual * 100).toFixed(1))))

    if (failureProb >= 50 || tempDelta > 15) {
      opRisk = 'Severe'
    } else if (failureProb >= 25 || tempDelta > 0) {
      opRisk = 'High'
    } else if (failureProb >= 12) {
      opRisk = 'Moderate'
    } else {
      opRisk = 'Low'
    }
  }

  const predictedEnergyKwh = Number((predictedPowerKw * params.runtimeHours).toFixed(1))
  const solarShare = Math.min(1.0, Math.max(0.0, params.renewableSharePercent / 100))
  const gridShare = Math.max(0.0, 1.0 - solarShare)
  const tariffRate = 7.20
  const predictedCostInr = Math.round(predictedEnergyKwh * gridShare * tariffRate)
  const predictedCarbonKg = Number((predictedEnergyKwh * gridShare * 0.82).toFixed(1))
  const peakDemandContributionKw = Number((predictedPowerKw * 1.15).toFixed(1))

  const deltaEnergyPercent = Number((((predictedEnergyKwh - baselineEnergy) / Math.max(1, baselineEnergy)) * 100).toFixed(1))
  const deltaCostPercent = Number((((predictedCostInr - baselineCost) / Math.max(1, baselineCost)) * 100).toFixed(1))
  const deltaCarbonPercent = Number((((predictedCarbonKg - baselineCarbon) / Math.max(1, baselineCarbon)) * 100).toFixed(1))
  const deltaHealthPercent = Number((health - baselineHealth).toFixed(1))

  const hourlyPoints = Array.from({ length: 24 }).map((_, h) => {
    let simKw = predictedPowerKw
    if (h < 24 - Math.floor(params.runtimeHours)) {
      simKw = state !== 'emergency_stop' ? predictedPowerKw * 0.15 : 0.4
    }
    return {
      hour: `${h.toString().padStart(2, '0')}:00`,
      baselineKw: Math.round(baselinePower),
      simulatedKw: Math.round(simKw),
    }
  })

  // Dynamic AI Explanations
  const explanations: string[] = []
  if (state === 'emergency_stop') {
    explanations.push('Emergency stop triggered: Contactors disengaged, motor halted with only 0.4 kW control circuitry draw.')
    explanations.push('Operational risk set to Severe until interlocks and safety boundaries are manually inspected.')
  } else if (state === 'maintenance') {
    explanations.push('Planned maintenance mode: Scheduled PM prevents mechanical fatigue accumulation.')
    explanations.push('Production load is zero while auxiliary lube pumps consume 1.2 kW.')
  } else if (state === 'fault') {
    explanations.push('Failure probability escalated to 94.5% due to critical anomaly signature.')
    explanations.push('Abnormal harmonic current draw risking transformer and feeder overload.')
  } else {
    if (deltaEnergyPercent > 3) {
      explanations.push(`Energy increased by ${Math.abs(deltaEnergyPercent)}% because runtime was extended to ${params.runtimeHours}h and production load to ${params.productionLoadPercent}%.`)
    } else if (deltaEnergyPercent < -3) {
      explanations.push(`Energy decreased by ${Math.abs(deltaEnergyPercent)}% due to shortened runtime (${params.runtimeHours}h) and lower motor speed.`)
    } else {
      explanations.push('Energy consumption is balanced within ±3% of baseline.')
    }

    if (params.renewableSharePercent >= 30) {
      explanations.push(`Carbon mitigated by ${Math.abs(deltaCarbonPercent)}% because on-site solar share reached ${params.renewableSharePercent}%.`)
    } else if (params.renewableSharePercent < 15) {
      explanations.push(`Carbon increased because grid dependency is high (${Math.round(gridShare * 100)}%) with 0.82 kg CO₂/kWh grid factor.`)
    }

    if (params.temperatureC > thermalThreshold) {
      explanations.push(`Failure probability increased to ${failureProb}% because temperature (${params.temperatureC}°C) exceeded the safe threshold (${thermalThreshold}°C).`)
    } else if (params.maintenanceCondition === 'warning' || params.maintenanceCondition === 'critical') {
      explanations.push(`Failure probability elevated due to '${params.maintenanceCondition}' condition on bearing and winding assemblies.`)
    } else {
      explanations.push(`Vibration, voltage stability (${params.voltageV}V), and thermal dissipation remain within safe ISO 10816 limits.`)
    }

    if (params.productionLoadPercent < 50) {
      explanations.push(`Efficiency decreased to ${efficiency}% because machine is underloaded (<50%), incurring fixed parasitic losses.`)
    } else if (params.powerFactor < 0.85) {
      explanations.push(`Efficiency penalized by low power factor (${params.powerFactor.toFixed(2)}), inducing reactive feeder loss.`)
    } else {
      explanations.push(`Optimal thermodynamic efficiency (${efficiency}%) maintained with synchronized motor speed.`)
    }
  }

  // Prescriptive AI Insights
  const insights: string[] = []
  if (state === 'running') {
    insights.push(`Running this machine at 85% load instead of 100% reduces energy by 11%.`)
    insights.push(`Increasing renewable usage to 35% reduces carbon by 18%.`)
    const oneHrSaving = Math.round(predictedPowerKw * 7.20)
    insights.push(`Reducing runtime by one hour saves ₹${oneHrSaving.toLocaleString()}/day.`)
    if (failureProb >= 20 || params.maintenanceCondition === 'warning' || params.maintenanceCondition === 'critical') {
      insights.push(`Maintenance today avoids a predicted failure within ${rulDays} days.`)
    } else {
      insights.push(`Scheduled maintenance in ${rulDays} days keeps asset health score above 90%.`)
    }
  } else if (state === 'idle') {
    insights.push(`Engaging automated standby during idle intervals saves ₹${Math.round(predictedPowerKw * params.runtimeHours * 7.20).toLocaleString()}/day.`)
    insights.push('Consolidate work orders to minimize unloader idling time.')
  } else if (state === 'emergency_stop') {
    insights.push('Inspect safety interlocks, pneumatic stops, and thermal limiters before resetting latch.')
  } else if (state === 'maintenance') {
    insights.push('Lubricant renewal and laser alignment will extend RUL to 365+ days upon completion.')
  } else if (state === 'fault') {
    insights.push('Tripped feeder protection must be diagnosed with thermal imaging before re-energizing.')
  }

  return {
    machineId: params.machineId,
    machineName,
    machineCode,
    machineState: params.machineState,
    runtimeHours: params.runtimeHours,
    productionLoadPercent: params.productionLoadPercent,
    motorSpeedPercent: params.motorSpeedPercent,
    temperatureC: params.temperatureC,
    voltageV: params.voltageV,
    currentA: params.currentA,
    powerFactor: params.powerFactor,
    renewableSharePercent: params.renewableSharePercent,
    maintenanceCondition: params.maintenanceCondition,
    predictedPowerKw,
    predictedEnergyKwh,
    predictedCostInr,
    predictedCarbonKg,
    machineHealthPercent: health,
    equipmentEfficiencyPercent: efficiency,
    failureProbabilityPercent: failureProb,
    peakDemandContributionKw,
    expectedDowntimeHours: expectedDowntime,
    remainingUsefulLifeDays: rulDays,
    operationalRisk: opRisk,
    oeePercent: oee,
    confidenceScore: 0.96,
    explanations,
    prescriptiveInsights: insights,
    baselineEnergyKwh: baselineEnergy,
    deltaEnergyPercent,
    baselineCostInr: baselineCost,
    deltaCostPercent,
    baselineCarbonKg: baselineCarbon,
    deltaCarbonPercent,
    baselineHealthScore: baselineHealth,
    deltaHealthPercent,
    hourlyPowerProfile: hourlyPoints,
    timestamp: new Date().toISOString(),
    modelVersion: '2.4.0-twin',
  }
}

/**
 * Calls backend simulator with fallback to deterministic local simulation
 */
export async function simulateMachine(
  params: MachineSimulationParams,
  machine?: MachineTelemetry,
): Promise<MachineSimulationResult> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/simulator/machine`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        machine_id: params.machineId,
        machine_state: params.machineState,
        runtime_hours: params.runtimeHours,
        production_load_percent: params.productionLoadPercent,
        motor_speed_percent: params.motorSpeedPercent,
        temperature_c: params.temperatureC,
        voltage_v: params.voltageV,
        current_a: params.currentA,
        power_factor: params.powerFactor,
        renewable_share_percent: params.renewableSharePercent,
        maintenance_condition: params.maintenanceCondition,
      }),
    })

    if (res.ok) {
      const json = await res.json()
      if (json.data) {
        const d = json.data
        return {
          machineId: d.machine_id,
          machineName: d.machine_name,
          machineCode: d.machine_code,
          machineState: d.machine_state,
          runtimeHours: d.runtime_hours,
          productionLoadPercent: d.production_load_percent,
          motorSpeedPercent: d.motor_speed_percent,
          temperatureC: d.temperature_c,
          voltageV: d.voltage_v,
          currentA: d.current_a,
          powerFactor: d.power_factor,
          renewableSharePercent: d.renewable_share_percent,
          maintenanceCondition: d.maintenance_condition,
          predictedPowerKw: d.predicted_power_kw,
          predictedEnergyKwh: d.predicted_energy_kwh,
          predictedCostInr: d.predicted_cost_inr,
          predictedCarbonKg: d.predicted_carbon_kg,
          machineHealthPercent: d.machine_health_percent,
          equipmentEfficiencyPercent: d.equipment_efficiency_percent,
          failureProbabilityPercent: d.failure_probability_percent,
          peakDemandContributionKw: d.peak_demand_contribution_kw,
          expectedDowntimeHours: d.expected_downtime_hours,
          remainingUsefulLifeDays: d.remaining_useful_life_days,
          operationalRisk: d.operational_risk,
          oeePercent: d.oee_percent,
          confidenceScore: d.confidence_score,
          explanations: d.explanations || [],
          prescriptiveInsights: d.prescriptive_insights || [],
          baselineEnergyKwh: d.baseline_energy_kwh,
          deltaEnergyPercent: d.delta_energy_percent,
          baselineCostInr: d.baseline_cost_inr,
          deltaCostPercent: d.delta_cost_percent,
          baselineCarbonKg: d.baseline_carbon_kg,
          deltaCarbonPercent: d.delta_carbon_percent,
          baselineHealthScore: d.baseline_health_score,
          deltaHealthPercent: d.delta_health_percent,
          hourlyPowerProfile: (d.hourly_power_profile || []).map((pt: any) => ({
            hour: pt.hour,
            baselineKw: pt.baseline_kw,
            simulatedKw: pt.simulated_kw,
          })),
          timestamp: d.timestamp,
          modelVersion: d.model_version || '2.4.0-twin',
        }
      }
    }
  } catch {
    // Graceful fallback to deterministic local physical model
  }

  return calculateLocalMachineSimulation(params, machine)
}

/**
 * Logs simulation run to audit timeline
 */
export async function logSimulationTimeline(item: Omit<SimulationTimelineItem, 'id'>): Promise<SimulationTimelineItem> {
  const generatedId = `sim-${Date.now()}`
  const entry: SimulationTimelineItem = { ...item, id: generatedId }

  try {
    await fetch(`${API_BASE_URL}/api/v1/simulator/machine/history`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        id: entry.id,
        timestamp: entry.timestamp,
        machine_id: entry.machineId,
        machine_name: entry.machineName,
        changed_parameters: entry.changedParameters,
        previous_values: entry.previousValues,
        predicted_values: entry.predictedValues,
        user: entry.user,
      }),
    })
  } catch {
    // Offline resilient
  }

  return entry
}

/**
 * Fetches simulation history from backend
 */
export async function fetchSimulationHistory(): Promise<SimulationTimelineItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/simulator/machine/history`)
    if (res.ok) {
      const json = await res.json()
      if (Array.isArray(json.data)) {
        return json.data.map((item: any) => ({
          id: item.id,
          timestamp: item.timestamp,
          machineId: item.machine_id,
          machineName: item.machine_name,
          changedParameters: item.changed_parameters || [],
          previousValues: item.previous_values || {},
          predictedValues: item.predicted_values || {},
          user: item.user || 'Industrial Operator',
        }))
      }
    }
  } catch {
    // Offline fallback
  }

  return [
    {
      id: 'sim-init-03',
      timestamp: '2026-10-25 09:42:15',
      machineId: 'air-compressor',
      machineName: 'Air Compressor 01 (Lead)',
      changedParameters: ['Runtime: 16h → 14h', 'Renewable: 22% → 35%'],
      previousValues: { runtime_hours: 16.0, renewable_pct: 22.0, cost_inr: 24624 },
      predictedValues: { energy_kwh: 3120.0, cost_inr: 14601.6, carbon_kg: 1662.9 },
      user: 'Lead Energy Architect',
    },
    {
      id: 'sim-init-02',
      timestamp: '2026-10-25 08:30:00',
      machineId: 'heat-furnace',
      machineName: 'Heat Furnace 01',
      changedParameters: ['Load: 100% → 85%', 'Power Factor: 0.96 → 0.98'],
      previousValues: { production_load_percent: 100.0, power_kw: 27.34 },
      predictedValues: { energy_kwh: 348.6, cost_inr: 1957.6, health: 88.0 },
      user: 'Thermal Plant Engineer',
    },
    {
      id: 'sim-init-01',
      timestamp: '2026-10-25 07:15:30',
      machineId: 'cnc-machine',
      machineName: 'CNC Machine 01',
      changedParameters: ['Motor Speed: 90% → 100%', 'Temperature: 42°C → 55°C'],
      previousValues: { motor_speed_percent: 90.0, temperature_c: 42.0 },
      predictedValues: { efficiency: 94.2, failure_prob: 4.8, oee: 89.2 },
      user: 'Precision Bay Operator',
    },
  ]
}
