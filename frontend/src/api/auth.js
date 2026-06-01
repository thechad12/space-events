import client from './client'
import axios from 'axios'

export const authApi = {
  register: (data) => axios.post('/api/auth/register', data).then((r) => r.data),
  login: (data) => axios.post('/api/auth/login', data).then((r) => r.data),
  me: () => client.get('/auth/me').then((r) => r.data),
}
