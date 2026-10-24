import type { Metadata } from 'next'

import { AnomalyCenterView } from '@/components/modules/anomaly-center/anomaly-center-view'

export const metadata: Metadata = {
  title: 'Anomaly Center | GreenPulse AI',
  description: 'Industrial automated fault detection, diagnostics (FDD), and root-cause failure incidents.',
}

export default function AnomalyCenterPage() {
  return <AnomalyCenterView />
}
