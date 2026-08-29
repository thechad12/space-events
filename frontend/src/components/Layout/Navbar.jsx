import { Link } from 'react-router-dom'
import { LogOut, Telescope, MapPin, ChevronDown } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'
import { useLocationStore } from '../../store/locationStore'
import { useTenantStore } from '../../store/tenantStore'
import { NotificationBell } from '../Notifications/NotificationPanel'
import NotificationPanel from '../Notifications/NotificationPanel'
import { getCurrentSubscription, getPermissionStatus } from '../../services/notifications'

export default function Navbar({ onAddLocation }) {
  const logout = useAuthStore((s) => s.logout)
  const user = useAuthStore((s) => s.user)
  const { locations, activeLocationId, setActiveLocation } = useLocationStore()
  const tenant = useTenantStore((s) => s.tenant)
  const [open, setOpen] = useState(false)
  const [showNotifPanel, setShowNotifPanel] = useState(false)
  const [isSubscribed, setIsSubscribed] = useState(false)
  const active = locations.find((l) => l.id === activeLocationId)

  useEffect(() => {
    if (getPermissionStatus() === 'granted') {
      getCurrentSubscription().then((sub) => setIsSubscribed(!!sub))
    }
  }, [])

  return (
    <>
      <nav className="relative z-20 flex items-center justify-between px-6 py-4 border-b border-white/10 glass-sm rounded-none">
        <Link to="/" className="flex items-center gap-2">
          {tenant.logo_url ? (
            <img src={tenant.logo_url} alt={tenant.brand_name} className="h-8 w-auto max-w-[120px] object-contain" />
          ) : (
            <>
              <div className="w-8 h-8 rounded-full bg-nebula-purple/30 flex items-center justify-center">
                <Telescope className="w-4 h-4 text-nebula-purple" />
              </div>
              <span className="text-lg font-semibold tracking-tight">
                {tenant.is_white_label
                  ? <span style={{ color: tenant.primary_color }}>{tenant.brand_name}</span>
                  : <>Look <span className="text-nebula-purple">Up!</span></>
                }
              </span>
            </>
          )}
        </Link>

        <div className="flex items-center gap-2">
          {/* Location switcher */}
          <div className="relative">
            <button
              onClick={() => setOpen((o) => !o)}
              className="flex items-center gap-2 px-3 py-1.5 glass-sm hover:bg-white/10 transition-colors text-sm"
            >
              <MapPin className="w-3.5 h-3.5 text-nebula-purple" />
              <span className="max-w-[140px] truncate">{active?.name ?? 'Select location'}</span>
              <ChevronDown className="w-3.5 h-3.5 text-white/50" />
            </button>

            {open && (
              <div className="absolute right-0 top-full mt-1 w-56 glass shadow-xl shadow-black/50 py-1 z-50">
                {locations.map((loc) => (
                  <button
                    key={loc.id}
                    onClick={() => { setActiveLocation(loc.id); setOpen(false) }}
                    className={`w-full text-left px-3 py-2 text-sm hover:bg-white/10 transition-colors flex items-center gap-2 ${
                      loc.id === activeLocationId ? 'text-nebula-purple' : 'text-white/80'
                    }`}
                  >
                    <MapPin className="w-3 h-3 shrink-0" />
                    <span className="truncate">{loc.name}</span>
                    {loc.is_default && <span className="ml-auto text-xs text-white/30">default</span>}
                  </button>
                ))}
                <div className="border-t border-white/10 mt-1 pt-1">
                  <button
                    onClick={() => { onAddLocation?.(); setOpen(false) }}
                    className="w-full text-left px-3 py-2 text-sm text-nebula-purple hover:bg-white/10 transition-colors"
                  >
                    + Add location
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Notification bell */}
          <NotificationBell
            isSubscribed={isSubscribed}
            onClick={() => setShowNotifPanel(true)}
          />

          {/* User / logout */}
          <div className="flex items-center gap-2">
            {user?.display_name && (
              <span className="text-sm text-white/50 hidden sm:block">{user.display_name}</span>
            )}
            <button
              onClick={logout}
              className="p-2 glass-sm hover:bg-white/10 transition-colors rounded-lg"
              title="Sign out"
            >
              <LogOut className="w-4 h-4 text-white/60" />
            </button>
          </div>
        </div>
      </nav>

      {showNotifPanel && (
        <NotificationPanel
          onClose={() => setShowNotifPanel(false)}
        />
      )}
    </>
  )
}
