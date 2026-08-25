import { useState, useEffect } from 'react'
import { Bell, BellOff, X, Check, AlertCircle, Loader2 } from 'lucide-react'
import {
  subscribeToPush,
  unsubscribeFromPush,
  getCurrentSubscription,
  getPermissionStatus,
} from '../../services/notifications'
import clsx from 'clsx'

const ADVANCE_OPTIONS = [
  { value: 2, label: '2 hours before' },
  { value: 6, label: '6 hours before' },
  { value: 24, label: '1 day before' },
  { value: 48, label: '2 days before' },
]

export function NotificationBell({ onClick, isSubscribed }) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'relative p-2 rounded-lg transition-colors',
        isSubscribed
          ? 'text-nebula-purple hover:bg-nebula-purple/20'
          : 'text-white/40 hover:text-white/70 hover:bg-white/10'
      )}
      title={isSubscribed ? 'Notifications on' : 'Enable notifications'}
    >
      {isSubscribed ? <Bell className="w-4 h-4" fill="currentColor" /> : <BellOff className="w-4 h-4" />}
      {isSubscribed && (
        <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-nebula-purple animate-pulse-slow" />
      )}
    </button>
  )
}

export default function NotificationPanel({ onClose }) {
  const [status, setStatus] = useState('idle') // idle | loading | subscribed | error | denied | unsupported
  const [advanceHours, setAdvanceHours] = useState(24)
  const [message, setMessage] = useState('')

  useEffect(() => {
    const perm = getPermissionStatus()
    if (perm === 'unsupported') { setStatus('unsupported'); return }
    if (perm === 'denied') { setStatus('denied'); return }

    getCurrentSubscription().then((sub) => {
      setStatus(sub ? 'subscribed' : 'idle')
    })
  }, [])

  async function handleEnable() {
    setStatus('loading')
    try {
      await subscribeToPush(advanceHours)
      setStatus('subscribed')
      setMessage('Notifications enabled! We\'ll alert you when events are visible from your locations.')
    } catch (err) {
      if (Notification.permission === 'denied') {
        setStatus('denied')
      } else {
        setStatus('error')
        setMessage(err.message ?? 'Failed to enable notifications.')
      }
    }
  }

  async function handleDisable() {
    setStatus('loading')
    try {
      await unsubscribeFromPush()
      setStatus('idle')
      setMessage('')
    } catch {
      setStatus('error')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative glass max-w-sm w-full shadow-2xl shadow-black/60 border border-nebula-purple/20"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-5 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-nebula-purple" />
            <h2 className="text-base font-semibold">Event Notifications</h2>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-white/10 rounded-lg transition-colors">
            <X className="w-4 h-4 text-white/50" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {status === 'unsupported' && (
            <StatusBanner icon={<AlertCircle />} color="amber" text="Push notifications are not supported in this browser." />
          )}

          {status === 'denied' && (
            <StatusBanner
              icon={<AlertCircle />}
              color="red"
              text="Notification permission was denied. Please enable notifications for this site in your browser settings."
            />
          )}

          {status === 'subscribed' && (
            <>
              <StatusBanner icon={<Check />} color="emerald" text="You're subscribed. We'll notify you when events are visible from your saved locations." />
              {message && <p className="text-xs text-white/50">{message}</p>}
              <button onClick={handleDisable} className="w-full py-2 glass-sm border border-red-400/20 text-red-400 text-sm rounded-lg hover:bg-red-400/10 transition-colors flex items-center justify-center gap-2">
                <BellOff className="w-4 h-4" /> Disable notifications
              </button>
            </>
          )}

          {(status === 'idle' || status === 'error') && (
            <>
              <p className="text-sm text-white/60">
                Get push notifications when rocket launches, auroras, meteor showers, and eclipses are visible from your saved locations.
              </p>

              <div>
                <label className="text-xs font-medium text-white/40 block mb-2">Notify me</label>
                <div className="grid grid-cols-2 gap-2">
                  {ADVANCE_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setAdvanceHours(opt.value)}
                      className={clsx(
                        'py-2 px-3 rounded-lg text-sm transition-all border',
                        advanceHours === opt.value
                          ? 'bg-nebula-purple/20 border-nebula-purple/50 text-white'
                          : 'border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'
                      )}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              {status === 'error' && message && (
                <p className="text-xs text-red-400">{message}</p>
              )}

              <button
                onClick={handleEnable}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <Bell className="w-4 h-4" /> Enable Notifications
              </button>
            </>
          )}

          {status === 'loading' && (
            <div className="flex items-center justify-center py-6">
              <Loader2 className="w-6 h-6 animate-spin text-nebula-purple" />
            </div>
          )}

          <p className="text-xs text-white/30 text-center">
            Notifications are sent via your browser. No account email is used.
          </p>
        </div>
      </div>
    </div>
  )
}

function StatusBanner({ icon, color, text }) {
  const colors = {
    emerald: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
    amber: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    red: 'text-red-400 bg-red-400/10 border-red-400/20',
  }
  return (
    <div className={clsx('flex items-start gap-3 p-3 rounded-lg border text-sm', colors[color])}>
      <span className="shrink-0 w-4 h-4 mt-0.5">{icon}</span>
      <p>{text}</p>
    </div>
  )
}
