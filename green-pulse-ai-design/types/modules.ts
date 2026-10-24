import type { IconKey, Severity, Tone, Trend } from './common'
import type { MachineStatus } from './machine'

export interface PlantKpi {
  id: string
  title: string
  value: number
  decimals?: number
  prefix?: string
  unit?: string
  iconKey: IconKey
  trend: Trend
  status: { label: string; tone: Tone }
  description: string
  sparkline: number[]
}

export interface ProductionSummary {
  hourlyThroughput: { hour: string; target: number; actual: number }[]
  targetUnits: number
  actualUnits: number
  throughputRatePerHour: number
  firstPassYield: number
  downtimeMinutes: number
  activeLines: number
  totalLines: number
}

export interface DepartmentMetric {
  id: string
  name: string
  zone: string
  powerKw: number
  energyTodayKwh: number
  efficiency: number
  healthScore: number
  status: 'optimal' | 'warning' | 'normal'
  machineCount: number
}

export interface UtilityConsumptionItem {
  id: string
  name: string
  currentRate: number
  unit: string
  capacity: number
  utilizationPercent: number
  todayTotal: number
  status: 'normal' | 'peak' | 'standby'
}

export interface ActiveUtilityAsset {
  id: string
  name: string
  type: string
  powerKw: number
  loadFactor: number
  status: 'running' | 'standby' | 'warning'
  runtimeTodayHours: number
}

export interface ShiftInfo {
  currentShift: string
  shiftCode: string
  timeRange: string
  leadEngineer: string
  leadRole: string
  operatorsOnFloor: number
  maintenanceTechs: number
  shiftEnergyBudgetKwh: number
  shiftEnergyConsumedKwh: number
  productionTarget: number
  productionActual: number
  elapsedPercent: number
}

export interface FactoryTimelineItem {
  id: string
  time: string
  title: string
  category: 'production' | 'maintenance' | 'grid' | 'safety'
  description: string
  severity?: 'info' | 'warning' | 'critical' | 'success'
}

export interface PlantOverviewData {
  plantId: string
  plantName: string
  lastUpdated: string
  kpis: PlantKpi[]
  productionSummary: ProductionSummary
  departments: DepartmentMetric[]
  utilities: UtilityConsumptionItem[]
  activeUtilities: ActiveUtilityAsset[]
  shift: ShiftInfo
  timeline: FactoryTimelineItem[]
  healthSummary: {
    healthIndex: number
    predictiveRisk: number
    uptimePercent: number
    complianceStatus: string
    iso50001Status: string
  }
}

// Digital Twin Types
export interface MachineTelemetry {
  id: string
  name: string
  code: string
  category: string
  zone: string
  floorPosition: { x: number; y: number; width: number; height: number }
  status: 'running' | 'idle' | 'warning' | 'fault'
  powerKw: number
  ratedPowerKw: number
  temperatureC: number
  thermalThresholdC: number
  voltage: { l1: number; l2: number; l3: number; lineToLine: number; unbalancePercent: number }
  current: { l1: number; l2: number; l3: number }
  powerFactor: number
  runtimeHoursTotal: number
  runtimeHoursShift: number
  mtbfHours: number
  mttrHours: number
  healthScore: number
  degradationRatePercent: number
  failureProbability72h: number
  likelyFailureMode: string
  carbonKgPerHour: number
  carbonTodayKg: number
  carbonSharePercent: number
  energyTodayKwh: number
  lastMaintenanceDate: string
  nextScheduledPm: string
  maintenanceHistory: { date: string; type: string; technician: string; notes: string }[]
  aiInsight: {
    title: string
    explanation: string
    severity: 'warning' | 'critical' | 'info' | 'success'
    suggestedRemedy: string
    potentialSavingsKw: number
  }
  timeline24h: { time: string; state: 'running' | 'idle' | 'warning' | 'fault'; power: number }[]
  specs: {
    model: string
    serial: string
    commissionDate: string
    operatorInCharge: string
    electricalSubstation: string
  }
}

// Energy Explorer Types
export interface EnergyExplorerData {
  currentDemandKw: number
  contractedPeakLimitKw: number
  peakHeadroomKw: number
  todayTotalKwh: number
  estimatedDailyCost: number
  hourlyTrend: { hour: string; actualKw: number; baselineKw: number; tariffRate: number; isPeakTariff: boolean }[]
  dailyTrend: { date: string; day: string; energyKwh: number; cost: number; targetKwh: number }[]
  weeklyTrend: { week: string; energyKwh: number; baselineKwh: number; weekendRatioPercent: number }[]
  monthlyTrend: { month: string; energyMwh: number; budgetMwh: number; costLaksh: number }[]
  machineComparison: { machine: string; currentKw: number; energyKwh: number; sharePercent: number; color: string }[]
  departmentComparison: { department: string; powerKw: number; sharePercent: number; costPerHour: number }[]
  peakDemandAnalytics: {
    peakTime: string
    peakRecordedKw: number
    penaltyThresholdKw: number
    powerFactorAtPeak: number
    exceedanceRiskPercent: number
  }
  heatmap7x24: { day: string; hours: number[] }[]
}

