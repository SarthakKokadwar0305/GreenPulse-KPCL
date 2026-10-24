import type { Metadata } from 'next'

import { CopilotView } from '@/components/modules/copilot/copilot-view'

export const metadata: Metadata = {
  title: 'AI Copilot & Knowledge Assistant | GreenPulse AI',
  description:
    'Industrial AI Copilot powered by Gemma 3 4B Instruct, Qdrant vector retrieval, and live factory SCADA Modbus telemetry.',
}

export default function CopilotPage() {
  return <CopilotView />
}
