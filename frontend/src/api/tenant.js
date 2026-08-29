import client from './client'

export const tenantApi = {
  get: (hostname) =>
    client.get('/tenant', { params: { host: hostname } }).then((r) => r.data),
}
