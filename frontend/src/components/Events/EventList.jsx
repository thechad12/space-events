import { useState, useMemo } from 'react'
import { isAfter, parseISO, startOfToday } from 'date-fns'
import EventCard from './EventCard'
import EventModal from './EventModal'
import { Loader2, SatelliteDish, Bookmark } from 'lucide-react'

const FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'bookmarked', label: 'Bookmarked' },
  { key: 'rocket_launch', label: 'Launches 🚀' },
  { key: 'meteor_shower', label: 'Meteors' },
  { key: 'lunar_eclipse', label: 'Lunar' },
  { key: 'solar_eclipse', label: 'Solar' },
  { key: 'aurora', label: 'Aurora' },
  { key: 'planetary', label: 'Planets' },
]

export default function EventList({ events = [], loading, error, bookmarkedIds = new Set(), seenIds = new Set() }) {
  const [selected, setSelected] = useState(null)
  const [filter, setFilter] = useState('all')
  const [showPast, setShowPast] = useState(false)

  const today = startOfToday()

  const visible = events
    .filter((e) => {
      if (filter === 'bookmarked') return bookmarkedIds.has(e.id)
      return filter === 'all' || e.type === filter
    })
    .filter((e) => showPast || !isAfter(today, parseISO(e.start_date)) || (e.end_date && isAfter(parseISO(e.end_date), today)))

  return (
    <div className="flex flex-col h-full">
      {/* Filter chips */}
      <div className="flex gap-2 pb-4 overflow-x-auto no-scrollbar shrink-0">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`shrink-0 px-3 py-1 rounded-full text-xs font-medium transition-all ${
              filter === f.key
                ? 'bg-nebula-purple text-white'
                : 'glass-sm text-white/60 hover:text-white hover:bg-white/10'
            }`}
          >
            {f.label}
          </button>
        ))}
        <button
          onClick={() => setShowPast((v) => !v)}
          className={`shrink-0 px-3 py-1 rounded-full text-xs font-medium transition-all ml-auto ${
            showPast ? 'bg-white/10 text-white' : 'glass-sm text-white/40 hover:text-white/60'
          }`}
        >
          {showPast ? 'Hide past' : 'Show past'}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 text-white/40">
            <Loader2 className="w-8 h-8 animate-spin mb-3" />
            <p className="text-sm">Scanning the cosmos…</p>
          </div>
        )}

        {error && (
          <div className="glass-sm border border-red-400/20 p-4 text-center">
            <p className="text-sm text-red-400">Failed to load events. Check your connection.</p>
          </div>
        )}

        {!loading && !error && visible.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-white/30">
            <SatelliteDish className="w-10 h-10 mb-3 opacity-50" />
            <p className="text-sm">No events found for this filter.</p>
          </div>
        )}

        {visible.map((event) => (
          <EventCard
            key={event.id}
            event={event}
            onClick={setSelected}
            bookmarkedIds={bookmarkedIds}
            seenIds={seenIds}
          />
        ))}
      </div>

      {selected && <EventModal event={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}
