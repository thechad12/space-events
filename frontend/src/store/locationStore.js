import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useLocationStore = create(
  persist(
    (set, get) => ({
      locations: [],
      activeLocationId: null,
      setLocations: (locations) => {
        const active = get().activeLocationId
        const defaultLoc = locations.find((l) => l.is_default)
        set({
          locations,
          activeLocationId: active && locations.find((l) => l.id === active)
            ? active
            : defaultLoc?.id ?? locations[0]?.id ?? null,
        })
      },
      setActiveLocation: (id) => set({ activeLocationId: id }),
      getActiveLocation: () => {
        const { locations, activeLocationId } = get()
        return locations.find((l) => l.id === activeLocationId) ?? locations[0] ?? null
      },
    }),
    { name: 'cosmic-locations' }
  )
)
