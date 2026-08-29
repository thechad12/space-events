import client from './client'

export const bookmarksApi = {
  list: () => client.get('/bookmarks').then((r) => r.data),

  add: (event) =>
    client
      .post('/bookmarks', {
        event_id: event.id,
        event_type: event.type,
        event_name: event.name,
        event_date: event.start_date,
      })
      .then((r) => r.data),

  remove: (eventId) => client.delete(`/bookmarks/${eventId}`),
}

export const seenApi = {
  list: () => client.get('/seen').then((r) => r.data),
  markSeen: (eventIds) => client.post('/seen', { event_ids: eventIds }),
}
