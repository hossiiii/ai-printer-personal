/**
 * Custom hook for PWA functionality
 */
import { useState, useEffect, useCallback } from 'react';

interface PWAInstallPrompt extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface PWAHook {
  isInstallable: boolean;
  isInstalled: boolean;
  isOnline: boolean;
  promptInstall: () => Promise<void>;
  isUpdateAvailable: boolean;
  updateApp: () => void;
}

export const usePWA = (): PWAHook => {
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [installPrompt, setInstallPrompt] = useState<PWAInstallPrompt | null>(null);
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [waitingServiceWorker, setWaitingServiceWorker] = useState<ServiceWorker | null>(null);

  // Check if app is installed
  useEffect(() => {
    const checkInstalled = () => {
      // Check if app is running in standalone mode
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                          (window.navigator as any).standalone ||
                          document.referrer.includes('android-app://');
      setIsInstalled(isStandalone);
    };

    checkInstalled();

    // Listen for display mode changes
    const mediaQuery = window.matchMedia('(display-mode: standalone)');
    mediaQuery.addEventListener('change', checkInstalled);

    return () => mediaQuery.removeEventListener('change', checkInstalled);
  }, []);

  // Handle install prompt
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as PWAInstallPrompt);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      setIsInstallable(false);
      setIsInstalled(true);
      setInstallPrompt(null);
      console.log('PWA was installed');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Handle online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Service Worker registration and updates
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration);

          // Check for updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  setIsUpdateAvailable(true);
                  setWaitingServiceWorker(newWorker);
                }
              });
            }
          });
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error);
        });

      // Listen for service worker messages
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'SYNC_SUCCESS') {
          console.log('Background sync completed:', event.data);
          // You can dispatch custom events here to update UI
        }
      });
    }
  }, []);

  // Prompt user to install app
  const promptInstall = useCallback(async () => {
    if (!installPrompt) {
      throw new Error('Install prompt not available');
    }

    try {
      await installPrompt.prompt();
      const choiceResult = await installPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      
      setInstallPrompt(null);
      setIsInstallable(false);
    } catch (error) {
      console.error('Install prompt failed:', error);
    }
  }, [installPrompt]);

  // Update app to new version
  const updateApp = useCallback(() => {
    if (waitingServiceWorker) {
      waitingServiceWorker.postMessage({ type: 'SKIP_WAITING' });
      window.location.reload();
    }
  }, [waitingServiceWorker]);

  return {
    isInstallable,
    isInstalled,
    isOnline,
    promptInstall,
    isUpdateAvailable,
    updateApp,
  };
};

// Hook for background sync
export const useBackgroundSync = () => {
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype);
  }, []);

  const requestSync = useCallback(async (tag: string) => {
    if (!isSupported) {
      console.log('Background sync not supported');
      return false;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register(tag);
      console.log(`Background sync registered: ${tag}`);
      return true;
    } catch (error) {
      console.error('Background sync registration failed:', error);
      return false;
    }
  }, [isSupported]);

  return {
    isSupported,
    requestSync,
  };
};

// Hook for push notifications
export const usePushNotifications = () => {
  const [isSupported, setIsSupported] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [subscription, setSubscription] = useState<PushSubscription | null>(null);

  useEffect(() => {
    setIsSupported('Notification' in window && 'PushManager' in window);
    setPermission(Notification.permission);
  }, []);

  const requestPermission = useCallback(async () => {
    if (!isSupported) {
      throw new Error('Push notifications not supported');
    }

    const permission = await Notification.requestPermission();
    setPermission(permission);
    return permission;
  }, [isSupported]);

  const subscribe = useCallback(async (vapidPublicKey: string) => {
    if (!isSupported || permission !== 'granted') {
      throw new Error('Push notifications not available');
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: vapidPublicKey,
      });

      setSubscription(subscription);
      return subscription;
    } catch (error) {
      console.error('Push subscription failed:', error);
      throw error;
    }
  }, [isSupported, permission]);

  const unsubscribe = useCallback(async () => {
    if (subscription) {
      await subscription.unsubscribe();
      setSubscription(null);
    }
  }, [subscription]);

  return {
    isSupported,
    permission,
    subscription,
    requestPermission,
    subscribe,
    unsubscribe,
  };
};

// Hook for offline storage
export const useOfflineStorage = () => {
  const storeOfflineData = useCallback(async (key: string, data: any) => {
    try {
      localStorage.setItem(`offline_${key}`, JSON.stringify({
        data,
        timestamp: Date.now(),
      }));
      return true;
    } catch (error) {
      console.error('Failed to store offline data:', error);
      return false;
    }
  }, []);

  const getOfflineData = useCallback((key: string) => {
    try {
      const stored = localStorage.getItem(`offline_${key}`);
      if (stored) {
        return JSON.parse(stored);
      }
      return null;
    } catch (error) {
      console.error('Failed to retrieve offline data:', error);
      return null;
    }
  }, []);

  const clearOfflineData = useCallback((key: string) => {
    try {
      localStorage.removeItem(`offline_${key}`);
      return true;
    } catch (error) {
      console.error('Failed to clear offline data:', error);
      return false;
    }
  }, []);

  return {
    storeOfflineData,
    getOfflineData,
    clearOfflineData,
  };
};