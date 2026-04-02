const CACHE_NAME = 'astrolabe-offline-v1';
      self.addEventListener('install', event => {
          event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.add('./')));
      });
      self.addEventListener('fetch', event => {
          event.respondWith(caches.match(event.request).then(res => res || fetch(event.request)));
      });
