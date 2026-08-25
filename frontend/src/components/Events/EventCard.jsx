import { format, parseISO } from 'date-fns'
import { Zap, Moon, Sun, Wind, Globe, Telescope, Star, Rocket } from 'lucide-react'
import clsx from 'clsx'

const TYPE_CONFIG = {
  rocket_launch: {
    icon: Rocket,
    color: 'text-sky-400',
    bg: 'bg-sky-400/10',
    border: 'border-sky-400/20',
    dot: 'bg-sky-400',
    label: 'Rocket Launch',
  },
  meteor_shower: {
    icon: Star,
    color: 'text-amber-400',
    bg: 'bg-amber-400/10',
    border: 'border-amber-400/20',
    dot: 'bg-amber-400',
    label: 'Meteor Shower',
  },
  lunar_eclipse: {
    icon: Moon,
    color: 'text-red-400',
    bg: 'bg-red-400/10',
    border: 'border-red-400/20',
    dot: 'bg-red-400',
    label: 'Lunar Eclipse',
  },
  solar_eclipse: {
    icon: Sun,
    color: 'text-yellow-400',
    bg: 'bg-yellow-400/10',
    border: 'border-yellow-400/20',
    dot: 'bg-yellow-400',
    label: 'Solar Eclipse',
  },
  aurora: {
    icon: Wind,
    color: 'text-emerald-400',
    bg: 'bg-emerald-400/10',
    border: 'border-emerald-400/20',
    dot: 'bg-emerald-400',
    label: 'Aurora',
  },
  planetary: {
    icon: Globe,
    color: 'text-violet-400',
    bg: 'bg-violet-400/10',
    border: 'border-violet-400/20',
    dot: 'bg-violet-400',
    label: 'Planetary',
  },
  comet: {
    icon: Zap,
    color: 'text-cyan-400',
    bg: 'bg-cyan-400/10',
    border: 'border-cyan-400/20',
    dot: 'bg-cyan-400',
    label: 'Comet',
  },
}

const QUALITY_COLORS = {
  excellent: 'text-emerald-400',
  good: 'text-sky-400',
  fair: 'text-amber-400',
  poor: 'text-red-400/70',
}

export default function EventCard({ event, onClick }) {
  const cfg = TYPE_CONFIG[event.type] ?? TYPE_CONFIG.planetary
  const Icon = cfg.icon
  const startDate = parseISO(event.start_date)
  const peakDate = event.peak_date ? parseISO(event.peak_date) : null

  return (
    <button
      onClick={() => onClick?.(event)}
      className={clsx(
        'w-full text-left glass-sm border hover:bg-white/8 transition-all duration-200 p-4 group hover:scale-[1.01]',
        cfg.border,
        !event.visibility.visible && 'opacity-60'
      )}
    >
      <div className="flex items-start gap-3">
        <div className={clsx('p-2 rounded-lg shrink-0', cfg.bg)}>
          <Icon className={clsx('w-4 h-4', cfg.color)} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className={clsx('text-xs font-medium mb-0.5', cfg.color)}>{cfg.label}</p>
              <h3 className="text-sm font-semibold text-white leading-tight group-hover:text-white/90">
                {event.name}
              </h3>
            </div>
            <div className="text-right shrink-0">
              <p className="text-xs text-white/40">{format(startDate, 'MMM d')}</p>
              <p className="text-xs text-white/30">{format(startDate, 'h:mm a')}</p>
              {peakDate && event.type !== 'rocket_launch' && (
                <p className="text-xs text-white/30">Peak {format(peakDate, 'MMM d')}</p>
              )}
            </div>
          </div>

          <p className="text-xs text-white/50 mt-1.5 line-clamp-2 leading-relaxed">
            {event.description}
          </p>

          <div className="flex items-center gap-3 mt-2">
            <span className={clsx('text-xs font-medium capitalize', QUALITY_COLORS[event.visibility.quality])}>
              {event.visibility.visible ? `${event.visibility.quality} visibility` : 'Not visible'}
            </span>
            {event.details?.peak_rate && (
              <span className="text-xs text-white/30">~{event.details.peak_rate}/hr</span>
            )}
            {event.details?.magnitude !== undefined && (
              <span className="text-xs text-white/30">mag {event.details.magnitude}</span>
            )}
            {event.details?.distance_km !== undefined && (
              <span className="text-xs text-white/30">{event.details.distance_km} km away</span>
            )}
            {event.details?.trajectory_corridor && (
              <span className="text-xs text-sky-400/60">in trajectory corridor</span>
            )}
          </div>
        </div>
      </div>
    </button>
  )
}

export { TYPE_CONFIG }
