import { create } from 'zustand'

const DEFAULT_TENANT = {
  brand_name: 'Look Up!',
  logo_url: null,
  primary_color: '#7c3aed',
  property_name: null,
  default_lat: null,
  default_lng: null,
  show_notifications: true,
  show_ar_mode: true,
  is_white_label: false,
}

export const useTenantStore = create((set) => ({
  tenant: DEFAULT_TENANT,
  setTenant: (tenant) => set({ tenant }),
}))
