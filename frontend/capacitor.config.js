/** @type {import('@capacitor/cli').CapacitorConfig} */
const config = {
  appId: 'com.cosmicevents.app',
  appName: 'Cosmic Events',
  webDir: 'dist',
  server: {
    // In production the app uses the bundled build.
    // For local dev against a running backend, uncomment and set:
    // url: 'http://localhost:3000',
    // cleartext: true,
  },
  plugins: {
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    SplashScreen: {
      launchShowDuration: 500,
      backgroundColor: '#04040f',
      showSpinner: false,
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#04040f',
    },
  },
  ios: {
    contentInset: 'always',
  },
}

module.exports = config
