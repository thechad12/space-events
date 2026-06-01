import { format, parseISO } from 'date-fns'
import { X, Calendar, MapPin, Info, Eye } from 'lucide-react'
import { TYPE_CONFIG } from './EventCard'
import clsx from 'clsx'

const QUALITY_COLORS = {
  excellent: 'text-emerald-400 bg-emerald-400/10',
  good: 'text-sky-400 bg-sky-400/10',
  fair: 'text-amber-400 bg-amber-400/10',
  poor: 'text-red-400 bg-red-400/10',
}

export default function EventModal({ event, onClose }) {
  if (!event) return null

  const cfg = TYPE_CONFIG[event.type] ?? TYPE_CONFIG.planetary
  const Icon = cfg.icon
  const startDate = parseISO(event.start_date)
  const endDate = event.end_date ? parseISO(event.end_date) : null
  const peakDate = event.peak_date ? parseISO(event.peak_date) : null

  const details = Object.entries(event.details ?? {}).filter(
    ([k]) => !['source'].includes(k)
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className={clsx('relative glass border max-w-lg w-full shadow-2xl shadow-black/60', cfg.border)}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className={clsx('flex items-start gap-4 p-5 border-b border-white/10')}>
          <div className={clsx('p-3 rounded-xl', cfg.bg)}>
            <Icon className={clsx('w-6 h-6', cfg.color)} />
          </div>
          <div className="flex-1 min-w-0">
            <p className={clsx('text-xs font-medium mb-1', cfg.color)}>{cfg.label}</p>
            <h2 className="text-lg font-bold text-white leading-tight">{event.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors shrink-0"
          >
            <X className="w-4 h-4 text-white/50" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4 max-h-[60vh] overflow-y-auto">
          {/* Dates */}
          <div className="flex gap-4 flex-wrap">
            <div className="flex items-center gap-2 text-sm">
              <Calendar className="w-4 h-4 text-white/40" />
              <span className="text-white/60">
                {format(startDate, 'MMM d, yyyy')}
                {endDate && ` – ${format(endDate, 'MMM d')}`}
              </span>
            </div>
            {peakDate && (
              <div className="flex items-center gap-2 text-sm">
                <span className={clsx('w-2 h-2 rounded-full', cfg.dot.replace('bg-', 'bg-'))} />
                <span className="text-white/60">Peak: {format(peakDate, 'MMM d, yyyy')}</span>
              </div>
            )}
          </div>

          {/* Visibility badge */}
          <div className={clsx('flex items-start gap-3 p-3 rounded-lg', QUALITY_COLORS[event.visibility.quality])}>
            <Eye className="w-4 h-4 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-semibold capitalize">{event.visibility.quality} visibility</p>
              <p className="text-xs mt-0.5 opacity-80">{event.visibility.notes}</p>
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-2 flex items-center gap-1">
              <Info className="w-3 h-3" /> About
            </h3>
            <p className="text-sm text-white/70 leading-relaxed">{event.description}</p>
          </div>

          {/* Details */}
          {details.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-2">Details</h3>
              <div className="grid grid-cols-2 gap-2">
                {details.map(([key, value]) => (
                  <div key={key} className="glass-sm px-3 py-2">
                    <p className="text-xs text-white/40 capitalize">{key.replace(/_/g, ' ')}</p>
                    <p className="text-sm text-white/80 font-medium mt-0.5">{String(value)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
