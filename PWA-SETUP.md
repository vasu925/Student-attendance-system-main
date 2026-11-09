# Student Attendance PWA

This Flask project exposes a web app manifest at `/manifest.json` and a root-scoped service worker at `/sw.js`. The service worker caches static assets only. Authenticated pages and attendance records are always requested from the server.

## Verify after deployment
1. Deploy this branch to a host that runs Flask and can connect to the configured MySQL database.
2. Confirm `https://YOUR-DOMAIN/manifest.json` returns the manifest.
3. Confirm `https://YOUR-DOMAIN/sw.js` returns JavaScript.
4. Open the HTTPS site in Chrome on Android and choose Install app / Add to Home screen.
5. Enter the HTTPS site URL in PWABuilder and review its validation report before packaging.

## Hosting note
This repository contains a Flask backend. A static-only Vercel deployment cannot run Flask routes or connect to MySQL by itself. Keep `SECRET_KEY` and `DATABASE_URL` in the server's environment variables, never in source control. Check hosting compatibility before changing production deployment.
