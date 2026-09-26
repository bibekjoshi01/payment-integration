import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  reporter: "list",
  use: { baseURL: "http://localhost:5173", trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: [
    {
      command:
        "../.venv/bin/python ../dj_server/manage.py migrate --noinput && ../.venv/bin/python ../dj_server/manage.py runserver 127.0.0.1:8000 --noreload",
      url: "http://127.0.0.1:8000/api/checkout/config",
      env: {
        PAYMENT_MODE: "mock",
        PAYMENT_DB_NAME: "browser-test.sqlite3",
        DJANGO_ALLOWED_HOSTS: "localhost,127.0.0.1",
      },
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --host localhost",
      url: "http://localhost:5173",
      reuseExistingServer: false,
    },
  ],
});
