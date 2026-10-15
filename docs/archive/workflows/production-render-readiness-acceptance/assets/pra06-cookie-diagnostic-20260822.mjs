#!/usr/bin/env node
import fs from 'node:fs'
import path from 'node:path'
import { execFileSync, spawnSync } from 'node:child_process'
import { createRequire } from 'node:module'

const ASSET_DIR = process.env.PRA_ASSET_DIR || path.dirname(new URL(import.meta.url).pathname)
const FRONTEND_BASE = process.env.PRA_FRONTEND_BASE || 'http://localhost:3102'
const API_BASE = process.env.PRA_API_BASE || 'http://api.localhost:8102'
const API_BIND = process.env.PRA_API_BIND || 'http://127.0.0.1:8102'
const SNAPSHOT = process.env.PRA_ISOLATED_WORKTREE
const PYTHON = process.env.PRA_ISOLATED_PYTHON || path.join(SNAPSHOT || '', 'backend/.pra06-venv/bin/python')
const DB_URL = process.env.DATABASE_URL
const USERNAME = process.env.PRA06_TEMP_USERNAME || 'pra06-cookie-diagnostic-admin'
const RUN_ID = process.env.PRA_RUN_ID || 'pra06-cookie-diagnostic-20260822'
const SAMPLE_ID = process.env.PRA_SAMPLE_ID || 'M30-cookie-diagnostic-01'
const RAW_FILE = path.join(ASSET_DIR, `${RUN_ID}.raw.ndjson`)
const MANIFEST_FILE = path.join(ASSET_DIR, `${RUN_ID}.manifest.json`)
const LOG_FILE = path.join(ASSET_DIR, `${RUN_ID}.log`)
const SEED_FILE = process.env.PRA_SEED_FILE || path.join(ASSET_DIR, `${RUN_ID}-seed.py`)

if (!SNAPSHOT || !DB_URL || !fs.existsSync(PYTHON)) throw new Error('isolated runtime inputs are missing')
const { chromium } = createRequire(path.join(SNAPSHOT, 'package.json'))('playwright')

function writeSync(file, value) {
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

function safeText(value) {
  return String(value || '')
    .replace(/(authorization|cookie|password|token|secret)\s*[:=]\s*[^\s]+/gi, '$1=[REDACTED]')
    .replace(/https?:\/\/[^\s)]+/g, value => {
      try {
        const url = new URL(value)
        return `${url.origin}${url.pathname}`
      } catch {
        return '[URL_REDACTED]'
      }
    })
    .slice(0, 1200)
}

function headersLower(headers) {
  const out = {}
  for (const [key, value] of Object.entries(headers || {})) out[String(key).toLowerCase()] = value
  return out
}

function cookieName(line) {
  const match = String(line || '').match(/^\s*([^=;\s]+)/)
  return match ? match[1] : null
}

function cookieAttributeSummary(line) {
  const text = String(line || '')
  const lower = text.toLowerCase()
  return {
    name: cookieName(text),
    header_present: text.length > 0,
    path_present: /(?:^|;)\s*path\s*=/i.test(text),
    domain_present: /(?:^|;)\s*domain\s*=/i.test(text),
    max_age_present: /(?:^|;)\s*max-age\s*=/i.test(text),
    expires_present: /(?:^|;)\s*expires\s*=/i.test(text),
    http_only_present: /(?:^|;)\s*httponly(?:;|$)/i.test(text),
    secure_present: /(?:^|;)\s*secure(?:;|$)/i.test(text),
    same_site_present: /(?:^|;)\s*samesite\s*=/i.test(text),
    same_site_lax_present: /(?:^|;)\s*samesite\s*=\s*lax(?:;|$)/i.test(text),
    raw_value_persisted: false,
    value_present: lower.includes('=')
  }
}

function summarizeSetCookie(headers) {
  const lower = headersLower(headers)
  const value = lower['set-cookie']
  const lines = Array.isArray(value) ? value : value ? [String(value)] : []
  return {
    header_present: lines.length > 0,
    header_count: lines.length,
    cookies: lines.map(cookieAttributeSummary),
    raw_value_persisted: false
  }
}

function summarizeCors(headers) {
  const lower = headersLower(headers)
  return {
    access_control_allow_origin: lower['access-control-allow-origin'] || null,
    access_control_allow_credentials: lower['access-control-allow-credentials'] || null,
    vary_origin: lower.vary ? String(lower.vary).toLowerCase().includes('origin') : false
  }
}

