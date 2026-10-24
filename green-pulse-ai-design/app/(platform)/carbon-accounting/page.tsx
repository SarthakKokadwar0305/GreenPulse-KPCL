import type { Metadata } from 'next'

import { CarbonAccountingView } from '@/components/modules/carbon-accounting/carbon-accounting-view'

export const metadata: Metadata = {
  title: 'Carbon Accounting | GreenPulse AI',
  description: 'GHG Protocol Scope 1 and Scope 2 carbon accounting and decarbonization tracking.',
}

export default function CarbonAccountingPage() {
  return <CarbonAccountingView />
}
