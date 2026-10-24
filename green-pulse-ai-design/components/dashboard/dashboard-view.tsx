import { AlertsPanel } from './alerts-panel'
import { DashboardHeader } from './dashboard-header'
import { EnergyOverviewSection } from './energy-overview-section'
import { InsightsPanel } from './insights-panel'
import { KpiSection } from './kpi-section'
import { MachineSection } from './machine-section'
import { PlantStatusSection } from './plant-status-section'
import { QuickActionsSection } from './quick-actions-section'
import { RecentEventsPanel } from './recent-events-panel'

export function DashboardView() {
  return (
    <div className="flex flex-col gap-8">
      <DashboardHeader />
      <KpiSection />
      <PlantStatusSection />
      <MachineSection />
      <EnergyOverviewSection />
      <section
        aria-label="Intelligence and activity"
        className="grid grid-cols-1 gap-4 xl:grid-cols-3"
      >
        <div className="xl:col-span-2">
          <InsightsPanel />
        </div>
        <RecentEventsPanel />
      </section>
      <AlertsPanel />
      <QuickActionsSection />
    </div>
  )
}
