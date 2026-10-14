import { spawnSync } from 'node:child_process'
import { join } from 'node:path'

import assert from 'node:assert/strict'
import test from 'node:test'

import { decideExit, extractReferencedAssets, runSmoke, summarize } from './runtime-smoke.mjs'

const FRONTEND_URL = 'http://localhost.test:8787'
const NOTES_URL = 'http://localhost.test:8787/notes'
const API_HEALTH_URL = 'http://127.0.0.1:8001/api/health'
const MAIN_ASSET_URL = 'http://localhost.test:8787/_next/static/chunks/main-a1b2.js'
const CSS_ASSET_URL = 'http://localhost.test:8787/_next/static/css/app-c3d4.css'
const FAVICON_URL = 'https://cdn.localhost.test/favicon.ico'

const HOME_HTML = [
	'<html>',
	'<head>',
	'<script src="/_next/static/chunks/main-a1b2.js" defer></script>',
	'<script src="/_next/static/chunks/main-a1b2.js" defer></script>',
	'<link rel="stylesheet" href="/_next/static/css/app-c3d4.css"/>',
	'<link rel="icon" href="https://cdn.localhost.test/favicon.ico"/>',
	'</head>',
	'<body></body>',
	'</html>',
].join('')

function createMockFetch(routes) {
	const calls = []
	const fetchImpl = async (url, init) => {
		calls.push({ url, init })
		const route = routes[url]
		if (!route) return { ok: false, status: 404, text: async () => '' }
		if (route.error) throw route.error
		const status = route.status ?? 200
		return { ok: status >= 200 && status < 300, status, text: async () => route.body ?? '' }
	}
	return { calls, fetchImpl }
}

function routesForHome(homeStatus = 200, homeBody = HOME_HTML) {
	return {
		[`${FRONTEND_URL}/`]: { status: homeStatus, body: homeBody },
		[MAIN_ASSET_URL]: { status: 200 },
		[CSS_ASSET_URL]: { status: 200 },
		[FAVICON_URL]: { status: 200 },
		[NOTES_URL]: { status: 200 },
		[API_HEALTH_URL]: { status: 200 },
	}
}

test('extractReferencedAssets collects script and link assets, resolves them, dedupes, and skips non-asset references', () => {
	const html = [
		'<html><head>',
		'<script src="/_next/static/chunks/main-a1b2.js" defer></script>',
		'<script src="chunks/lazy-e5f6.js"></script>',
		'<script src="https://cdn.example.com/analytics.js" async></script>',
		'<link rel="stylesheet" href="/_next/static/css/app-c3d4.css"/>',
		'<link rel="icon" href="/favicon.ico"/>',
		'<script src="/_next/static/chunks/main-a1b2.js"></script>',
		'<script src="data:text/javascript,console.log(1)"></script>',
		'<script src="blob:https://example.com/9f8e"></script>',
		'<script src="javascript:void(0)"></script>',
		'<link rel="author" href="mailto:team@example.com"/>',
		'<link rel="bookmark" href="#top"/>',
		'<img srcset="/hero.png 1x, /hero-2x.png 2x" src="/hero.png" alt="hero">',
		'</head><body></body></html>',
	].join('')

	assert.deepEqual(extractReferencedAssets(html, 'https://example.com/app/'), [
		'https://example.com/_next/static/chunks/main-a1b2.js',
		'https://example.com/app/chunks/lazy-e5f6.js',
		'https://cdn.example.com/analytics.js',
		'https://example.com/_next/static/css/app-c3d4.css',
		'https://example.com/favicon.ico',
	])
})

test('summarize counts ok and failed checks and collects reasons', () => {
	const results = [
		{ name: 'home', url: 'https://example.com/', ok: true, status: 200 },
		{ name: 'asset', url: 'https://example.com/a.js', ok: false, status: 404 },
		{ name: 'asset', url: 'https://example.com/b.js', ok: false, status: 0, error: 'timeout after 10000ms' },
	]

	assert.deepEqual(summarize(results), {
		total: 3,
		ok: 1,
		failed: 2,
		failures: [
			{ name: 'asset', url: 'https://example.com/a.js', reason: 'HTTP 404' },
			{ name: 'asset', url: 'https://example.com/b.js', reason: 'timeout after 10000ms' },
		],
		assets: { referenced: 2, ok: 0, failed: 2 },
	})
})

