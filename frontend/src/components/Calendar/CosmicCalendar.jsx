import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import listPlugin from '@fullcalendar/list'
import { useState } from 'react'
import EventModal from '../Events/EventModal'
import { TYPE_CONFIG } from '../Events/EventCard'

const TYPE_COLORS = {
  meteor_shower: '#f59e0b',
  lunar_eclipse: '#f87171',
  solar_eclipse: '#fbbf24',
  aurora: '#34d399',
  planetary: '#a78bfa',
  comet: '#22d3ee',
}

export default function CosmicCalendar({ events = [] }) {
  const [selected, setSelected] = useState(null)

  const calEvents = events.map((e) => ({
    id: e.id,
    title: e.name,
    start: e.peak_date ?? e.start_date,
    end: e.end_date,
    backgroundColor: `${TYPE_COLORS[e.type] ?? '#a78bfa'}33`,
    borderColor: TYPE_COLORS[e.type] ?? '#a78bfa',
    textColor: TYPE_COLORS[e.type] ?? '#a78bfa',
    extendedProps: { event: e },
  }))

  return (
    <div className="glass p-4 h-full">
      <FullCalendar
        plugins={[dayGridPlugin, listPlugin]}
        initialView="dayGridMonth"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,listMonth',
        }}
        events={calEvents}
        eventClick={(info) => setSelected(info.event.extendedProps.event)}
        height="100%"
        dayMaxEvents={3}
      />
      {selected && <EventModal event={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}
