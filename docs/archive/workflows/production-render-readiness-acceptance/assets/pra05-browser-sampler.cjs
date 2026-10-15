#!/usr/bin/env node
'use strict'

const fs = require('node:fs')
const path = require('node:path')
const { execFileSync } = require('node:child_process')
const { createRequire } = require('node:module')

const ASSET_DIR = __dirname
const STATE_FILE = path.join(ASSET_DIR, 'pra05-fixture-baseline-v3.json')
const FRONTEND_BASE = process.env.PRA_FRONTEND_BASE || 'http://localhost:3100'
const API_BASE = process.env.PRA_API_BASE || 'http://api.localhost:8100'
const DB_HOST = process.env.PRA_DB_HOST || '127.0.0.1'
const DB_PORT = process.env.PRA_DB_PORT || '55432'
const DB_NAME = process.env.PRA_DB_NAME || 'pra_f4'
const DB_USER = process.env.PRA_DB_USER || 'pra04'
const PLAYWRIGHT_ROOT = process.env.PRA_PLAYWRIGHT_ROOT

if (!PLAYWRIGHT_ROOT) {
  throw new Error('PRA_PLAYWRIGHT_ROOT is required and must point to the isolated dependency tree')
}

const { chromium } = createRequire(path.join(PLAYWRIGHT_ROOT, 'package.json'))('playwright')

const SCENARIOS = {
  E0: { path: '/notes', state: 'empty', mark: 'notes:list-ready', apiPath: '/api/notes', visible: 0 },
  L20: { path: '/notes', state: 'ready', mark: 'notes:list-ready', apiPath: '/api/notes', visible: 20 },
  D1: { path: '/notes/pra04-d1', state: 'ready', mark: 'notes:detail-ready', apiPath: '/api/notes/pra04-d1', visible: null }
}

function args() {
  const out = { scenario: null, count: 1, raw: null, runId: null, batchSize: 1, restore: false }
  for (let i = 2; i < process.argv.length; i += 1) {
    const value = process.argv[i]
    if (value === '--restore-m30') out.restore = true
    else if (value.startsWith('--scenario=')) out.scenario = value.slice(11).toUpperCase()
    else if (value.startsWith('--count=')) out.count = Number(value.slice(8))
    else if (value.startsWith('--raw=')) out.raw = value.slice(6)
    else if (value.startsWith('--run-id=')) out.runId = value.slice(9)
    else if (value.startsWith('--batch-size=')) out.batchSize = Number(value.slice(13))
  }
  return out
}

function safeText(value) {
  return String(value || '')
    .replace(/(authorization|cookie|password|token|secret)\s*[:=]\s*[^\s]+/gi, '$1=[REDACTED]')
    .replace(/file:\/\/[^\s)]+/g, 'file://[REDACTED]')
    .slice(0, 1000)
}

function atomicWrite(file, value) {
  const tmp = `${file}.tmp-${process.pid}`
  fs.writeFileSync(tmp, value, { encoding: 'utf8', mode: 0o600 })
  fs.renameSync(tmp, file)
}

function appendJson(file, value) {
  const fd = fs.openSync(file, 'a', 0o600)
  try {
    fs.writeSync(fd, `${JSON.stringify(value)}\n`)
    fs.fsyncSync(fd)
  } finally {
    fs.closeSync(fd)
  }
}

function psql(sql) {
  return execFileSync('psql', ['-X', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, '-d', DB_NAME, '-At', '-F', '\t', '-c', sql], {
    cwd: ASSET_DIR,
    encoding: 'utf8',
    env: { ...process.env, PGPASSWORD: '' },
    stdio: ['ignore', 'pipe', 'pipe']
  }).trim()
}

function fixtureRows() {
  const output = psql("select slug, status, hidden::text, type from notes order by slug")
  return output ? output.split('\n').map(line => {
    const [slug, status, hidden, type] = line.split('\t')
    return { slug, status, hidden: hidden === 't' || hidden === 'true', type }
  }) : []
}

