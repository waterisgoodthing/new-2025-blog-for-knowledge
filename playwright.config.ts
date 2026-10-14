import { defineConfig, devices } from '@playwright/test'

const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:8787'

// Local same-site runs: without editing /etc/hosts, map the CI hostnames to
// loopback inside Chromium only. `app.ci.test` and `api.ci.test` share the
// registrable domain `ci.test`, so the SameSite=Lax `admin_session` cookie is
// still sent (the reason the CI topology uses these hosts at all).
const resolveHosts = process.env.E2E_RESOLVE_HOSTS === '1'
const hostResolverArgs = resolveHosts
  ? [
      '--host-resolver-rules=MAP api.ci.test 127.0.0.1, MAP app.ci.test 127.0.0.1',
      '--no-proxy-server',
    ]
  : []

// F04 globalSetup seeds the deterministic R22b business data. E2E_SKIP_SEED=1
// disables it for runs that do not need a backend (e.g. E2E-05 alone).
const skipSeed = process.env.E2E_SKIP_SEED === '1'

export default defineConfig({
  testDir: './tests/e2e',
  globalSetup: skipSeed ? undefined : './tests/e2e/global-setup.ts',
  fullyParallel: false,
  workers: 1,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: { args: hostResolverArgs },
      },
    },
  ],
})
