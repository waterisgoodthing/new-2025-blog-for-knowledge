#!/usr/bin/env node

import fs from 'node:fs'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { createRequire } from 'node:module'

const ASSET_DIR = path.dirname(new URL(import.meta.url).pathname)
const FRONTEND_BASE = process.env.PRA_FRONTEND_BASE || 'http://localhost:3100'
const API_BASE = process.env.PRA_API_BASE || 'http://api.localhost:8100'
const DB_HOST = process.env.PRA_DB_HOST || '127.0.0.1'
const DB_PORT = process.env.PRA_DB_PORT || '55432'
const DB_NAME = process.env.PRA_DB_NAME || 'pra_f4'
const DB_USER = process.env.PRA_DB_USER || 'pra04'
const ISOLATED_WORKTREE = process.env.PRA_ISOLATED_WORKTREE || '/private/tmp/pra04-20260822-auWgUg/worktree'
const PLAYWRIGHT_ROOT = process.env.PRA_PLAYWRIGHT_ROOT
const STATE_FILE = path.join(ASSET_DIR, 'pra05-fixture-baseline-v3.json')
const EVENTS_FILE = path.join(ASSET_DIR, 'pra05-fixture-events.ndjson')

if (!PLAYWRIGHT_ROOT) throw new Error('PRA_PLAYWRIGHT_ROOT must point to isolated worktree node_modules')
const { chromium } = createRequire(path.join(PLAYWRIGHT_ROOT, 'package.json'))('playwright')

const SCENARIOS = {
  E0: { path: '/notes', state: 'empty', mark: 'notes:list-ready', apiPath: '/api/notes', visible: 0 },
  L20: { path: '/notes', state: 'ready', mark: 'notes:list-ready', apiPath: '/api/notes', visible: 20 },
  D1: { path: '/notes/pra04-d1', state: 'ready', mark: 'notes:detail-ready', apiPath: '/api/notes/pra04-d1', visible: null }
}

function parseArgs() {
  const result = { scenario: null, count: 1, batchSize: 1, runId: null, raw: null, restore: false }
  for (const value of process.argv.slice(2)) {
    if (value === '--restore-m30') result.restore = true
    else if (value.startsWith('--scenario=')) result.scenario = value.slice('--scenario='.length).toUpperCase()
    else if (value.startsWith('--count=')) result.count = Number(value.slice('--count='.length))
    else if (value.startsWith('--batch-size=')) result.batchSize = Number(value.slice('--batch-size='.length))
    else if (value.startsWith('--run-id=')) result.runId = value.slice('--run-id='.length)
    else if (value.startsWith('--raw=')) result.raw = value.slice('--raw='.length)
  }
  return result
}

function safeText(value) {
  return String(value || '')
    .replace(/(authorization|cookie|password|token|secret)\s*[:=]\s*[^\s]+/gi, '$1=[REDACTED]')
    .replace(/file:\/\/[^\s)]+/g, 'file://[REDACTED]')
    .slice(0, 1200)
}

function safeUrl(value) {
  try {
    const url = new URL(value)
    return `${url.origin}${url.pathname}${url.search}`
  } catch {
    return safeText(value)
  }
}

function pathAndQuery(value) {
  try {
    const url = new URL(value)
    return `${url.pathname}${url.search}`
  } catch {
    return safeText(value)
  }
}

function atomicWrite(file, content) {
  const temp = `${file}.tmp-${process.pid}`
  fs.writeFileSync(temp, content, { encoding: 'utf8', mode: 0o600 })
  fs.renameSync(temp, file)
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
  return execFileSync('psql', [
    '-X', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, '-d', DB_NAME,
    '-At', '-F', '\t', '-c', sql
  ], {
    cwd: ASSET_DIR,
    encoding: 'utf8',
    env: { ...process.env, PGPASSWORD: '' },
    stdio: ['ignore', 'pipe', 'pipe']
  }).trim()
}

