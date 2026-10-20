import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const DEFAULT_FRONTEND_URL = 'http://localhost:8787'
const DEFAULT_API_HEALTH_URL = 'http://127.0.0.1:8001/api/health'
const DEFAULT_TIMEOUT_MS = 10000
const DEFAULT_CONCURRENCY = 6

const SKIPPED_PROTOCOLS = new Set(['data:', 'blob:', 'javascript:', 'mailto:'])

// Extraction boundary: double-quoted attributes only (matches Next.js/React build output).
// Known non-goals: single-quoted/unquoted attributes, '>' inside attribute values, and srcset.
// The dedupe key strips the URL fragment so the same asset is fetched once.
// <link rel="preconnect|dns-prefetch"> hrefs are excluded: connection hints, not fetched
// subresources, so a bare-origin GET is a guaranteed false 404.
const ASSET_TAG_PATTERN = /<(script|link)\b[^>]*>/gi
const SCRIPT_SRC_PATTERN = /\ssrc="([^"]*)"/i
const LINK_HREF_PATTERN = /\shref="([^"]*)"/i
const LINK_REL_PATTERN = /\srel="([^"]*)"/i
const CONNECTION_HINT_RELS = new Set(['preconnect', 'dns-prefetch'])

export function extractReferencedAssets(html, baseUrl) {
	const base = new URL(baseUrl)
	const assets = []
	const seen = new Set()
	for (const tag of html.matchAll(ASSET_TAG_PATTERN)) {
		const isScript = tag[1].toLowerCase() === 'script'
		if (!isScript) {
			const relMatch = tag[0].match(LINK_REL_PATTERN)
			const relTokens = relMatch ? relMatch[1].trim().toLowerCase().split(/\s+/) : []
			if (relTokens.some((token) => CONNECTION_HINT_RELS.has(token))) continue
		}
		const attributePattern = isScript ? SCRIPT_SRC_PATTERN : LINK_HREF_PATTERN
		const attributeMatch = tag[0].match(attributePattern)
		if (!attributeMatch) continue
		const reference = attributeMatch[1].trim()
		if (!reference || reference.startsWith('#')) continue
		let url
		try {
			url = new URL(reference, base)
		} catch {
			continue
		}
		if (SKIPPED_PROTOCOLS.has(url.protocol)) continue
		if (url.protocol !== 'http:' && url.protocol !== 'https:') continue
		const dedupeKey = `${url.origin}${url.pathname}${url.search}`
		if (seen.has(dedupeKey)) continue
		seen.add(dedupeKey)
		assets.push(url.href)
	}
	return assets
}

export function summarize(results) {
	const failures = []
	let assetReferenced = 0
	let assetOk = 0
	for (const result of results) {
		if (result.name === 'asset') {
			assetReferenced += 1
			if (result.ok) assetOk += 1
		}
		if (result.ok) continue
		failures.push({
			name: result.name,
			url: result.url,
			reason: result.error ?? `HTTP ${result.status ?? 0}`,
		})
	}
	return {
		total: results.length,
		ok: results.length - failures.length,
		failed: failures.length,
		failures,
		assets: { referenced: assetReferenced, ok: assetOk, failed: assetReferenced - assetOk },
	}
}

export function decideExit(summary) {
	return summary.failed === 0 ? 0 : 1
}

async function mapWithConcurrency(items, concurrency, worker) {
	const results = new Array(items.length)
	let cursor = 0
	const workerCount = Math.max(1, Math.min(concurrency, items.length))
	const runners = Array.from({ length: workerCount }, async () => {
		while (cursor < items.length) {
			const index = cursor
			cursor += 1
			results[index] = await worker(items[index], index)
		}
	})
	await Promise.all(runners)
	return results
}

async function performCheck({ name, url, fetchImpl, timeoutMs, readText = false }) {
	const controller = new AbortController()
	const timer = setTimeout(() => controller.abort(new Error(`timeout after ${timeoutMs}ms`)), timeoutMs)
	try {
		const response = await fetchImpl(url, { signal: controller.signal, redirect: 'follow' })
		const status = typeof response.status === 'number' ? response.status : 0
		const ok = response.ok === true
		if (!ok) {
			return { check: { name, url, ok, status, error: `HTTP ${status}` }, text: '' }
		}
		const text = readText ? await response.text() : ''
		return { check: { name, url, ok, status }, text }
	} catch (error) {
		return {
			check: { name, url, ok: false, status: 0, error: error?.message ?? String(error) },
			text: '',
		}
	} finally {
		clearTimeout(timer)
	}
}

