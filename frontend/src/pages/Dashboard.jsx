import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { eventsApi } from '../api/events'
import { locationsApi } from '../api/locations'
import { authApi } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import { useLocationStore } from '../store/locationStore'
import StarField from '../components/Layout/StarField'
import Navbar from '../components/Layout/Navbar'
import EventList from '../components/Events/EventList'
import CosmicCalendar from '../components/Calendar/CosmicCalendar'
import LocationManager from '../components/Location/LocationManager'
import { LayoutList, CalendarDays, MapPin } from 'lucide-react'

export default function Dashboard() {
  const [view, setView] = useState('list')
  const [showLocMgr, setShowLocMgr] = useState(false)
  const { setUser } = useAuthStore()
  const { setLocations, getActiveLocation } = useLocationStore()

  // Bootstrap user
  useEffect(() => {
    authApi.me().then(setUser).catch(() => {})
  }, [])

  // Load locations
  const locationsQuery = useQuery({
    queryKey: ['locations'],
    queryFn: locationsApi.list,
    onSuccess: setLocations,
  })

  useEffect(() => {
    if (locationsQuery.data) setLocations(locationsQuery.data)
  }, [locationsQuery.data])

  const activeLoc = getActiveLocation()

  // Load events for active location
  const eventsQuery = useQuery({
    queryKey: ['events', activeLoc?.id],
    queryFn: () =>
      eventsApi.getEvents({
        lat: activeLoc.lat,
        lng: activeLoc.lng,
        location_name: activeLoc.name,
      }),
    enabled: !!activeLoc,
    staleTime: 10 * 60 * 1000,
  })

  const events = eventsQuery.data?.events ?? []

  return (
    <div className="min-h-screen bg-space-gradient relative">
      <StarField />

      <div className="relative z-10 flex flex-col h-screen">
        <Navbar onAddLocation={() => setShowLocMgr(true)} />

        <main className="flex-1 overflow-hidden flex flex-col">
          {/* Sub-header */}
          <div className="flex items-center justify-between px-6 py-3 border-b border-white/5">
            <div className="flex items-center gap-2 text-sm text-white/50">
              {activeLoc ? (
                <>
                  <MapPin className="w-3.5 h-3.5" />
                  <span>{activeLoc.name}</span>
                  <span className="text-white/20">
                    ({activeLoc.lat.toFixed(1)}°, {activeLoc.lng.toFixed(1)}°)
                  </span>
                </>
              ) : (
                <button
                  onClick={() => setShowLocMgr(true)}
                  className="text-nebula-purple hover:text-violet-400 transition-colors flex items-center gap-1"
                >
                  <MapPin className="w-3.5 h-3.5" />
                  Add your first location to get started
                </button>
              )}
            </div>

            {/* View toggle */}
            <div className="flex items-center gap-1 glass-sm p-1">
              <button
                onClick={() => setView('list')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${
                  view === 'list' ? 'bg-nebula-purple text-white' : 'text-white/50 hover:text-white'
                }`}
              >
                <LayoutList className="w-3.5 h-3.5" />
                List
              </button>
              <button
                onClick={() => setView('calendar')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${
                  view === 'calendar' ? 'bg-nebula-purple text-white' : 'text-white/50 hover:text-white'
                }`}
              >
                <CalendarDays className="w-3.5 h-3.5" />
                Calendar
              </button>
            </div>
          </div>

          {/* Content area */}
          <div className="flex-1 overflow-hidden p-6">
            {!activeLoc ? (
              <div className="flex flex-col items-center justify-center h-full text-white/30">
                <MapPin className="w-12 h-12 mb-4 opacity-30" />
                <p className="text-lg font-medium">No location selected</p>
                <p className="text-sm mt-1">Add a location to see cosmic events near you.</p>
                <button
                  onClick={() => setShowLocMgr(true)}
                  className="btn-primary mt-6"
                >
                  Add Location
                </button>
              </div>
            ) : view === 'list' ? (
              <EventList
                events={events}
                loading={eventsQuery.isLoading}
                error={eventsQuery.isError}
              />
            ) : (
              <CosmicCalendar events={events} />
            )}
          </div>
        </main>
      </div>

      {showLocMgr && <LocationManager onClose={() => setShowLocMgr(false)} />}
    </div>
  )
}
