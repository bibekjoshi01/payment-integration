# React frontend

Start the Django backend on port 8000, then run from this directory:

```sh
npm ci
npm run dev
```

Open **http://localhost:5173**. No frontend API keys or `.env` file are needed.

## Test and build

```sh
npm run lint
npm run build
npx playwright install chromium  # Download once
npm test
```

Browser tests require the root `.venv`. Stop running servers on ports 8000 and 5173 first; tests start their own servers.

To preview the build, run `npm run preview` with Django running.

See [testing and troubleshooting](../docs/testing.md) and [architecture](../docs/architecture.md).
