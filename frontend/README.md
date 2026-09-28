# React checkout

Start Django on port 8000 first. Then, from this directory:

```sh
npm ci
npm run dev
```

Open http://localhost:5173. Vite forwards `/api` to Django, so there are no browser secrets or separate CORS settings to configure. No frontend `.env` is required.

```sh
npm run lint
npm run build
npm run preview
```

Preview uses the same API proxy and requires Django to keep running. Vite preview is a local preview server, not production hosting.

The supported app lives in `src/checkout`, with routes in `src/App.jsx`. Older auth and payment prototypes remain in `src/components` and `src/pages` as reference code and are not part of the new UI. ESLint checks the active app. Use the committed npm lockfile and `npm ci` for reproducible installs.

```sh
npx playwright install chromium
npm test
```

Browser tests need the root `.venv` and start both servers themselves. Stop existing servers on 8000 and 5173 first. They force mock mode, exercise all gateways on desktop and mobile, and use a separate database. [Testing notes](../docs/testing.md).
