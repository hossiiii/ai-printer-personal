// Service Worker for AI Printer PWA
const CACHE_NAME = 'ai-printer-v2.0.0';
const API_CACHE_NAME = 'ai-printer-api-v2.0.0';
const STATIC_CACHE_NAME = 'ai-printer-static-v2.0.0';

// URLs to cache
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
  'https://fonts.googleapis.com/icon?family=Material+Icons'
];

// API endpoints to cache
const apiEndpoints = [
  '/api/health',
  '/api/templates',
  '/api/user/profile'
];

// Install event - cache static resources
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    Promise.all([
      // Cache static resources
      caches.open(STATIC_CACHE_NAME).then((cache) => {
        console.log('[SW] Caching static resources');
        return cache.addAll(urlsToCache);
      }),
      
      // Cache API responses
      caches.open(API_CACHE_NAME).then((cache) => {
        console.log('[SW] Pre-caching API endpoints');
        return Promise.all(
          apiEndpoints.map(endpoint => {
            return fetch(endpoint)
              .then(response => {
                if (response.ok) {
                  return cache.put(endpoint, response.clone());
                }
              })
              .catch(err => console.log(`[SW] Failed to cache ${endpoint}:`, err));
          })
        );
      })
    ]).then(() => {
      console.log('[SW] Installation complete');
      // Force activation of new service worker
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && 
              cacheName !== API_CACHE_NAME && 
              cacheName !== STATIC_CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[SW] Activation complete');
      // Take control of all clients immediately
      return self.clients.claim();
    })
  );
});

// Fetch event - handle network requests with caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests and chrome-extension URLs
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }
  
  // Handle different types of requests with appropriate strategies
  if (url.pathname.startsWith('/api/')) {
    // API requests: Network-first with cache fallback
    event.respondWith(handleApiRequest(request));
  } else if (isStaticAsset(url.pathname)) {
    // Static assets: Cache-first strategy
    event.respondWith(handleStaticAsset(request));
  } else {
    // Navigation requests: Stale-while-revalidate
    event.respondWith(handleNavigationRequest(request));
  }
});

// Handle API requests with network-first strategy
async function handleApiRequest(request) {
  const url = request.url;
  
  try {
    // Try network first
    const networkResponse = await fetch(request.clone());
    
    if (networkResponse.ok) {
      // Cache successful responses (except POST/PUT/DELETE)
      if (request.method === 'GET') {
        const cache = await caches.open(API_CACHE_NAME);
        await cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    } else {
      throw new Error(`Network response not ok: ${networkResponse.status}`);
    }
  } catch (error) {
    console.log('[SW] Network request failed, trying cache:', url);
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // If no cache, return offline response for certain endpoints
    if (url.includes('/api/')) {
      return new Response(JSON.stringify({
        error: 'Offline',
        message: 'This feature requires an internet connection'
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    throw error;
  }
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME);
      await cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Failed to fetch static asset:', request.url);
    throw error;
  }
}

// Handle navigation requests with stale-while-revalidate
async function handleNavigationRequest(request) {
  const cachedResponse = await caches.match(request);
  
  // Return cached version immediately if available
  if (cachedResponse) {
    // Update cache in background
    fetch(request).then(response => {
      if (response.ok) {
        const cache = caches.open(CACHE_NAME);
        cache.then(c => c.put(request, response));
      }
    }).catch(err => console.log('[SW] Background update failed:', err));
    
    return cachedResponse;
  }
  
  // No cache, try network
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      await cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Return offline page or app shell
    const offlineResponse = await caches.match('/');
    if (offlineResponse) {
      return offlineResponse;
    }
    
    throw error;
  }
}

// Check if URL is a static asset
function isStaticAsset(pathname) {
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2'];
  return staticExtensions.some(ext => pathname.endsWith(ext)) || 
         pathname.startsWith('/static/') ||
         pathname.startsWith('/icons/');
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'upload-audio') {
    event.waitUntil(syncAudioUploads());
  } else if (event.tag === 'save-document') {
    event.waitUntil(syncDocumentSaves());
  }
});

// Sync audio uploads when back online
async function syncAudioUploads() {
  try {
    // Get pending uploads from IndexedDB
    const pendingUploads = await getPendingUploads();
    
    for (const upload of pendingUploads) {
      try {
        const formData = new FormData();
        formData.append('audio', upload.audioBlob);
        formData.append('filename', upload.filename);
        
        const response = await fetch('/api/transcribe', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          // Remove from pending uploads
          await removePendingUpload(upload.id);
          
          // Notify client of successful sync
          const clients = await self.clients.matchAll();
          clients.forEach(client => {
            client.postMessage({
              type: 'SYNC_SUCCESS',
              data: { uploadId: upload.id }
            });
          });
        }
      } catch (error) {
        console.log('[SW] Failed to sync upload:', error);
      }
    }
  } catch (error) {
    console.log('[SW] Background sync failed:', error);
  }
}

// Sync document saves when back online
async function syncDocumentSaves() {
  // Similar implementation for document saves
  console.log('[SW] Syncing document saves...');
}

// IndexedDB helpers (simplified - in production you'd use a library like idb)
async function getPendingUploads() {
  // Return array of pending uploads from IndexedDB
  return [];
}

async function removePendingUpload(id) {
  // Remove upload from IndexedDB
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('[SW] Push message received');
  
  const options = {
    body: 'Your document has been processed!',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'view',
        title: 'View Document',
        icon: '/icons/view-icon.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/close-icon.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('AI Printer', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification click received');
  
  event.notification.close();
  
  if (event.action === 'view') {
    // Open app to document
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Message handling from main thread
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data && event.data.type === 'CACHE_AUDIO') {
    // Cache audio file for offline use
    cacheAudioFile(event.data.audioUrl);
  }
});

// Cache audio file
async function cacheAudioFile(audioUrl) {
  try {
    const cache = await caches.open(API_CACHE_NAME);
    await cache.add(audioUrl);
    console.log('[SW] Audio file cached:', audioUrl);
  } catch (error) {
    console.log('[SW] Failed to cache audio file:', error);
  }
}