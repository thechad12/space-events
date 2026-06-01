import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { locationsApi } from '../../api/locations'
import { useLocationStore } from '../../store/locationStore'
import { Search, Plus, Trash2, Star, Loader2, X } from 'lucide-react'
import clsx from 'clsx'

export default function LocationManager({ onClose }) {
  const qc = useQueryClient()
  const { locations, activeLocationId, setActiveLocation } = useLocationStore()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)

  const createMutation = useMutation({
    mutationFn: locationsApi.create,
    onSuccess: () => { qc.invalidateQueries(['locations']); setResults([]) },
  })

  const deleteMutation = useMutation({
    mutationFn: locationsApi.remove,
    onSuccess: () => qc.invalidateQueries(['locations']),
  })

  const setDefaultMutation = useMutation({
    mutationFn: ({ id }) => locationsApi.update(id, { is_default: true }),
    onSuccess: () => qc.invalidateQueries(['locations']),
  })

  async function handleSearch(e) {
    e.preventDefault()
    if (!query.trim()) return
    setSearching(true)
    try {
      const data = await locationsApi.geocode(query)
      setResults(data)
    } catch {
      setResults([])
    } finally {
      setSearching(false)
    }
  }

  function addLocation(r) {
    createMutation.mutate({
      name: r.name,
      lat: r.lat,
      lng: r.lng,
      is_default: locations.length === 0,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative glass max-w-md w-full shadow-2xl shadow-black/60"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-5 border-b border-white/10">
          <h2 className="text-base font-semibold">Manage Locations</h2>
          <button onClick={onClose} className="p-1.5 hover:bg-white/10 rounded-lg transition-colors">
            <X className="w-4 h-4 text-white/50" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              className="input flex-1"
              placeholder="Search city or place…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button type="submit" className="btn-primary px-3" disabled={searching}>
              {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            </button>
          </form>

          {/* Geocode results */}
          {results.length > 0 && (
            <div className="space-y-1">
              <p className="text-xs text-white/40 font-medium">Search results</p>
              {results.map((r, i) => (
                <div key={i} className="glass-sm flex items-center justify-between gap-3 px-3 py-2">
                  <p className="text-sm text-white/80 truncate flex-1">{r.display_name}</p>
                  <button
                    onClick={() => addLocation(r)}
                    disabled={createMutation.isPending}
                    className="shrink-0 p-1.5 hover:bg-nebula-purple/30 rounded text-nebula-purple transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Saved locations */}
          <div className="space-y-1">
            <p className="text-xs text-white/40 font-medium uppercase tracking-wider">Saved Locations</p>
            {locations.length === 0 && (
              <p className="text-sm text-white/30 py-3 text-center">No locations saved yet.</p>
            )}
            {locations.map((loc) => (
              <div
                key={loc.id}
                className={clsx(
                  'glass-sm flex items-center gap-3 px-3 py-2 cursor-pointer transition-colors',
                  loc.id === activeLocationId ? 'border-nebula-purple/40 bg-nebula-purple/5' : 'hover:bg-white/5'
                )}
                onClick={() => setActiveLocation(loc.id)}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white/90 truncate">{loc.name}</p>
                  <p className="text-xs text-white/30">
                    {loc.lat.toFixed(2)}, {loc.lng.toFixed(2)}
                    {loc.is_default && ' · default'}
                  </p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); setDefaultMutation.mutate({ id: loc.id }) }}
                  className={clsx('p-1.5 rounded transition-colors', loc.is_default ? 'text-amber-400' : 'text-white/20 hover:text-amber-400/60')}
                  title="Set as default"
                >
                  <Star className="w-3.5 h-3.5" fill={loc.is_default ? 'currentColor' : 'none'} />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(loc.id) }}
                  className="p-1.5 rounded text-white/20 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
