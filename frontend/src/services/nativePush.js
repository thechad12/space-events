/**
 * Native push notifications via Capacitor + Firebase Cloud Messaging.
 * Only runs when the app is packaged with Capacitor (iOS/Android).
 * Falls back gracefully in the browser.
 */
import client from '../api/client'

export const isNative = () => typeof window !== 'undefined' && !!(window.Capacitor?.isNativePlatform?.())

export async function initNativePush() {
  if (!isNative()) return

  const { PushNotifications } = await import('@capacitor/push-notifications')

  const permResult = await PushNotifications.requestPermissions()
  if (permResult.receive !== 'granted') return

  await PushNotifications.register()

  PushNotifications.addListener('registration', async ({ value: fcmToken }) => {
    try {
      await client.post('/notifications/mobile-subscribe', {
        fcm_token: fcmToken,
        platform: window.Capacitor.getPlatform(),
      })
    } catch (err) {
      console.warn('FCM token registration failed:', err)
    }
  })

  PushNotifications.addListener('registrationError', (err) => {
    console.error('Push registration error:', err)
  })

  PushNotifications.addListener('pushNotificationReceived', (notification) => {
    console.log('Push received (foreground):', notification)
    // You can show an in-app banner here if desired
  })

  PushNotifications.addListener('pushNotificationActionPerformed', ({ notification }) => {
    const eventType = notification.data?.event_type
    if (eventType) {
      window.location.href = `/?filter=${eventType}`
    }
  })
}
