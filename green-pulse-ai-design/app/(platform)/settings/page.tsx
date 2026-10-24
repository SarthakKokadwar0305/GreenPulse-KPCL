import type { Metadata } from 'next'

import { SettingsView } from '@/components/modules/settings/settings-view'

export const metadata: Metadata = {
  title: 'Settings & System Configuration | GreenPulse AI',
  description: 'Plant parameters, SCADA gateway configuration, user roles, security, and audit logs.',
}

export default function SettingsPage() {
  return <SettingsView />
}