export async function runSmoke({
	frontendUrl,
	apiHealthUrl,
	timeoutMs = DEFAULT_TIMEOUT_MS,
	concurrency = DEFAULT_CONCURRENCY,
	fetchImpl = globalThis.fetch,
}) {
	const frontend = new URL(frontendUrl).href
	const notesUrl = new URL('/notes', frontend).href
	const healthUrl = new URL(apiHealthUrl).href

	const home = await performCheck({ name: 'home', url: frontend, fetchImpl, timeoutMs, readText: true })
	const checks = [home.check]

	if (home.check.ok) {
		const assets = extractReferencedAssets(home.text, frontend)
		const assetChecks = await mapWithConcurrency(assets, concurrency, async (url) => {
			const { check } = await performCheck({ name: 'asset', url, fetchImpl, timeoutMs })
			return check
		})
		checks.push(...assetChecks)
	}

	const notes = await performCheck({ name: 'notes', url: notesUrl, fetchImpl, timeoutMs })
	checks.push(notes.check)

	const apiHealth = await performCheck({ name: 'api-health', url: healthUrl, fetchImpl, timeoutMs })
	checks.push(apiHealth.check)

	return { checks, summary: summarize(checks) }
}

function parseUrl(value, flag) {
	try {
		return new URL(value).href
	} catch {
		throw new Error(`${flag} expects an absolute URL, got "${value}"`)
	}
}

function parseTimeout(value, flag) {
	const parsed = Number(value)
	if (!Number.isFinite(parsed) || parsed <= 0) {
		throw new Error(`${flag} expects a positive number of milliseconds, got "${value}"`)
	}
	return parsed
}

function parseCount(value, flag) {
	const parsed = Number(value)
	if (!Number.isInteger(parsed) || parsed < 1) {
		throw new Error(`${flag} expects an integer >= 1, got "${value}"`)
	}
	return parsed
}

function parseArgs(argv) {
	const optionKeys = {
		'--frontend-url': 'frontendUrl',
		'--api-health-url': 'apiHealthUrl',
		'--timeout': 'timeoutMs',
		'--concurrency': 'concurrency',
	}
	const valueParsers = {
		'--frontend-url': (value) => parseUrl(value, '--frontend-url'),
		'--api-health-url': (value) => parseUrl(value, '--api-health-url'),
		'--timeout': (value) => parseTimeout(value, '--timeout'),
		'--concurrency': (value) => parseCount(value, '--concurrency'),
	}
	const options = {
		frontendUrl: DEFAULT_FRONTEND_URL,
		apiHealthUrl: DEFAULT_API_HEALTH_URL,
		timeoutMs: DEFAULT_TIMEOUT_MS,
		concurrency: DEFAULT_CONCURRENCY,
	}
	for (let index = 0; index < argv.length; index += 1) {
		const flag = argv[index]
		if (flag === '--help') return { ...options, help: true }
		const parseValue = valueParsers[flag]
		if (!parseValue) throw new Error(`unknown argument: ${flag}`)
		const value = argv[index + 1]
		if (value === undefined) throw new Error(`${flag} requires a value`)
		index += 1
		options[optionKeys[flag]] = parseValue(value)
	}
	return options
}

function printUsage() {
	console.log(
		[
			'runtime-smoke: verify the frontend shell, its referenced assets, and the backend health probe.',
			'',
			'Usage: node scripts/runtime-smoke.mjs [options]',
			'',
			'Options:',
			`  --frontend-url <url>    Frontend base URL to smoke (default: ${DEFAULT_FRONTEND_URL})`,
			`  --api-health-url <url>  Backend health endpoint (default: ${DEFAULT_API_HEALTH_URL})`,
			`  --timeout <ms>          Per-request timeout in milliseconds (default: ${DEFAULT_TIMEOUT_MS})`,
			`  --concurrency <n>       Parallel asset requests (default: ${DEFAULT_CONCURRENCY})`,
			'  --help                  Show this help',
			'',
			'Checks: GET / -> every <script src>/<link href> asset -> GET /notes -> GET <api-health-url>.',
			'Exit code 0 when every check passes (referenced N / failed 0), otherwise 1.',
		].join('\n'),
	)
}

async function main(argv) {
	let options
	try {
		options = parseArgs(argv)
	} catch (error) {
		console.error(`runtime-smoke: ${error.message}`)
		printUsage()
		process.exitCode = 1
		return
	}
	if (options.help) {
		printUsage()
		return
	}
	try {
		const { summary } = await runSmoke(options)
		for (const { name, url, reason } of summary.failures) {
			console.log(`FAIL ${name} ${url} ${reason}`)
		}
		console.log(
			`SMOKE referenced=${summary.assets.referenced} ok=${summary.assets.ok} failed=${summary.assets.failed} checks=${summary.total} failed=${summary.failed} frontend=${options.frontendUrl}`,
		)
		console.log(
			`SMOKE_JSON ${JSON.stringify({
				frontend: options.frontendUrl,
				apiHealth: options.apiHealthUrl,
				referenced: summary.assets.referenced,
				ok: summary.assets.ok,
				failed: summary.assets.failed,
				totalChecks: summary.total,
				totalFailed: summary.failed,
				failures: summary.failures,
			})}`,
		)
		process.exitCode = decideExit(summary)
	} catch (error) {
		console.error(`FAIL smoke ${error?.message ?? String(error)}`)
		process.exitCode = 1
	}
}

const invokedDirectly =
	Boolean(process.argv[1]) && import.meta.url === pathToFileURL(resolve(process.argv[1])).href

if (invokedDirectly) {
	await main(process.argv.slice(2))
	process.exit(process.exitCode ?? 0)
}