function sqlLiteral(value) {
  if (!/^[a-z0-9-]+$/.test(value)) throw new Error(`unexpected synthetic slug: ${value}`)
  return `'${value}'`
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

function restoreM30(baseline) {
  const statements = baseline.map(row => `update notes set status=${sqlLiteral(row.status)}, hidden=${row.hidden ? 'true' : 'false'} where slug=${sqlLiteral(row.slug)};`)
  psql(`begin; ${statements.join(' ')} commit;`)
  const summary = fixtureSummary()
  if (summary.total !== baseline.length || summary.public_visible !== 20 || !summary.d1_public) {
    throw new Error(`M30 restore failed: ${JSON.stringify(summary)}`)
  }
  return summary
}

function applyScenario(scenario, baseline) {
  if (scenario === 'E0') psql('update notes set hidden=true;')
  else restoreM30(baseline)
  const summary = fixtureSummary()
  const expectedVisible = scenario === 'E0' ? 0 : 20
  if (summary.public_visible !== expectedVisible || (scenario === 'D1' && !summary.d1_public)) {
    throw new Error(`fixture ${scenario} failed: ${JSON.stringify(summary)}`)
  }
  return summary
}

function writeFixtureEvent(runId, action, scenario, fixture) {
  appendJson(EVENTS_FILE, {
    run_id: runId,
    recorded_at: new Date().toISOString(),
    action,
    scenario,
    fixture,
    database: { host: DB_HOST, port: Number(DB_PORT), name: DB_NAME, user: DB_USER, isolated: true }
  })
}

async function warmApi(expected) {
  const started = Date.now()
  const warmUrl = expected.apiPath === '/api/notes/pra04-d1'
    ? `${API_BASE}${expected.apiPath}`
    : `${API_BASE}${expected.apiPath}?status=published&page=1&size=20`
  try {
    const response = await fetch(warmUrl, { signal: AbortSignal.timeout(5000) })
    return { url: warmUrl, status: response.status, ok: response.ok, duration_ms: Date.now() - started }
  } catch (error) {
    return { url: warmUrl, status: null, ok: false, duration_ms: Date.now() - started, error: safeText(error.message) }
  }
}

function collectInitScript() {
  return () => {
    window.__pra05_started_at = new Date().toISOString()
  }
}

async function sample(browser, scenario, sampleId, runId, fixture, warmProbe) {
  const expected = SCENARIOS[scenario]
  const targetUrl = `${FRONTEND_BASE}${expected.path}`
  const startedAt = new Date().toISOString()
  const consoleErrors = []
  const pageErrors = []
  const failedRequests = []
  const unexpectedNavigations = []
  const dialogs = []
  const downloads = []
  const apiResponses = []
  const allRequests = []
  const reasons = []
  let context
  try {
    context = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'zh-CN' })
    await context.addInitScript(collectInitScript())
    const page = await context.newPage()
    page.on('console', message => { if (message.type() === 'error') consoleErrors.push(safeText(message.text())) })
    page.on('pageerror', error => pageErrors.push(safeText(error.message)))
    page.on('request', request => allRequests.push({ url: safeUrl(request.url()), method: request.method(), resource_type: request.resourceType() }))
    page.on('requestfailed', request => failedRequests.push({ url: safeUrl(request.url()), method: request.method(), resource_type: request.resourceType(), failure: safeText(request.failure()?.errorText) }))
    page.on('response', response => {
      if (response.url().includes('/api/')) apiResponses.push({ url: safeUrl(response.url()), method: response.request().method(), status: response.status() })
    })
    page.on('framenavigated', frame => {
      if (frame === page.mainFrame()) {
        const current = frame.url()
        if (current && current !== targetUrl && current !== `${targetUrl}/`) unexpectedNavigations.push(safeUrl(current))
      }
    })
    page.on('dialog', async dialog => { dialogs.push({ type: dialog.type(), message: safeText(dialog.message()) }); await dialog.dismiss() })
    page.on('download', download => downloads.push({ suggested_filename: safeText(download.suggestedFilename()) }))

    let navigationResponse = null
    try {
      navigationResponse = await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 15000 })
    } catch (error) {
      reasons.push(`navigation:${safeText(error.message)}`)
    }

    try {
      await page.waitForFunction(({ state, mark }) => {
        const nodes = document.querySelectorAll('[data-render-state]')
        return nodes.length === 1 && nodes[0].getAttribute('data-render-state') === state && performance.getEntriesByName(mark, 'mark').length >= 1
      }, { state: expected.state, mark: expected.mark }, { timeout: 15000 })
    } catch (error) {
      reasons.push(`readiness:${safeText(error.message)}`)
    }

    // Allow Next.js link prefetches to settle before collecting failure events.
    // Any remaining aborted RSC prefetch is retained in failed_requests below.
    await page.waitForTimeout(1000)
    const browserEvidence = await page.evaluate(({ expected, apiBase, responseRecords }) => {
      const nodes = [...document.querySelectorAll('[data-render-state]')]
      const node = nodes[0]
      const nav = performance.getEntriesByType('navigation')[0]
      const lcpEntries = performance.getEntriesByType('largest-contentful-paint')
      const marks = performance.getEntriesByName(expected.mark, 'mark')
      const apiResources = performance.getEntriesByType('resource')
        .filter(entry => {
          try { return new URL(entry.name).origin === new URL(apiBase).origin && new URL(entry.name).pathname.startsWith('/api/') } catch { return false }
        })
        .map(entry => ({ url: `${new URL(entry.name).pathname}${new URL(entry.name).search}`, start: entry.startTime, responseEnd: entry.responseEnd, duration: entry.duration, transferSize: entry.transferSize }))
      const main = node?.tagName.toLowerCase() === 'main' ? node : null
      const syntheticLinks = main ? [...main.querySelectorAll('a[href]')].filter(anchor => /^\/(?:notes|blog)\/pra04-/.test(new URL(anchor.href, location.href).pathname)).length : 0
      const mark = marks[0] || null
      return {
        navigation: nav ? {
          start_time: nav.startTime,
          response_start: nav.responseStart,
          ttfb: nav.responseStart - nav.startTime,
          dom_content_loaded: nav.domContentLoadedEventEnd,
          load: nav.loadEventEnd,
          duration: nav.duration
        } : null,
        lcp: lcpEntries.length ? {
          start_time: lcpEntries[lcpEntries.length - 1].startTime,
          time: new Date(performance.timeOrigin + lcpEntries[lcpEntries.length - 1].startTime).toISOString()
        } : null,
        readiness: {
          mark_name: expected.mark,
          mark_count: marks.length,
          mark_start: mark?.startTime ?? null,
          mark_duration: mark?.duration ?? null,
          mark_time: mark ? new Date(performance.timeOrigin + mark.startTime).toISOString() : null
        },
        dom: {
          selector: '[data-render-state]',
          selector_count: nodes.length,
          tag_name: node?.tagName.toLowerCase() || null,
          state: node?.getAttribute('data-render-state') || null,
          text_content: main?.textContent || null,
          text_length: main?.textContent?.length || 0,
          heading_count: main?.querySelectorAll('h1,h2,h3').length || 0,
          h3_count: main?.querySelectorAll('h3').length || 0,
          synthetic_link_count: syntheticLinks,
          prose_count: main?.querySelectorAll('.prose').length || 0,
          pre_count: main?.querySelectorAll('pre').length || 0,
          table_count: main?.querySelectorAll('table').length || 0,
          link_count: main?.querySelectorAll('a[href]').length || 0
        },
        api_resources: apiResources,
        api_responses: responseRecords.map(record => ({ ...record, url: `${new URL(record.url).pathname}${new URL(record.url).search}` }))
      }
    }, { expected, apiBase: API_BASE, responseRecords: apiResponses })

    if (navigationResponse && browserEvidence.navigation) browserEvidence.navigation.response_status = navigationResponse.status()
    const requiredResources = browserEvidence.api_resources.filter(resource => resource.url.split('?')[0] === expected.apiPath)
    const requiredResponses = browserEvidence.api_responses.filter(response => response.url.split('?')[0] === expected.apiPath && response.method === 'GET')
    const forbiddenApi = allRequests.filter(request => request.url.includes('/api/auth/me') || request.url.includes('/api/admin/'))

    const dom = browserEvidence.dom
    if (dom.selector_count !== 1 || dom.tag_name !== 'main') reasons.push(`dom-selector-not-unique:${dom.selector_count}`)
    if (dom.state !== expected.state) reasons.push(`dom-state:${dom.state || 'missing'}`)
    if (browserEvidence.readiness.mark_count !== 1 || browserEvidence.readiness.mark_start === null) reasons.push(`readiness-mark:${browserEvidence.readiness.mark_count}`)
    if (requiredResources.length !== 1 || requiredResources[0].duration === null || requiredResources[0].responseEnd === null) reasons.push(`required-api-resource:${requiredResources.length}`)
    if (requiredResponses.length !== 1 || requiredResponses[0].status !== 200) reasons.push(`required-api-status:${requiredResponses.map(response => response.status).join(',') || 'missing'}`)
    if (forbiddenApi.length) reasons.push(`forbidden-api:${forbiddenApi.map(request => pathAndQuery(request.url)).join(',')}`)
    if (expected.visible !== null && dom.synthetic_link_count !== expected.visible) reasons.push(`visible-count:${dom.synthetic_link_count}`)
    if (expected.visible === null && (dom.prose_count < 1 || dom.heading_count < 2 || dom.pre_count < 1 || dom.table_count < 1 || dom.link_count < 1)) reasons.push(`detail-dom:prose=${dom.prose_count},headings=${dom.heading_count},pre=${dom.pre_count},table=${dom.table_count},links=${dom.link_count}`)
    if (consoleErrors.length) reasons.push('console-errors')
    if (pageErrors.length) reasons.push('page-errors')
    if (failedRequests.length) reasons.push('failed-requests')
    if (unexpectedNavigations.length) reasons.push('unexpected-navigation')
    if (dialogs.length) reasons.push('dialogs')
    if (downloads.length) reasons.push('downloads')

    return {
      run_id: runId,
      sample_id: sampleId,
      scenario,
      sample_status: reasons.length ? 'failed' : 'valid',
      valid: reasons.length === 0,
      browser_temperature: 'cold',
      server_temperature: 'warm',
      browser_version: browser.version(),
      environment_mode: 'production-build-local-isolated',
      frontend_base: FRONTEND_BASE,
      api_base: API_BASE,
      navigation_url: targetUrl,
      started_at: startedAt,
      ended_at: new Date().toISOString(),
      fixture,
      server_warm_probe: warmProbe,
      navigation: browserEvidence.navigation,
      lcp: browserEvidence.lcp,
      readiness: browserEvidence.readiness,
      api_resources: browserEvidence.api_resources,
      api_responses: browserEvidence.api_responses,
      required_api: { resources: requiredResources, responses: requiredResponses },
      dom,
      console_errors: consoleErrors,
      page_errors: pageErrors,
      failed_requests: failedRequests,
      unexpected_navigations: unexpectedNavigations,
      dialogs,
      downloads,
      request_count: allRequests.length,
      failure_reason: reasons.length ? reasons.join('; ') : null
    }
  } catch (error) {
    return {
      run_id: runId,
      sample_id: sampleId,
      scenario,
      sample_status: 'failed',
      valid: false,
      browser_temperature: 'cold',
      server_temperature: 'warm',
      browser_version: browser.version(),
      environment_mode: 'production-build-local-isolated',
      frontend_base: FRONTEND_BASE,
      api_base: API_BASE,
      navigation_url: targetUrl,
      started_at: startedAt,
      ended_at: new Date().toISOString(),
      fixture,
      server_warm_probe: warmProbe,
      navigation: null,
      lcp: null,
      readiness: { mark_name: expected.mark, mark_count: 0, mark_start: null, mark_duration: null, mark_time: null },
      api_resources: [],
      api_responses: apiResponses,
      required_api: { resources: [], responses: [] },
      dom: { selector: '[data-render-state]', selector_count: null, tag_name: null, state: null, text_content: null, text_length: 0 },
      console_errors: consoleErrors,
      page_errors: pageErrors,
      failed_requests: failedRequests,
      unexpected_navigations: unexpectedNavigations,
      dialogs,
      downloads,
      request_count: allRequests.length,
      failure_reason: `harness:${safeText(error.message)}`
    }
  } finally {
    if (context) await context.close().catch(() => undefined)
  }
}

