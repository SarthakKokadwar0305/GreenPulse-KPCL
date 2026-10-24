import type { Metadata } from 'next'

import { EnergyExplorerView } from '@/components/modules/energy-explorer/energy-explorer-view'

export const metadata: Metadata = {
  title: 'Energy Explorer | GreenPulse AI',
  description: 'Detailed multi-resolution industrial energy analytics and 7-day 24h consumption heatmaps.',
}

export default function EnergyExplorerPage() {
  return <EnergyExplorerView />
}
