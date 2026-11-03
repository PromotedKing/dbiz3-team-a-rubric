/* Offline: the shell comes from the cache; a page that cannot load shows the error state of the UI conventions (§13). */
const CACHE = "mb360-v1";
const SHELL = ["/static/tci.css", "/static/app.js", "/static/icon.svg", "/static/offline.html"];

self.addEventListener("install", (e) => e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener("activate", (e) => e.waitUntil(caches.keys().then((keys) =>
  Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  if (e.request.mode === "navigate") {
    e.respondWith(fetch(e.request).catch(() => caches.match("/static/offline.html")));
  } else if (new URL(e.request.url).pathname.startsWith("/static/")) {
    e.respondWith(fetch(e.request).then((r) => {
      const copy = r.clone();
      caches.open(CACHE).then((c) => c.put(e.request, copy));
      return r;
    }).catch(() => caches.match(e.request)));
  }
});
