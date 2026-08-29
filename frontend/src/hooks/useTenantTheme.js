import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { tenantApi } from '../api/tenant'
import { useTenantStore } from '../store/tenantStore'

function hexToRgb(hex) {
  const h = hex.replace('#', '')
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  return `${r}, ${g}, ${b}`
}

function injectTheme(color) {
  const root = document.documentElement
  root.style.setProperty('--brand-primary', color)
  root.style.setProperty('--brand-primary-rgb', hexToRgb(color))

  // Override Tailwind's compiled nebula-purple classes at runtime
  let style = document.getElementById('tenant-theme')
  if (!style) {
    style = document.createElement('style')
    style.id = 'tenant-theme'
    document.head.appendChild(style)
  }
  style.textContent = `
    .text-nebula-purple  { color: ${color} !important; }
    .bg-nebula-purple    { background-color: ${color} !important; }
    .border-nebula-purple { border-color: ${color} !important; }
    .bg-nebula-purple\\/10  { background-color: rgba(${hexToRgb(color)}, 0.1) !important; }
    .bg-nebula-purple\\/20  { background-color: rgba(${hexToRgb(color)}, 0.2) !important; }
    .bg-nebula-purple\\/30  { background-color: rgba(${hexToRgb(color)}, 0.3) !important; }
    .border-nebula-purple\\/30 { border-color: rgba(${hexToRgb(color)}, 0.3) !important; }
    .border-nebula-purple\\/50 { border-color: rgba(${hexToRgb(color)}, 0.5) !important; }
    .ring-nebula-purple\\/50 { --tw-ring-color: rgba(${hexToRgb(color)}, 0.5) !important; }
    .focus\\:ring-nebula-purple\\/50:focus { --tw-ring-color: rgba(${hexToRgb(color)}, 0.5) !important; }
    .focus\\:border-nebula-purple\\/50:focus { border-color: rgba(${hexToRgb(color)}, 0.5) !important; }
    .hover\\:bg-violet-600:hover { background-color: ${color} !important; filter: brightness(1.1); }
    .fc { --fc-button-bg-color: rgba(${hexToRgb(color)}, 0.3) !important;
          --fc-button-hover-bg-color: rgba(${hexToRgb(color)}, 0.5) !important;
          --fc-button-active-bg-color: rgba(${hexToRgb(color)}, 0.7) !important; }
  `
}

export function useTenantTheme() {
  const setTenant = useTenantStore((s) => s.setTenant)
  const hostname = window.location.hostname

  const { data } = useQuery({
    queryKey: ['tenant', hostname],
    queryFn: () => tenantApi.get(hostname),
    staleTime: Infinity,  // tenant config is stable for the session
    retry: false,
  })

  useEffect(() => {
    if (!data) return
    setTenant(data)
    injectTheme(data.primary_color)
    if (data.brand_name) document.title = data.brand_name
  }, [data])

  return data
}
