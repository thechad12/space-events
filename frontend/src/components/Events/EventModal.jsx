import { format, parseISO } from 'date-fns'
import { X, Calendar, Info, Eye, Clock, Navigation, Zap } from 'lucide-react'
import { TYPE_CONFIG } from './EventCard'
import { downloadIcs, getGoogleCalendarUrl, getOutlookUrl } from '../../services/calendarUtils'
import clsx from 'clsx'

const QUALITY_COLORS = {
  excellent: 'text-emerald-400 bg-emerald-400/10',
  good: 'text-sky-400 bg-sky-400/10',
  fair: 'text-amber-400 bg-amber-400/10',
  poor: 'text-red-400 bg-red-400/10',
}

// Keys shown in the Details grid — readable label overrides
const DETAIL_LABELS = {
  peak_rate: 'Peak rate',
  radiant: 'Radiant',
  radiant_direction: 'Direction to face',
  best_viewing_time: 'Best viewing time',
  speed_kms: 'Meteor speed (km/s)',
  source_body: 'Source',
  rocket: 'Vehicle',
  mission: 'Mission',
  orbit: 'Orbit',
  launch_site: 'Launch site',
  launch_site_location: 'Launch location',
  status: 'Status',
  distance_km: 'Distance from you',
  max_kp: 'Max Kp index',
  min_kp_needed: 'Min Kp needed',
  storm_level: 'Storm level',
}

// Keys to exclude from the Details grid
const HIDDEN_DETAIL_KEYS = new Set([
  'source', 'hemisphere', 'trajectory_corridor', 'window_start', 'window_end',
  'viewing_tip', 'launch_site_lat', 'launch_site_lng',
])

function DetailValue({ k, v }) {
  if (k === 'peak_rate') return <>{v} meteors/hr</>
  if (k === 'speed_kms') return <>{v} km/s</>
  if (k === 'distance_km') return <>{Number(v).toLocaleString()} km</>
  return <>{String(v)}</>
}

export default function EventModal({ event, onClose }) {
  if (!event) return null

  const cfg = TYPE_CONFIG[event.type] ?? TYPE_CONFIG.planetary
  const Icon = cfg.icon
  const startDate = parseISO(event.start_date)
  const endDate = event.end_date ? parseISO(event.end_date) : null
  const peakDate = event.peak_date ? parseISO(event.peak_date) : null

  const viewingTip = event.details?.viewing_tip

  const details = Object.entries(event.details ?? {}).filter(
    ([k, v]) => !HIDDEN_DETAIL_KEYS.has(k) && v !== null && v !== undefined && v !== ''
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className={clsx('relative glass border max-w-lg w-full shadow-2xl shadow-black/60 flex flex-col max-h-[90vh]', cfg.border)}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start gap-4 p-5 border-b border-white/10 shrink-0">
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
        <div className="p-5 space-y-4 overflow-y-auto flex-1">

          {/* Dates */}
          <div className="flex gap-4 flex-wrap text-sm">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-white/40" />
              <span className="text-white/60">
                {format(startDate, 'MMM d, yyyy')}
                {endDate && ` – ${format(endDate, 'MMM d, yyyy')}`}
              </span>
            </div>
            {peakDate && (
              <div className="flex items-center gap-2">
                <span className={clsx('w-2 h-2 rounded-full shrink-0', cfg.dot)} />
                <span className="text-white/60">Peak: {format(peakDate, 'MMM d, yyyy')}</span>
              </div>
            )}
          </div>

          {/* Visibility */}
          <div className={clsx('flex items-start gap-3 p-3 rounded-lg', QUALITY_COLORS[event.visibility.quality])}>
            <Eye className="w-4 h-4 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-semibold capitalize">{event.visibility.quality} visibility</p>
              <p className="text-xs mt-0.5 opacity-80 leading-relaxed">{event.visibility.notes}</p>
            </div>
          </div>

          {/* About */}
          <div>
            <SectionHeading icon={<Info className="w-3 h-3" />} label="About" />
            <p className="text-sm text-white/70 leading-relaxed">{event.description}</p>
          </div>

          {/* How to observe */}
          {viewingTip && (
            <div>
              <SectionHeading icon={<Navigation className="w-3 h-3" />} label="How to Observe" />
              <p className="text-sm text-white/70 leading-relaxed">{viewingTip}</p>
              {event.details?.best_viewing_time && (
                <div className="flex items-center gap-2 mt-2 text-xs text-white/50">
                  <Clock className="w-3 h-3" />
                  <span>Best window: {event.details.best_viewing_time} local time</span>
                </div>
              )}
            </div>
          )}

          {/* Details grid */}
          {details.length > 0 && (
            <div>
              <SectionHeading icon={<Zap className="w-3 h-3" />} label="Details" />
              <div className="grid grid-cols-2 gap-2">
                {details.map(([k, v]) => (
                  <div key={k} className="glass-sm px-3 py-2">
                    <p className="text-xs text-white/40">{DETAIL_LABELS[k] ?? k.replace(/_/g, ' ')}</p>
                    <p className="text-sm text-white/80 font-medium mt-0.5">
                      <DetailValue k={k} v={v} />
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Add to Calendar */}
          <div>
            <SectionHeading icon={<Calendar className="w-3 h-3" />} label="Add to Calendar" />
            <div className="flex gap-2 flex-wrap">
              <a
                href={getGoogleCalendarUrl(event)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-3 py-2 glass-sm border border-white/10 hover:border-white/20 hover:bg-white/8 transition-all text-xs text-white/70 hover:text-white rounded-lg"
              >
                <GoogleIcon />
                Google Calendar
              </a>
              <a
                href={getOutlookUrl(event)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-3 py-2 glass-sm border border-white/10 hover:border-white/20 hover:bg-white/8 transition-all text-xs text-white/70 hover:text-white rounded-lg"
              >
                <OutlookIcon />
                Outlook
              </a>
              <button
                onClick={() => downloadIcs(event)}
                className="flex items-center gap-2 px-3 py-2 glass-sm border border-white/10 hover:border-white/20 hover:bg-white/8 transition-all text-xs text-white/70 hover:text-white rounded-lg"
              >
                <Calendar className="w-3.5 h-3.5" />
                Apple / iCal (.ics)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function SectionHeading({ icon, label }) {
  return (
    <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-2 flex items-center gap-1">
      {icon} {label}
    </h3>
  )
}

function GoogleIcon() {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 11v2.4h3.97c-.16 1.03-1.2 3.02-3.97 3.02-2.39 0-4.34-1.98-4.34-4.42s1.95-4.42 4.34-4.42c1.36 0 2.27.58 2.79 1.08l1.9-1.83C15.47 5.69 13.89 5 12 5c-3.87 0-7 3.13-7 7s3.13 7 7 7c4.04 0 6.72-2.84 6.72-6.84 0-.46-.05-.81-.11-1.16H12z"/>
    </svg>
  )
}

function OutlookIcon() {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M7 6h10v2H7V6zm0 4h10v2H7v-2zm0 4h7v2H7v-2zM3 3h18v18H3V3zm2 2v14h14V5H5z"/>
    </svg>
  )
}
