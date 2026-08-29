import { defineConfig, devices } from '@playwright/test'
import { resolve } from 'node:path'

export default defineConfig({
	testDir: '.',
	outputDir: resolve(__dirname, '../../../../docs/workflows/markdown-special-adapter-enablement/assets/playwright-test-results'),
	fullyParallel: false,
	forbidOnly: true,
	reporter: 'line',
	use: {
		...devices['Desktop Chrome'],
		headless: true,
		trace: 'retain-on-failure',
		screenshot: 'only-on-failure',
		video: 'off'
	},
	webServer: {
		command: 'node ./node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4179',
		cwd: resolve(__dirname, '../../../..'),
		port: 4179,
		reuseExistingServer: false
	}
})