function fixtureSummary() {
  const output = psql("select count(*)::int, count(*) filter (where status='published' and hidden=false)::int, count(*) filter (where status='published' and hidden=true)::int, count(*) filter (where status='draft')::int, count(*) filter (where slug='pra04-d1' and status='published' and hidden=false)::int from notes")
  const [total, publicVisible, publishedHidden, drafts, d1Public] = output.split('\t').map(Number)
  return { total, public_visible: publicVisible, published_hidden: publishedHidden, drafts, d1_public: d1Public === 1 }
}

const CANONICAL_HIDDEN_PUBLISHED = ['pra04-blog-26', 'pra04-blog-29', 'pra04-mistake-27', 'pra04-mistake-30', 'pra04-note-28']

function establishCanonicalM30() {
  const hiddenPublished = CANONICAL_HIDDEN_PUBLISHED.map(sqlLiteral).join(',')
  psql(`begin; update notes set status='published', hidden=false; update notes set status='draft', hidden=true where slug in ('pra04-blog-23','pra04-mistake-21','pra04-mistake-24','pra04-note-22','pra04-note-25'); update notes set status='published', hidden=true where slug in (${hiddenPublished}); commit;`)
  const summary = fixtureSummary()
  if (summary.total !== 30 || summary.public_visible !== 20 || summary.published_hidden !== 5 || summary.drafts !== 5 || !summary.d1_public) {
    throw new Error(`canonical M30 establishment failed: ${JSON.stringify(summary)}`)
  }
  return summary
}

function sqlLiteral(value) {
  if (!/^[a-z0-9-]+$/.test(value)) throw new Error(`unexpected synthetic slug: ${value}`)
  return `'${value}'`
}

function restoreM30(baseline) {
  const statements = baseline.map(row => `update notes set status=${sqlLiteral(row.status)}, hidden=${row.hidden ? 'true' : 'false'} where slug=${sqlLiteral(row.slug)};`)
  psql(`begin; ${statements.join(' ')} commit;`)
  const summary = fixtureSummary()
  if (summary.total !== baseline.length || summary.public_visible !== 20 || !summary.d1_public) {
    throw new Error(`M30 restore failed: ${JSON.stringify(summary)}`)
  }
  return summary
}

function setScenario(scenario, baseline) {
  if (scenario === 'E0') psql('update notes set hidden=true;')
  else restoreM30(baseline)
  const summary = fixtureSummary()
  const expected = scenario === 'E0' ? 0 : 20
  if (summary.public_visible !== expected || (scenario === 'D1' && !summary.d1_public)) {
    throw new Error(`fixture ${scenario} failed: ${JSON.stringify(summary)}`)
  }
  return summary
}

function writeFixtureRecord(runId, action, scenario, summary) {
  appendJson(path.join(ASSET_DIR, 'pra05-fixture-events.ndjson'), {
    run_id: runId,
    recorded_at: new Date().toISOString(),
    action,
    scenario,
    fixture: summary,
    database: { host: DB_HOST, port: Number(DB_PORT), name: DB_NAME, user: DB_USER, isolated: true }
  })
}

async function healthProbe() {
  const started = Date.now()
  const response = await fetch(`${API_BASE}/api/health`)
  return { status: response.status, ok: response.ok, duration_ms: Date.now() - started }
}

function initScript() {
  return () => {
    window.__praApiEvents = []
    const originalFetch = window.fetch.bind(window)
    window.fetch = async (input, init) => {
      const url = typeof input === 'string' ? input : input.url
      const method = init?.method || (typeof input === 'string' ? 'GET' : input.method) || 'GET'
      const isApi = url.includes('/api/')
      const started = performance.now()
      try {
        const response = await originalFetch(input, init)
        const responseEnd = performance.now()
        if (isApi) window.__praApiEvents.push({ url, method, status: response.status, start: started, responseEnd, duration: responseEnd - started })
        return response
      } catch (error) {
        const responseEnd = performance.now()
        if (isApi) window.__praApiEvents.push({ url, method, status: 0, start: started, responseEnd, duration: responseEnd - started, error: String(error) })
        throw error
      }
    }
  }
}