async function main() {
  const options = parseArgs()
  const runId = options.runId || `pra05-qa-${new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)}`
  if (options.restore) {
    const baseline = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')).baseline
    const fixture = restoreM30(baseline)
    writeFixtureEvent(runId, 'restore-m30', 'M30', fixture)
    console.log(JSON.stringify({ run_id: runId, restored: true, fixture }))
    return
  }
  if (!SCENARIOS[options.scenario]) throw new Error('--scenario must be E0, L20, or D1')
  if (!Number.isInteger(options.count) || options.count < 1 || options.count > 10) throw new Error('--count must be 1..10')
  if (!Number.isInteger(options.batchSize) || options.batchSize < 1 || options.batchSize > 3) throw new Error('--batch-size must be 1..3')

  const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'))
  const baseline = state.baseline
  if (!Array.isArray(baseline) || baseline.length !== 30) throw new Error('isolated synthetic baseline must contain 30 rows')
  const fixture = applyScenario(options.scenario, baseline)
  writeFixtureEvent(runId, 'apply', options.scenario, fixture)
  const rawFile = path.resolve(options.raw || path.join(ASSET_DIR, `pra05-${options.scenario.toLowerCase()}-${runId}.ndjson`))
  const manifestFile = path.join(ASSET_DIR, `pra05-${options.scenario.toLowerCase()}-${runId}-manifest.json`)
  let valid = 0
  let attempted = 0
  const maxAttempts = Math.max(options.count, options.count * 2)
  let browser = null
  try {
    browser = await chromium.launch({ headless: true })
    const browserVersion = browser.version()
    atomicWrite(manifestFile, `${JSON.stringify({
      run_id: runId,
      scenario: options.scenario,
      count_requested: options.count,
      max_attempts: maxAttempts,
      batch_size: options.batchSize,
      frontend_base: FRONTEND_BASE,
      api_base: API_BASE,
      isolated_worktree: ISOLATED_WORKTREE,
      browser_version: browserVersion,
      environment_mode: 'production-build-local-isolated',
      browser_temperature: 'cold',
      server_temperature: 'warm',
      fixture,
      git_head: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: ISOLATED_WORKTREE, encoding: 'utf8' }).trim()
    }, null, 2)}\n`)
    while (valid < options.count && attempted < maxAttempts) {
      const batchSize = Math.min(options.batchSize, options.count - valid)
      for (let index = 0; index < batchSize; index += 1) {
        attempted += 1
        const warmProbe = await warmApi(SCENARIOS[options.scenario])
        const record = await sample(browser, options.scenario, `${options.scenario}-${String(attempted).padStart(2, '0')}`, runId, fixture, warmProbe)
        appendJson(rawFile, record)
        console.log(JSON.stringify({ sample_id: record.sample_id, valid: record.valid, failure_reason: record.failure_reason }))
        if (record.valid) valid += 1
        if (attempted >= maxAttempts || valid >= options.count) break
      }
    }
    if (valid < options.count) throw new Error(`valid sample target not met: ${valid}/${options.count}; ${attempted} attempts persisted at ${path.basename(rawFile)}`)
  } finally {
    if (browser) await browser.close().catch(() => undefined)
    const restored = restoreM30(baseline)
    writeFixtureEvent(runId, 'restore-m30', 'M30', restored)
  }
  console.log(JSON.stringify({ run_id: runId, scenario: options.scenario, valid, attempted, raw_file: path.basename(rawFile) }))
}

main().catch(error => {
  console.error(safeText(error.message))
  process.exitCode = 1
})
