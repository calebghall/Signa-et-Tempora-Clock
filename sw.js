const CACHE_NAME = 's&t-clock-v1'; 
const CACHE_ASSETS = [
    './',
    'index.html',
    'js/lib/tz-lookup/tz.js' 
];

// SW saves cached version
self.addEventListener('install', event => {
    // Forces the new SW to become active immediately
    self.skipWaiting(); 
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
              return cache.addAll(CACHE_ASSETS);
        })
    );
});

// Clean up old versions
self.addEventListener('activate', event => {
    event.waitUntil(self.clients.claim());
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.map(key => {
                if (key !== CACHE_NAME) return caches.delete(key);
            })
        ))
    );
});

// Sticks with cached version / Offline support
// Downloads new site ONLY when version changes
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            // If it's in the cache, return it immediately (NO network request)
            if (cachedResponse) {
                return cachedResponse;
            }
            // Otherwise, go to the network
            return fetch(event.request);
        })
    );
});