function urlPath(value) {
  try { return new URL(value).pathname } catch { return value }
}

async function sample(browser, scenarioName, sampleId, runId, browserVersion, expected, fixture) {
  const startedAt = new Date().toISOString()
  const targetUrl = `${FRONTEND_BASE}${expected.path}`
  const consoleErrors = []
  const pageErrors = []
  const failedRequests = []
  const unexpectedNavigations = []
  const dialogs = []
  const downloads = []
  let page
  let context
  const reasons = []
  const requestUrls = []
  try {
    context = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'zh-CN' })
    await context.addInitScript(initScript())
    page = await context.newPage()
    page.on('console', message => { if (message.type() === 'error') consoleErrors.push(safeText(message.text())) })
    page.on('pageerror', error => pageErrors.push(safeText(error.message)))
    page.on('request', request => { if (request.url().includes('/api/')) requestUrls.push({ url: urlPath(request.url()), method: request.method() }) })
    page.on('requestfailed', request => failedRequests.push({ url: urlPath(request.url()), method: request.method(), failure: safeText(request.failure()?.errorText) }))
    page.on('framenavigated', frame => {
      if (frame === page.mainFrame()) {
        const current = frame.url()
        if (current && current !== targetUrl && current !== `${targetUrl}/`) unexpectedNavigations.push(urlPath(current))
      }
    })
    page.on('dialog', async dialog => { dialogs.push({ type: dialog.type(), message: safeText(dialog.message()) }); await dialog.dismiss() })
    page.on('download', download => downloads.push({ suggested_filename: safeText(download.suggestedFilename()) }))

    let navigationResponse
    try { navigationResponse = await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 10000 }) }
    catch (error) { reasons.push(`navigation:${safeText(error.message)}`) }

    try {
      await page.waitForFunction(({ state, mark }) => {
        const nodes = document.querySelectorAll('[data-render-state]')
        return nodes.length === 1 && nodes[0].tagName.toLowerCase() === 'main' && nodes[0].getAttribute('data-render-state') === state && performance.getEntriesByName(mark, 'mark').length >= 1
      }, { state: expected.state, mark: expected.mark }, { timeout: 10000 })
    } catch (error) { reasons.push(`readiness:${safeText(error.message)}`) }

    const evidence = await page.evaluate(({ expected, apiBase }) => {
      const nodes = [...document.querySelectorAll('[data-render-state]')]
      const node = nodes[0]
      const nav = performance.getEntriesByType('navigation')[0]
      const lcpEntries = performance.getEntriesByType('largest-contentful-paint')
      const marks = performance.getEntriesByName(expected.mark, 'mark')
      const main = node?.tagName.toLowerCase() === 'main' ? node : null
      const syntheticLinks = main ? [...main.querySelectorAll('a[href]')].filter(anchor => /^\/(?:notes|blog)\/pra04-/.test(new URL(anchor.href, location.href).pathname)).length : 0
      return {
        dom: {
          selector: '[data-render-state]', selector_count: nodes.length, tag_name: node?.tagName.toLowerCase() || null,
          state: node?.getAttribute('data-render-state') || null, h3_count: main?.querySelectorAll('h3').length || 0,
          synthetic_link_count: syntheticLinks, prose_count: main?.querySelectorAll('.prose').length || 0,
          heading_count: main?.querySelectorAll('h1,h2,h3').length || 0, pre_count: main?.querySelectorAll('pre').length || 0,
          table_count: main?.querySelectorAll('table').length || 0, link_count: main?.querySelectorAll('a[href]').length || 0,
          text_length: main?.textContent?.length || 0
        },
        navigation: nav ? { ttfb: nav.responseStart - nav.startTime, dom_content_loaded: nav.domContentLoadedEventEnd, load: nav.loadEventEnd, duration: nav.duration, response_status: navigationResponseStatus } : null,
        lcp: lcpEntries.length ? lcpEntries[lcpEntries.length - 1].startTime : null,
        marks: marks.map(entry => ({ name: entry.name, start: entry.startTime, duration: entry.duration })),
        api_events: window.__praApiEvents.map(event => ({ ...event, url: new URL(event.url, apiBase).pathname + new URL(event.url, apiBase).search }))
      }
      function navigationResponseStatus() { return null }
    }, { expected, apiBase: API_BASE })
    if (navigationResponse && evidence.navigation) evidence.navigation.response_status = navigationResponse.status()

    const apiEvents = evidence.api_events || []
    const requiredApi = apiEvents.filter(event => event.url.split('?')[0] === expected.apiPath && event.method === 'GET')
    const forbiddenApi = apiEvents.filter(event => event.url.startsWith('/api/auth/me') || event.url.startsWith('/api/admin/'))
    const dom = evidence.dom
    if (dom.selector_count !== 1 || dom.tag_name !== 'main') reasons.push(`dom-selector-not-unique:${dom.selector_count}`)
    if (dom.state !== expected.state) reasons.push(`dom-state:${dom.state || 'missing'}`)
    if (evidence.marks.length !== 1) reasons.push(`mark-count:${evidence.marks.length}`)
    if (requiredApi.length !== 1 || requiredApi[0].status !== 200) reasons.push(`required-api:${requiredApi.length ? requiredApi.map(event => event.status).join(',') : 'missing'}`)
    if (forbiddenApi.length) reasons.push(`forbidden-api:${forbiddenApi.map(event => event.url).join(',')}`)
    if (expected.visible !== null && dom.synthetic_link_count !== expected.visible) reasons.push(`visible-count:links=${dom.synthetic_link_count}`)
    if (expected.visible === null && (dom.prose_count < 1 || dom.heading_count < 2 || dom.pre_count < 1 || dom.table_count < 1 || dom.link_count < 1)) reasons.push(`detail-dom:prose=${dom.prose_count},headings=${dom.heading_count},pre=${dom.pre_count},table=${dom.table_count},links=${dom.link_count}`)
    if (consoleErrors.length) reasons.push('console-errors')
    if (pageErrors.length) reasons.push('page-errors')
    if (failedRequests.length) reasons.push('failed-requests')
    if (unexpectedNavigations.length) reasons.push('unexpected-navigation')
    if (dialogs.length) reasons.push('dialogs')
    if (downloads.length) reasons.push('downloads')

    const mark = evidence.marks[0]
    return {
      run_id: runId, sample_id: sampleId, scenario: scenarioName, sample_status: reasons.length ? 'failed' : 'valid', valid: reasons.length === 0,
      browser_temperature: 'cold', server_temperature: 'warm', browser_version: browserVersion, environment_mode: 'production-build-local-isolated',
      base_url: FRONTEND_BASE, navigation_url: targetUrl, started_at: startedAt, ended_at: new Date().toISOString(),
      fixture, navigation: evidence.navigation, lcp: evidence.lcp, readiness: { mark_name: expected.mark, mark_count: evidence.marks.length, mark_start: mark?.start ?? null, readiness_duration: mark?.start ?? null },
      required_api: requiredApi, api_requests: apiEvents, dom: evidence.dom, console_errors: consoleErrors, page_errors: pageErrors,
      failed_requests: failedRequests, unexpected_navigations: unexpectedNavigations, dialogs, downloads, request_count: requestUrls.length,
      failure_reason: reasons.length ? reasons.join('; ') : null
    }
  } catch (error) {
    return {
      run_id: runId, sample_id: sampleId, scenario: scenarioName, sample_status: 'failed', valid: false,
      browser_temperature: 'cold', server_temperature: 'warm', browser_version: browserVersion, environment_mode: 'production-build-local-isolated',
      base_url: FRONTEND_BASE, navigation_url: targetUrl, started_at: startedAt, ended_at: new Date().toISOString(), fixture,
      navigation: null, lcp: null, readiness: { mark_name: expected.mark, mark_count: 0, mark_start: null, readiness_duration: null }, required_api: [], api_requests: [],
      dom: { selector: '[data-render-state]', selector_count: null, tag_name: null, state: null }, console_errors: consoleErrors, page_errors: pageErrors,
      failed_requests: failedRequests, unexpected_navigations: unexpectedNavigations, dialogs, downloads, request_count: requestUrls.length,
      failure_reason: `harness:${safeText(error.message)}`
    }
  } finally {
    if (context) await context.close().catch(() => undefined)
  }
}

