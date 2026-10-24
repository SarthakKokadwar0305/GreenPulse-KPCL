import { EnergyTrendChart } from './energy-trend-chart'
import { MachineEnergyChart } from './machine-energy-chart'

export function EnergyOverviewSection() {
  return (
    <section
      aria-label="Energy overview"
      className="grid grid-cols-1 gap-4 xl:grid-cols-5"
    >
      <div className="xl:col-span-3">
        <EnergyTrendChart />
      </div>
      <div className="xl:col-span-2">
        <MachineEnergyChart />
      </div>
    </section>
  )
}