// Carbon Accounting Types
export interface CarbonAccountingData {
  todayTotalTons: number
  todayTargetTons: number
  monthToDateTons: number
  sustainabilityScore: number
  sustainabilityTier: string
  scope1: {
    totalTons: number
    targetTons: number
    breakdown: { source: string; tons: number; share: number; activityData: string }[]
  }
  scope2: {
    totalTons: number
    gridEmissionFactorKgPerKwh: number
    purchasedMwh: number
    renewableOffsetTons: number
    breakdown: { source: string; tons: number; share: number }[]
  }
  monthlyTrend: { month: string; scope1: number; scope2: number; netTotal: number; target: number }[]
  byMachine: { machine: string; carbonTons: number; intensityKgPerUnit: number; percent: number }[]
  byDepartment: { department: string; tons: number; sharePercent: number }[]
  esgOverview: {
    environmentalIndex: number
    renewableEnergySharePercent: number
    waterRecycleRatioPercent: number
    wasteDivertedPercent: number
    griCompliance: string
    brsrStatus: string
  }
}

// AI Forecast Types
export interface AiForecastData {
  forecastRange: string
  generatedAt: string
  modelArchitecture: string
  r2Score: number
  projectedDayEnergyKwh: number
  projectedCost: number
  projectedCarbonTons: number
  projectedPeakDemandKw: number
  peakHour: string
  hourlyForecast: {
    time: string
    actualKw: number | null
    forecastKw: number
    lowerBound80: number
    upperBound80: number
    lowerBound95: number
    upperBound95: number
    temperatureC: number
    scheduledActivity: string | null
  }[]
  aiExplanation: {
    primaryDrivers: { factor: string; impactKw: string; direction: 'up' | 'down'; rationale: string }[]
    modelConfidenceNote: string
    peakSpikeWarning: string
  }
  timelineMilestones: {
    time: string
    event: string
    impact: string
    recommendation: string
    severity: 'info' | 'warning' | 'normal'
  }[]
}

// Anomaly Center Types
export interface AnomalyIncident {
  id: string
  machineId: string
  machineName: string
  zone: string
  severity: 'critical' | 'warning' | 'info'
  status: 'open' | 'investigating' | 'acknowledged' | 'resolved'
  detectedAt: string
  durationMinutes: number
  rootCause: string
  evidence: { metric: string; measured: string; expected: string; zScore: number }[]
  confidencePercent: number
  suggestedAction: string
  estimatedCostImpactPerHour: number
  currency: string
  assignedEngineer?: string
  workOrderId?: string
}

// Recommendation Center Types
export interface AiRecommendation {
  id: string
  title: string
  machineName: string
  category: 'Load Shifting' | 'Asset Tuning' | 'Automation' | 'Maintenance' | 'Renewables'
  priority: 'High' | 'Medium' | 'Low'
  estimatedSavingsKwhPerMonth: number
  estimatedSavingsCurrencyPerMonth: number
  estimatedCarbonReductionTonsPerMonth: number
  paybackPeriodMonths: number
  roiPercent: number
  confidencePercent: number
  rationale: string
  actionSteps: string[]
  applied: boolean
  appliedAt?: string
}

// What-If Simulator Types
export interface SimulationBaseline {
  productionLoadPercent: number
  machineRuntimeHours: number
  shiftSchedule: '1-shift' | '2-shift' | '3-shift' | 'night-shift'
  baseTariffPerKwh: number
  peakTariffMultiplier: number
  renewableSharePercent: number
  dailyEnergyKwh: number
  dailyCost: number
  dailyCarbonTons: number
  hourlyProfile: { hour: string; baselineKw: number }[]
}

// Reports Types
export interface IndustrialReport {
  id: string
  title: string
  category: 'energy' | 'carbon' | 'forecast' | 'anomaly'
  period: string
  generatedAt: string
  author: string
  fileSize: string
  status: 'ready' | 'generating' | 'scheduled'
  downloadUrl?: string
  summaryStats: { label: string; value: string }[]
}

export interface ScheduledReportConfig {
  id: string
  name: string
  frequency: 'Daily' | 'Weekly' | 'Monthly'
  sendTime: string
  recipients: string[]
  format: 'PDF' | 'Excel' | 'CSV'
  category: string
  active: boolean
  lastSent: string
}

// Settings Types
export interface PlantSettings {
  plantName: string
  facilityCode: string
  jurisdiction: string
  location: string
  contractedDemandKw: number
  utilityAccount: string
  substationFeeder: string
  operatingShifts: string
  ratedPlantCapacityTonsPerDay: number
}

export interface UserProfileSettings {
  name: string
  email: string
  role: string
  department: string
  licenseTier: string
  phone: string
  twoFactorEnabled: boolean
  timezone: string
  avatarUrl?: string
}

export interface NotificationThresholds {
  peakDemandWarningKw: number
  peakDemandCriticalKw: number
  powerFactorMinimum: number
  thermalAlarmThresholdC: number
  anomalyNotificationEmail: boolean
  anomalyNotificationSms: boolean
  webhookUrl: string
  quietHoursStart: string
  quietHoursEnd: string
}

export interface ApiConfiguration {
  scadaHost: string
  scadaPort: number
  opcUaEndpoint: string
  mqttBrokerUrl: string
  apiKeyMasked: string
  syncIntervalSeconds: number
  connectionStatus: 'connected' | 'degraded' | 'disconnected'
  lastTelemetryHeartbeat: string
}

export interface AuditLogEntry {
  id: string
  timestamp: string
  user: string
  action: string
  module: string
  ipAddress: string
  status: 'success' | 'warning' | 'security_alert'
  hash: string
}
