const CACHE_NAME = "student-attendance-static-v1";
const APP_SHELL = ["/static/style.css", "/static/icons/icon.svg"];
self.addEventListener("install", (event) => { event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))); self.skipWaiting(); });
self.addEventListener("activate", (event) => { event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(caches.match(request).then((cached) => cached || fetch(request).then((response) => { if (response.ok) caches.open(CACHE_NAME).then((cache) => cache.put(request, response.clone())); return response; })));
  } else {
    // Authenticated pages and attendance records are never cached.
    event.respondWith(fetch(request));
  }
});
