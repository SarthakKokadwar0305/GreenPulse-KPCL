import type { Metadata } from 'next'

import { AiForecastView } from '@/components/modules/ai-forecast-center/ai-forecast-view'

export const metadata: Metadata = {
  title: 'AI Forecast Center | GreenPulse AI',
  description: 'Machine learning energy demand, cost, and peak load multi-horizon forecasts.',
}

export default function AiForecastPage() {
  return <AiForecastView />
}