async function main() {
  const options = args()
  const runId = options.runId || `pra05-${new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)}`
  if (options.restore) {
    const baseline = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')).baseline
    const summary = restoreM30(baseline)
    writeFixtureRecord(runId, 'restore-m30', 'M30', summary)
    console.log(JSON.stringify({ run_id: runId, restored: true, fixture: summary }))
    return
  }
  if (!SCENARIOS[options.scenario]) throw new Error('--scenario must be E0, L20, or D1')
  if (!Number.isInteger(options.count) || options.count < 1 || options.count > 10) throw new Error('--count must be 1..10')
  if (!Number.isInteger(options.batchSize) || options.batchSize < 1 || options.batchSize > 3) throw new Error('--batch-size must be 1..3')
  let baseline
  if (fs.existsSync(STATE_FILE)) {
    baseline = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')).baseline
  } else {
    const canonical = establishCanonicalM30()
    baseline = fixtureRows()
    atomicWrite(STATE_FILE, JSON.stringify({ run_id: runId, recorded_at: new Date().toISOString(), establishment: canonical, baseline }, null, 2) + '\n')
  }
  if (!baseline.length) throw new Error('isolated fixture has no notes')
  const fixture = setScenario(options.scenario, baseline)
  writeFixtureRecord(runId, 'apply', options.scenario, fixture)
  const rawFile = path.resolve(options.raw || path.join(ASSET_DIR, `pra05-${options.scenario.toLowerCase()}-${runId}.ndjson`))
  const manifestFile = path.join(ASSET_DIR, `pra05-${options.scenario.toLowerCase()}-${runId}-manifest.json`)
  const health = await healthProbe()
  const browser = await chromium.launch({ headless: true })
  const browserVersion = browser.version()
  atomicWrite(manifestFile, JSON.stringify({ run_id: runId, scenario: options.scenario, count_requested: options.count, batch_size: options.batchSize, frontend_base: FRONTEND_BASE, api_base: API_BASE, browser_version: browserVersion, environment_mode: 'production-build-local-isolated', browser_temperature: 'cold', server_temperature: 'warm', server_warm_probe: health, git_head: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: path.resolve(ASSET_DIR, '../../../..'), encoding: 'utf8' }).trim(), fixture }, null, 2) + '\n')
  let valid = 0
  let attempted = 0
  try {
    while (valid < options.count) {
      const batch = Math.min(options.batchSize, options.count - valid)
      for (let i = 0; i < batch; i += 1) {
        attempted += 1
        const record = await sample(browser, options.scenario, `${options.scenario}-${String(attempted).padStart(2, '0')}`, runId, browserVersion, SCENARIOS[options.scenario], fixture)
        appendJson(rawFile, record)
        console.log(JSON.stringify({ sample_id: record.sample_id, valid: record.valid, failure_reason: record.failure_reason }))
        if (!record.valid) throw new Error(`sample failed; inspect ${path.basename(rawFile)} before retrying`)
        valid += 1
      }
    }
  } finally {
    await browser.close().catch(() => undefined)
    const summary = restoreM30(baseline)
    writeFixtureRecord(runId, 'restore-m30', 'M30', summary)
  }
  console.log(JSON.stringify({ run_id: runId, scenario: options.scenario, valid, attempted, raw_file: path.basename(rawFile) }))
}

main().catch(error => { console.error(safeText(error.message)); process.exitCode = 1 })
