import client from './client'

export const eventsApi = {
  getEvents: (params) => client.get('/events', { params }).then((r) => r.data),
}
