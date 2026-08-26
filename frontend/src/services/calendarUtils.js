// ─── iCal helpers ────────────────────────────────────────────────────────────

function toIcsDatetime(isoString) {
  if (!isoString) return null
  // Accepts "2026-08-12T02:00:00", "+00:00", or "Z" variants
  const clean = isoString
    .replace(/\.\d+/, '')      // strip ms
    .replace('+00:00', 'Z')
    .replace(/[-:]/g, '')
  // Ensure trailing Z for UTC; leave bare if local/floating
  return clean.endsWith('Z') ? clean : clean + 'Z'
}

function escapeIcs(str) {
  return String(str ?? '')
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\n/g, '\\n')
}

function buildDescription(event) {
  const parts = []
  if (event.description) parts.push(event.description)
  if (event.visibility?.notes) parts.push(`Viewing notes: ${event.visibility.notes}`)
  if (event.details?.viewing_tip) parts.push(`Tip: ${event.details.viewing_tip}`)
  if (event.details?.source_body) parts.push(`Source: ${event.details.source_body}`)
  if (event.details?.peak_rate) parts.push(`Peak rate: ~${event.details.peak_rate} meteors/hr`)
  if (event.details?.rocket) parts.push(`Vehicle: ${event.details.rocket}`)
  if (event.details?.launch_site) parts.push(`Launch site: ${event.details.launch_site}`)
  if (event.details?.distance_km) parts.push(`Distance from you: ${event.details.distance_km} km`)
  return parts.join('\n\n')
}

export function downloadIcs(event) {
  const start = toIcsDatetime(event.start_date)
  const end = toIcsDatetime(event.end_date || event.start_date)
  const desc = buildDescription(event)

  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Look Up!//EN',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'BEGIN:VEVENT',
    `UID:${event.id}@lookupapp.app`,
    `DTSTART:${start}`,
    `DTEND:${end}`,
    `SUMMARY:${escapeIcs(event.name)}`,
    `DESCRIPTION:${escapeIcs(desc)}`,
    'END:VEVENT',
    'END:VCALENDAR',
  ]

  const blob = new Blob([lines.join('\r\n')], { type: 'text/calendar;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${event.name.replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '_')}.ics`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// ─── Google Calendar ──────────────────────────────────────────────────────────

function toGoogleDatetime(isoString) {
  return toIcsDatetime(isoString) // same compact UTC format
}

export function getGoogleCalendarUrl(event) {
  const desc = buildDescription(event)
  const params = new URLSearchParams({
    action: 'TEMPLATE',
    text: event.name,
    dates: `${toGoogleDatetime(event.start_date)}/${toGoogleDatetime(event.end_date || event.start_date)}`,
    details: desc,
  })
  return `https://calendar.google.com/calendar/render?${params.toString()}`
}

// ─── Outlook.com ──────────────────────────────────────────────────────────────

export function getOutlookUrl(event) {
  const desc = buildDescription(event)
  const params = new URLSearchParams({
    path: '/calendar/action/compose',
    rru: 'addevent',
    subject: event.name,
    startdt: event.start_date,
    enddt: event.end_date || event.start_date,
    body: desc,
  })
  return `https://outlook.live.com/calendar/0/deeplink/compose?${params.toString()}`
}