test('decideExit maps zero failures to exit 0 and any failure to exit 1', () => {
	assert.equal(decideExit({ total: 6, ok: 6, failed: 0, failures: [] }), 0)
	assert.equal(
		decideExit({
			total: 6,
			ok: 5,
			failed: 1,
			failures: [{ name: 'asset', url: 'https://example.com/a.js', reason: 'HTTP 404' }],
		}),
		1,
	)
})

test('runSmoke passes when the home page, referenced assets, notes, and api health all respond ok', async () => {
	const { calls, fetchImpl } = createMockFetch(routesForHome())

	const result = await runSmoke({ frontendUrl: FRONTEND_URL, apiHealthUrl: API_HEALTH_URL, fetchImpl })

	assert.deepEqual(
		result.checks.map(({ name }) => name),
		['home', 'asset', 'asset', 'asset', 'notes', 'api-health'],
	)
	assert.ok(result.checks.every(({ ok }) => ok))
	assert.equal(result.summary.total, 6)
	assert.equal(result.summary.ok, 6)
	assert.equal(result.summary.failed, 0)
	assert.deepEqual(result.summary.assets, { referenced: 3, ok: 3, failed: 0 })
	assert.equal(result.summary.total, result.summary.assets.referenced + 3)
	assert.deepEqual(result.summary.failures, [])
	assert.equal(decideExit(result.summary), 0)
	assert.deepEqual(
		calls.map(({ url }) => url),
		[`${FRONTEND_URL}/`, MAIN_ASSET_URL, CSS_ASSET_URL, FAVICON_URL, NOTES_URL, API_HEALTH_URL],
	)
	assert.ok(calls.every(({ init }) => init?.signal instanceof AbortSignal))
})

test('runSmoke fails with the offending asset url when a referenced asset returns 404', async () => {
	const routes = routesForHome()
	routes[MAIN_ASSET_URL] = { status: 404 }
	const { fetchImpl } = createMockFetch(routes)

	const result = await runSmoke({ frontendUrl: FRONTEND_URL, apiHealthUrl: API_HEALTH_URL, fetchImpl })

	assert.equal(result.summary.failed, 1)
	assert.equal(result.summary.ok, 5)
	assert.deepEqual(result.summary.assets, { referenced: 3, ok: 2, failed: 1 })
	assert.deepEqual(result.summary.failures, [{ name: 'asset', url: MAIN_ASSET_URL, reason: 'HTTP 404' }])
	assert.equal(result.checks.find(({ name }) => name === 'home').ok, true)
	assert.equal(result.checks.find(({ name }) => name === 'notes').ok, true)
	assert.equal(result.checks.find(({ name }) => name === 'api-health').ok, true)
	assert.equal(decideExit(result.summary), 1)
})

test('runSmoke fails and decides exit 1 when the api health probe returns 503', async () => {
	const routes = routesForHome()
	routes[API_HEALTH_URL] = { status: 503 }
	const { fetchImpl } = createMockFetch(routes)

	const result = await runSmoke({ frontendUrl: FRONTEND_URL, apiHealthUrl: API_HEALTH_URL, fetchImpl })

	assert.equal(decideExit(result.summary), 1)
})

test('extractReferencedAssets intentionally skips single-quoted and unquoted attributes', () => {
	const html = [
		"<script src='/_next/static/chunks/main-a1b2.js'></script>",
		'<script src=/_next/static/chunks/lazy-e5f6.js></script>',
		'<link rel=stylesheet href=/_next/static/css/app-c3d4.css>',
	].join('')

	assert.deepEqual(extractReferencedAssets(html, 'https://example.com/'), [])
})

test('extractReferencedAssets skips preconnect and dns-prefetch links but keeps stylesheet, icon, and preload links', () => {
	const html = [
		'<html><head>',
		'<link rel="preconnect" href="https://fonts.googleapis.cn/"/>',
		'<link rel="dns-prefetch" href="https://fonts.gstatic.cn/"/>',
		'<link rel="stylesheet" href="/_next/static/css/app-c3d4.css"/>',
		'<link rel="icon" href="/favicon.ico"/>',
		'<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin=""/>',
		'</head><body></body></html>',
	].join('')

	assert.deepEqual(extractReferencedAssets(html, 'https://example.com/'), [
		'https://example.com/_next/static/css/app-c3d4.css',
		'https://example.com/favicon.ico',
		'https://example.com/fonts/inter.woff2',
	])
})

