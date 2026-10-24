import type { Metadata } from 'next'

import { RecommendationCenterView } from '@/components/modules/recommendation-center/recommendation-center-view'

export const metadata: Metadata = {
  title: 'Recommendation Center | GreenPulse AI',
  description: 'AI-generated energy conservation measures (ECMs), load shifting strategies, and ROI analytics.',
}

export default function RecommendationCenterPage() {
  return <RecommendationCenterView />
}
