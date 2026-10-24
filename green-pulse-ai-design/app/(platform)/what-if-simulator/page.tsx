import type { Metadata } from 'next'

import { WhatIfSimulatorView } from '@/components/modules/what-if-simulator/what-if-simulator-view'

export const metadata: Metadata = {
  title: 'What-if Simulator | GreenPulse AI',
  description: 'Interactive parametric energy simulation for production load, machine runtimes, and tariff schedules.',
}

export default function WhatIfSimulatorPage() {
  return <WhatIfSimulatorView />
}