test('extractReferencedAssets skips connection-hint rels case-insensitively across multiple rel tokens', () => {
	const html = [
		'<link rel="preconnect dns-prefetch" href="https://fonts.googleapis.cn/"/>',
		'<link rel="DNS-PREFETCH" href="https://fonts.gstatic.cn/"/>',
	].join('')

	assert.deepEqual(extractReferencedAssets(html, 'https://example.com/'), [])
})

test('extractReferencedAssets keeps a preload link even though rel starts with "pre"', () => {
	const html = '<link rel="preload" href="/_next/static/media/inter.woff2" as="font" crossorigin=""/>'

	assert.deepEqual(extractReferencedAssets(html, 'https://example.com/'), [
		'https://example.com/_next/static/media/inter.woff2',
	])
})

test('runSmoke fails and decides exit 1 when the notes page returns 404', async () => {
	const routes = routesForHome()
	routes[NOTES_URL] = { status: 404 }
	const { fetchImpl } = createMockFetch(routes)

	const result = await runSmoke({ frontendUrl: FRONTEND_URL, apiHealthUrl: API_HEALTH_URL, fetchImpl })

	assert.ok(result.summary.failed >= 1)
	assert.deepEqual(
		result.summary.failures.find(({ name }) => name === 'notes'),
		{ name: 'notes', url: NOTES_URL, reason: 'HTTP 404' },
	)
	assert.equal(decideExit(result.summary), 1)
})

test('runSmoke fetches an asset referenced with different fragments only once', async () => {
	const html = [
		'<html><head>',
		'<script src="/_next/static/chunks/main-a1b2.js"></script>',
		'<link rel="preload" href="/_next/static/chunks/main-a1b2.js#one"/>',
		'<link rel="preload" href="/_next/static/chunks/main-a1b2.js#two"/>',
		'</head><body></body></html>',
	].join('')
	const { calls, fetchImpl } = createMockFetch(routesForHome(200, html))

	const result = await runSmoke({ frontendUrl: FRONTEND_URL, apiHealthUrl: API_HEALTH_URL, fetchImpl })

	assert.deepEqual(result.summary.assets, { referenced: 1, ok: 1, failed: 0 })
	assert.equal(calls.filter(({ url }) => url === MAIN_ASSET_URL).length, 1)
	assert.equal(result.summary.failed, 0)
})

test('runSmoke records a network error as a failed check instead of throwing', async () => {
	const routes = routesForHome()
	routes[CSS_ASSET_URL] = { error: new Error('connection refused') }
	const { fetchImpl } = createMockFetch(routes)

	const result = await runSmoke({ frontendUrl: FRONTEND_URL, apiHealthUrl: API_HEALTH_URL, fetchImpl })

	assert.equal(result.summary.failed, 1)
	assert.deepEqual(result.summary.failures, [
		{ name: 'asset', url: CSS_ASSET_URL, reason: 'connection refused' },
	])
})

test('runSmoke skips asset requests when the home page itself fails', async () => {
	const { calls, fetchImpl } = createMockFetch(routesForHome(500, 'Internal Server Error'))

	const result = await runSmoke({ frontendUrl: FRONTEND_URL, apiHealthUrl: API_HEALTH_URL, fetchImpl })

	assert.equal(result.checks.find(({ name }) => name === 'home').ok, false)
	assert.ok(result.summary.failed >= 1)
	assert.ok(!calls.some(({ url }) => url === MAIN_ASSET_URL || url === CSS_ASSET_URL || url === FAVICON_URL))
})

test('CLI wiring exits 1 with SMOKE output when every check fails on a dead port', () => {
	const result = spawnSync(
		'node',
		[
			join(import.meta.dirname, 'runtime-smoke.mjs'),
			'--frontend-url',
			'http://127.0.0.1:1',
			'--api-health-url',
			'http://127.0.0.1:1/api/health',
			'--timeout',
			'1500',
		],
		{ encoding: 'utf8', timeout: 15000 },
	)

	assert.equal(result.status, 1)
	const output = `${result.stdout ?? ''}${result.stderr ?? ''}`
	assert.ok(output.includes('SMOKE referenced=0 ok=0 failed=0 checks=3 failed=3'))
	assert.match(output, /SMOKE_JSON/)
})
