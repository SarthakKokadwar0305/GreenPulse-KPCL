import type {
  AlertStatus,
  InsightSeverity,
  MachineStatus,
  Tone,
} from '@/types'

interface StatusMeta {
  label: string
  tone: Tone
}

export const MACHINE_STATUS_META: Record<MachineStatus, StatusMeta> = {
  running: { label: 'Running', tone: 'success' },
  idle: { label: 'Idle', tone: 'neutral' },
  warning: { label: 'Needs attention', tone: 'warning' },
  maintenance: { label: 'Maintenance', tone: 'info' },
}

export const ALERT_STATUS_META: Record<AlertStatus, StatusMeta> = {
  open: { label: 'Open', tone: 'warning' },
  investigating: { label: 'Investigating', tone: 'info' },
  acknowledged: { label: 'Acknowledged', tone: 'neutral' },
  resolved: { label: 'Resolved', tone: 'success' },
}

export const SEVERITY_LABEL: Record<InsightSeverity, string> = {
  critical: 'Critical',
  warning: 'Warning',
  info: 'Info',
  success: 'Optimal',
}
