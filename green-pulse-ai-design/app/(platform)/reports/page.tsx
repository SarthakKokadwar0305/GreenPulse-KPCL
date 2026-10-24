import type { Metadata } from 'next'

import { ReportsView } from '@/components/modules/reports/reports-view'

export const metadata: Metadata = {
  title: 'Reports & ESG Filings | GreenPulse AI',
  description: 'Industrial energy audits, GHG Protocol Scope 1/2 compliance packs, and scheduled PDF reporting.',
}

export default function ReportsPage() {
  return <ReportsView />
}