function summarizeBlocked(items) {
  if (!Array.isArray(items)) return []
  return items.map(item => {
    if (typeof item === 'string') return { reason: item }
    return {
      name: cookieName(item.cookieLine),
      blocked_reasons: item.blockedReasons || item.blockedReason || item.reason || [],
      raw_value_persisted: false
    }
  })
}

function isExpectedFailedRequest(request) {
  if (request.failure !== 'net::ERR_ABORTED') return false
  try {
    const url = new URL(request.url)
    if (url.hostname === 'www.google-analytics.com' && url.pathname === '/g/collect') return true
    if (url.origin === FRONTEND_BASE && /^\/(?:notes|blog)\//.test(url.pathname)) return true
  } catch {}
  return false
}

function isExpectedConsoleError(message) {
  return /^Failed to load resource: the server responded with a status of 401 \(Unauthorized\)$/.test(String(message || '').trim())
}

function runSeed(command) {
  const result = spawnSync(PYTHON, [SEED_FILE, command, USERNAME], {
    cwd: path.join(SNAPSHOT, 'backend'),
    env: { ...process.env, DATABASE_URL: DB_URL, PYTHONPATH: path.join(SNAPSHOT, 'backend') },
    encoding: 'utf8',
    maxBuffer: 1024 * 1024
  })
  if (result.status !== 0) {
    throw new Error(`seed-${command}-failed:exit-${result.status}`)
  }
  return JSON.parse(result.stdout.trim())
}

function endpoint(url) {
  try {
    const parsed = new URL(url)
    return `${parsed.origin}${parsed.pathname}`
  } catch {
    return safeText(url)
  }
}

function endpointKind(url, method = 'GET') {
  const value = endpoint(url)
  if (value.endsWith('/api/auth/login')) return method === 'POST' ? 'login_post' : 'login_preflight'
  if (value.endsWith('/api/auth/me')) return 'me'
  if (value.endsWith('/api/admin/dashboard/summary')) return 'strict_management'
  if (value.includes('/api/notes')) return 'management_list'
  return null
}

async function main() {
  const mainHead = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: SNAPSHOT, encoding: 'utf8' }).trim()
  const manifest = {
    run_id: RUN_ID,
    status: 'in_progress',
    purpose: 'single normal browser login cookie propagation diagnosis',
    source_head: mainHead,
    snapshot_worktree: SNAPSHOT,
    frontend_base: FRONTEND_BASE,
    api_base: API_BASE,
    api_bind: API_BIND,
    login_url: `${API_BASE}/api/auth/login`,
    origin: FRONTEND_BASE,
    runtime: {
      next_public_api_url: API_BASE,
      allowed_origins: FRONTEND_BASE,
      auth_bypass: false,
      auth_bypass_allow: false
    },
    fixture: { profile: 'M30', setup: 'in_progress', temporary_admin_username: USERNAME, password_persisted: false },
    probe: {
      normal_login_attempts: 1,
      ten_sample_run: process.env.PRA_M30_BATCH === 'true',
      performance_baseline: false,
      production_readiness_claim: false,
      password_token_cookie_values_persisted: false
    },
    started_at: new Date().toISOString()
  }
  writeSync(MANIFEST_FILE, `${JSON.stringify(manifest, null, 2)}\n`)
  const fixture = runSeed('prepare')
  manifest.fixture = { ...fixture.fixture, temporary_admin_username: USERNAME, password_persisted: false }
  writeSync(MANIFEST_FILE, `${JSON.stringify(manifest, null, 2)}\n`)

  const browser = await chromium.launch({ headless: true })
  const browserVersion = browser.version()
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'zh-CN' })
  const page = await context.newPage()
  const cdp = await context.newCDPSession(page)
  await cdp.send('Network.enable')

  const requestMeta = new Map()
  const responseMeta = new Map()
  const requestEvents = []
  const responseEvents = []
  const extraRequestEvents = []
  const extraResponseEvents = []
  const consoleErrors = []
  const pageErrors = []
  const failedRequests = []
  const unexpectedNavigations = []
  const dialogs = []
  const downloads = []
  const directStrict = { status: null, error: null }
  let navigationStatus = null
  let navigationError = null

  cdp.on('Network.requestWillBeSent', event => {
    const kind = endpointKind(event.request?.url, event.request?.method)
    requestMeta.set(event.requestId, { url: event.request?.url, method: event.request?.method, kind })
    if (kind) requestEvents.push({
      kind,
      url: endpoint(event.request.url),
      method: event.request.method,
      request_id: event.requestId
    })
  })
  cdp.on('Network.requestWillBeSentExtraInfo', event => {
    const meta = requestMeta.get(event.requestId)
    if (!meta?.kind) return
    const headers = headersLower(event.headers)
    extraRequestEvents.push({
      kind: meta.kind,
      url: endpoint(meta.url),
      method: meta.method,
      origin: headers.origin || null,
      cookie_header_present: Boolean(headers.cookie),
      raw_cookie_value_persisted: false
    })
  })
  cdp.on('Network.responseReceived', event => {
    const request = requestMeta.get(event.requestId)
    const kind = endpointKind(event.response?.url, request?.method)
    responseMeta.set(event.requestId, { url: event.response?.url, kind, status: event.response?.status })
    if (kind) responseEvents.push({
      kind,
      url: endpoint(event.response.url),
      status: event.response.status,
      headers: summarizeCors(event.response.headers)
    })
  })
  cdp.on('Network.responseReceivedExtraInfo', event => {
    const meta = responseMeta.get(event.requestId) || requestMeta.get(event.requestId)
    if (!meta?.kind) return
    const headers = headersLower(event.headers)
    extraResponseEvents.push({
      kind: meta.kind,
      url: endpoint(meta.url),
      status: event.statusCode ?? meta.status ?? null,
      cors: summarizeCors(headers),
      set_cookie: summarizeSetCookie(headers),
      blocked_set_cookie: summarizeBlocked(event.blockedSetCookieWithReason || event.blockedSetCookieReasons),
      exempted_set_cookie: summarizeBlocked(event.exemptedSetCookieWithReason),
      raw_cookie_value_persisted: false
    })
  })
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(safeText(message.text())) })
  page.on('pageerror', error => pageErrors.push(safeText(error.message)))
  page.on('requestfailed', request => {
    failedRequests.push({ url: endpoint(request.url()), method: request.method(), failure: safeText(request.failure()?.errorText) })
  })
  page.on('framenavigated', frame => {
    if (frame !== page.mainFrame()) return
    try {
      const current = new URL(frame.url())
      if (current.pathname !== '/manage' && current.pathname !== '/manage/') {
        unexpectedNavigations.push(`${current.origin}${current.pathname}`)
      }
    } catch (error) {
      unexpectedNavigations.push(safeText(frame.url()))
    }
  })
  page.on('dialog', async dialog => {
    dialogs.push({ type: dialog.type(), message: safeText(dialog.message()) })
    await dialog.dismiss()
  })
  page.on('download', download => {
    downloads.push({ suggested_filename: safeText(download.suggestedFilename()) })
  })

  try {
    const navigation = await page.goto(`${FRONTEND_BASE}/manage`, { waitUntil: 'domcontentloaded', timeout: 15000 })
    navigationStatus = navigation?.status() ?? null
  } catch (error) {
    navigationError = safeText(error.message)
  }

  let loginFormFound = false
  let clickError = null
  try {
    await page.getByLabel('用户名').waitFor({ state: 'visible', timeout: 10000 })
    loginFormFound = true
    await page.getByLabel('用户名').fill(USERNAME)
    await page.getByLabel('密码').fill(fixture.password)
    await page.getByRole('button', { name: '密码登录' }).click()
  } catch (error) {
    clickError = safeText(error.message)
  }

  await page.waitForTimeout(3500)
  try {
    directStrict.status = await page.evaluate(async apiBase => {
      const response = await fetch(`${apiBase}/api/admin/dashboard/summary`, { credentials: 'include' })
      return response.status
    }, API_BASE)
  } catch (error) {
    directStrict.error = safeText(error.message)
  }
  await page.waitForTimeout(1000)

  const evidence = await page.evaluate(() => {
    const nodes = Array.from(document.querySelectorAll('[data-render-state]'))
    const marks = performance.getEntriesByType('mark').map(entry => ({ name: entry.name, start: entry.startTime, duration: entry.duration }))
    const navigation = performance.getEntriesByType('navigation')[0]
    const lcpEntries = performance.getEntriesByType('largest-contentful-paint')
    const resources = performance.getEntriesByType('resource')
      .filter(entry => entry.name.includes('/api/'))
      .map(entry => ({
        url: entry.name,
        start: entry.startTime,
        responseEnd: entry.responseEnd,
        duration: entry.duration
      }))
    const mark = name => marks.filter(entry => entry.name === name)
    const main = nodes.find(node => node.tagName.toLowerCase() === 'main')
    return {
      navigation_timing: navigation ? {
        ttfb: navigation.responseStart - navigation.startTime,
        dom_content_loaded: navigation.domContentLoadedEventEnd,
        load: navigation.loadEventEnd,
        duration: navigation.duration
      } : null,
      lcp: lcpEntries.length ? lcpEntries[lcpEntries.length - 1].startTime : null,
      resource_timings: resources,
      dom: {
        selector: '[data-render-state]',
        selector_count: nodes.length,
        main_count: nodes.filter(node => node.tagName.toLowerCase() === 'main').length,
        state: main?.getAttribute('data-render-state') || null,
        management_row_count: document.querySelectorAll('tbody tr').length
      },
      marks: {
        auth_submit: mark('manage:auth-submit'),
        content_ready: mark('manage:content-ready')
      },
      url: location.href
    }
  })
  // The session cookie is scoped to /api; querying the API origin root does not
  // return path-scoped cookies in Playwright. Query a matching API path and
  // keep the raw cookie value out of persisted evidence.
  const cookies = await context.cookies(`${API_BASE}/api/auth/me`)
  const sessionCookies = cookies.filter(cookie => cookie.name === 'admin_session').map(cookie => ({
    name: cookie.name,
    domain: cookie.domain,
    path: cookie.path,
    http_only: cookie.httpOnly,
    secure: cookie.secure,
    same_site: cookie.sameSite,
    expires_present: Number.isFinite(cookie.expires) && cookie.expires > 0,
    value_present: Boolean(cookie.value),
    raw_value_persisted: false
  }))

  const loginResponses = responseEvents.filter(event => event.kind === 'login_post')
  const loginPreflightResponses = responseEvents.filter(event => event.kind === 'login_preflight')
  const loginExtra = extraResponseEvents.filter(event => event.kind === 'login_post')
  const meResponses = responseEvents.filter(event => event.kind === 'me')
  const strictResponses = responseEvents.filter(event => event.kind === 'strict_management')
  const meRequests = extraRequestEvents.filter(event => event.kind === 'me')
  const strictRequests = extraRequestEvents.filter(event => event.kind === 'strict_management')
  const expectedConsoleErrors = consoleErrors.filter(isExpectedConsoleError)
  const unexpectedConsoleErrors = consoleErrors.filter(error => !isExpectedConsoleError(error))
  const expectedFailedRequests = failedRequests.filter(isExpectedFailedRequest)
  const unexpectedFailedRequests = failedRequests.filter(request => !isExpectedFailedRequest(request))
  const reasons = []
  if (navigationError) reasons.push(`navigation:${navigationError}`)
  if (navigationStatus !== 200) reasons.push(`navigation-status:${navigationStatus ?? 'missing'}`)
  if (!loginFormFound) reasons.push('login-form:missing')
  if (clickError) reasons.push(`login-submit:${clickError}`)
  if (!loginResponses.some(event => event.status === 200)) reasons.push(`login-post-status:${loginResponses.map(event => event.status).join(',') || 'missing'}`)
  if (!meResponses.some(event => event.status === 200)) reasons.push(`me-status:${meResponses.map(event => event.status).join(',') || 'missing'}`)
  if (!strictResponses.some(event => event.status === 200) && directStrict.status !== 200) reasons.push(`strict-management-status:${strictResponses.map(event => event.status).join(',') || directStrict.status || 'missing'}`)
  if (!sessionCookies.length) reasons.push('cookie-jar:admin_session-absent')
  if (sessionCookies.length && !sessionCookies.some(cookie => cookie.http_only)) reasons.push('cookie-jar:admin_session-not-httponly')
  if (!evidence.dom.main_count || evidence.dom.state !== 'ready') reasons.push(`readiness-dom:${evidence.dom.main_count}:${evidence.dom.state || 'missing'}`)
  if (!evidence.marks.content_ready.length) reasons.push('readiness-mark:manage-content-ready-missing')
  if (unexpectedConsoleErrors.length) reasons.push('console-errors')
  if (pageErrors.length) reasons.push('page-errors')
  if (unexpectedFailedRequests.length) reasons.push('failed-requests')
  if (unexpectedNavigations.length) reasons.push('unexpected-navigation')
  if (dialogs.length) reasons.push('dialogs')
  if (downloads.length) reasons.push('downloads')

  const raw = {
    run_id: RUN_ID,
    sample_id: SAMPLE_ID,
    sample_status: reasons.length ? 'failed' : 'valid',
    valid: reasons.length === 0,
    browser_temperature: 'cold',
    server_temperature: 'warm',
    browser_version: browserVersion,
    environment_mode: 'production-build-local-isolated',
    frontend_base: FRONTEND_BASE,
    api_base: API_BASE,
    login_url: `${API_BASE}/api/auth/login`,
    origin: FRONTEND_BASE,
    fixture: fixture.fixture,
    navigation: {
      url: `${FRONTEND_BASE}/manage`,
      status: navigationStatus,
      error: navigationError,
      ...(evidence.navigation_timing || {})
    },
    lcp: evidence.lcp,
    api_timings: evidence.resource_timings,
    login_response: loginResponses,
    login_preflight_response: loginPreflightResponses,
    login_response_extra_info: loginExtra,
    me_responses: meResponses,
    strict_management_responses: strictResponses,
    direct_same_context_strict_management: directStrict,
    request_cookie_presence: {
      me: meRequests,
      strict_management: strictRequests,
      raw_cookie_value_persisted: false
    },
    browser_cookie_jar: {
      admin_session_present: sessionCookies.length > 0,
      cookies: sessionCookies,
      raw_cookie_value_persisted: false
    },
    readiness: evidence,
    console_errors: consoleErrors,
    expected_console_errors: expectedConsoleErrors,
    unexpected_console_errors: unexpectedConsoleErrors,
    page_errors: pageErrors,
    failed_requests: failedRequests,
    expected_failed_requests: expectedFailedRequests,
    unexpected_failed_requests: unexpectedFailedRequests,
    unexpected_navigations: unexpectedNavigations,
    dialogs,
    downloads,
    failure_reason: reasons.length ? reasons.join('; ') : null,
    password_token_cookie_values_persisted: false,
    recorded_at: new Date().toISOString()
  }
  appendJson(RAW_FILE, raw)
  writeSync(LOG_FILE, [
    `run_id=${RUN_ID}`,
    `normal_login_attempts=1`,
    `login_post_status=${loginResponses.map(event => event.status).join(',') || 'missing'}`,
    `me_status=${meResponses.map(event => event.status).join(',') || 'missing'}`,
    `strict_management_status=${strictResponses.map(event => event.status).join(',') || directStrict.status || 'missing'}`,
    `admin_session_cookie_jar_present=${sessionCookies.length > 0}`,
    `set_cookie_attribute_evidence_present=${loginExtra.some(event => event.set_cookie.header_present)}`,
    `blocked_set_cookie_reason_count=${loginExtra.reduce((sum, event) => sum + event.blocked_set_cookie.length, 0)}`,
    `request_cookie_header_presence=${JSON.stringify({ me: meRequests.map(event => event.cookie_header_present), strict_management: strictRequests.map(event => event.cookie_header_present) })}`,
    `expected_console_error_count=${expectedConsoleErrors.length}`,
    `unexpected_console_error_count=${unexpectedConsoleErrors.length}`,
    `expected_failed_request_count=${expectedFailedRequests.length}`,
    `unexpected_failed_request_count=${unexpectedFailedRequests.length}`,
    `failure_reason=${raw.failure_reason || 'none'}`,
    `password_token_cookie_values_persisted=false`,
    `ten_sample_run=false`,
    `performance_baseline=false`,
    `production_readiness_claim=false`,
    ''
  ].join('\n'))
  manifest.status = raw.valid ? 'pass' : 'fail'
  manifest.browser_version = browserVersion
  manifest.ended_at = new Date().toISOString()
  manifest.result = {
    sample_id: raw.sample_id,
    valid: raw.valid,
    failure_reason: raw.failure_reason,
    login_post_statuses: loginResponses.map(event => event.status),
    me_statuses: meResponses.map(event => event.status),
    strict_management_statuses: strictResponses.map(event => event.status),
    admin_session_cookie_jar_present: sessionCookies.length > 0,
    login_set_cookie_attribute_evidence_present: loginExtra.some(event => event.set_cookie.header_present),
    blocked_set_cookie_reason_count: loginExtra.reduce((sum, event) => sum + event.blocked_set_cookie.length, 0),
    request_cookie_header_presence: { me: meRequests.map(event => event.cookie_header_present), strict_management: strictRequests.map(event => event.cookie_header_present) },
    readiness_dom_state: evidence.dom.state,
    readiness_marks: { auth_submit: evidence.marks.auth_submit.length, content_ready: evidence.marks.content_ready.length }
  }
  writeSync(MANIFEST_FILE, `${JSON.stringify(manifest, null, 2)}\n`)
  await context.close()
  await browser.close()
  runSeed('disable')
  console.log(JSON.stringify({ run_id: RUN_ID, valid: raw.valid, failure_reason: raw.failure_reason }))
  if (!raw.valid) process.exitCode = 2
}

main().catch(error => {
  writeSync(LOG_FILE, `${safeText(error.message)}\n`)
  process.exitCode = 1
})
