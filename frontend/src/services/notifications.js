import client from '../api/client'

const SW_PATH = '/sw.js'

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)))
}

export async function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) throw new Error('Service workers not supported')
  return navigator.serviceWorker.register(SW_PATH)
}

export async function getVapidPublicKey() {
  const { data } = await client.get('/notifications/vapid-public-key')
  return data.public_key
}

export async function subscribeToPush(notifyHoursBefore = 24) {
  const reg = await registerServiceWorker()
  await navigator.serviceWorker.ready

  const vapidKey = await getVapidPublicKey()
  const applicationServerKey = urlBase64ToUint8Array(vapidKey)

  const subscription = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey,
  })

  const json = subscription.toJSON()
  await client.post('/notifications/subscribe', {
    endpoint: json.endpoint,
    keys: { p256dh: json.keys.p256dh, auth: json.keys.auth },
    notify_hours_before: notifyHoursBefore,
  })

  return subscription
}

export async function unsubscribeFromPush() {
  const reg = await navigator.serviceWorker.getRegistration(SW_PATH)
  if (!reg) return

  const sub = await reg.pushManager.getSubscription()
  if (!sub) return

  await client.delete('/notifications/unsubscribe', { params: { endpoint: sub.endpoint } })
  await sub.unsubscribe()
}

export async function getCurrentSubscription() {
  if (!('serviceWorker' in navigator)) return null
  const reg = await navigator.serviceWorker.getRegistration(SW_PATH)
  if (!reg) return null
  return reg.pushManager.getSubscription()
}

export function getPermissionStatus() {
  if (!('Notification' in window)) return 'unsupported'
  return Notification.permission // 'default' | 'granted' | 'denied'
}
