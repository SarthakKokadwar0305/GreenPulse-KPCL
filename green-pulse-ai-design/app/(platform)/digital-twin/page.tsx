import type { Metadata } from 'next'

import { DigitalTwinView } from '@/components/modules/digital-twin/digital-twin-view'

export const metadata: Metadata = {
  title: 'Digital Twin | GreenPulse AI',
  description: 'Interactive cyber-physical 2.5D factory floor and machine telemetry digital twin.',
}

export default function DigitalTwinPage() {
  return <DigitalTwinView />
}
