import type { Metadata } from 'next'

import { PlantOverviewView } from '@/components/modules/plant-overview/plant-overview-view'

export const metadata: Metadata = {
  title: 'Plant Overview | GreenPulse AI',
  description: 'Executive overview of the manufacturing plant, line throughput, and energy intensity.',
}

export default function PlantOverviewPage() {
  return <PlantOverviewView />
}
