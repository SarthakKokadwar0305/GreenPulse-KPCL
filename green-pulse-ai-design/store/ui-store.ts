import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

interface UiState {
  sidebarCollapsed: boolean
  mobileNavOpen: boolean
  selectedPlantId: string | null
  toggleSidebar: () => void
  setMobileNavOpen: (open: boolean) => void
  selectPlant: (plantId: string) => void
}

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      mobileNavOpen: false,
      selectedPlantId: null,
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setMobileNavOpen: (open) => set({ mobileNavOpen: open }),
      selectPlant: (plantId) => set({ selectedPlantId: plantId }),
    }),
    {
      name: 'greenpulse-ui',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        selectedPlantId: state.selectedPlantId,
      }),
      skipHydration: true,
    },
  ),
)
