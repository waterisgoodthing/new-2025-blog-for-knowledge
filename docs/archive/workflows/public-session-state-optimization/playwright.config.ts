import { defineConfig, devices } from '@playwright/test'
import { resolve } from 'node:path'

const root = resolve(__dirname, '../../..')

export default defineConfig({
	testDir: resolve(root, 'src/app'),
	testMatch: 'public-session-state.browser.spec.ts',
	outputDir: resolve(__dirname, 'assets/playwright-test-results'),
	fullyParallel: false,
	forbidOnly: true,
	reporter: 'line',
	use: {
		...devices['Desktop Chrome'],
		baseURL: 'http://127.0.0.1:3000',
		headless: true,
		trace: 'retain-on-failure',
		screenshot: 'only-on-failure',
		video: 'off'
	},
	webServer: [
		{
			command: 'PYTHONPATH=. .venv/bin/python -m uvicorn tests.pss_browser_harness:app --host 127.0.0.1 --port 8001 --lifespan off',
			cwd: resolve(root, 'backend'),
			port: 8001,
			reuseExistingServer: false
		},
		{
			command: 'NEXT_PUBLIC_API_URL=http://127.0.0.1:8001 node node_modules/next/dist/bin/next dev --hostname 127.0.0.1 --port 3000',
			cwd: root,
			port: 3000,
			reuseExistingServer: false
		}
	]
})
