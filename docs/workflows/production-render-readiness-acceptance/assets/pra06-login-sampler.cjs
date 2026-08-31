#!/usr/bin/env node
'use strict'

const crypto = require('node:crypto')
const fs = require('node:fs')
const path = require('node:path')
const { execFileSync, spawnSync } = require('node:child_process')
const { createRequire } = require('node:module')

const ASSET_DIR = __dirname
const REPO_ROOT = path.resolve(ASSET_DIR, '../../../..')
const FRONTEND_BASE = process.env.PRA_FRONTEND_BASE || 'http://localhost:3100'
const API_BASE = process.env.PRA_API_BASE || 'http://api.localhost:8100'
const DB_HOST = process.env.PRA_DB_HOST || '127.0.0.1'
const DB_PORT = process.env.PRA_DB_PORT || '55432'
const DB_NAME = process.env.PRA_DB_NAME || 'pra_f4'
const DB_USER = process.env.PRA_DB_USER || 'pra04'
const TEMP_ADMIN_USERNAME = process.env.PRA06_TEMP_USERNAME || 'pra04-admin'
const ISOLATED_WORKTREE = process.env.PRA_ISOLATED_WORKTREE || '/private/tmp/pra04-20260822-auWgUg/worktree'
const ISOLATED_PYTHON = process.env.PRA_ISOLATED_PYTHON || path.join(ISOLATED_WORKTREE, 'backend/.pra04-venv/bin/python')
const PLAYWRIGHT_ROOT = process.env.PRA_PLAYWRIGHT_ROOT || ISOLATED_WORKTREE
const RAW_FILE = path.resolve(process.env.PRA06_RAW || path.join(ASSET_DIR, 'pra06-login-raw.ndjson'))
const NEGATIVE_FILE = path.resolve(process.env.PRA06_NEGATIVE || path.join(ASSET_DIR, 'pra06-negative-probe.json'))

if (!fs.existsSync(ISOLATED_PYTHON)) throw new Error('isolated Python runtime is missing')
if (!fs.existsSync(path.join(PLAYWRIGHT_ROOT, 'package.json')) || !fs.existsSync(path.join(PLAYWRIGHT_ROOT, 'node_modules'))) throw new Error('isolated Playwright dependency tree is missing')

const { chromium } = createRequire(path.join(PLAYWRIGHT_ROOT, 'package.json'))('playwright')

function args() {
  const out = { count: 10, batchSize: 2, maxAttempts: 15, runId: null }
  for (let i = 2; i < process.argv.length; i += 1) {
    const value = process.argv[i]
    if (value.startsWith('--count=')) out.count = Number(value.slice(8))
    else if (value.startsWith('--batch-size=')) out.batchSize = Number(value.slice(13))
    else if (value.startsWith('--max-attempts=')) out.maxAttempts = Number(value.slice(15))
    else if (value.startsWith('--run-id=')) out.runId = value.slice(9)
  }
  return out
}

function safeText(value) {
  return String(value || '')
    .replace(/(authorization|cookie|password|token|secret)\s*[:=]\s*[^\s]+/gi, '$1=[REDACTED]')
    .replace(/https?:\/\/[^\s/@]+:[^\s/@]+@/gi, 'http://[REDACTED]@')
    .replace(/file:\/\/[^\s)]+/g, 'file://[REDACTED]')
    .slice(0, 1000)
}

function safeUrl(value) {
  try {
    const url = new URL(value)
    return `${url.pathname}${url.search}`
  } catch {
    return safeText(value)
  }
}

function fsyncWrite(file, value) {
  const tmp = `${file}.tmp-${process.pid}`
  const fd = fs.openSync(tmp, 'w', 0o600)
  try {
    fs.writeSync(fd, value, null, 'utf8')
    fs.fsyncSync(fd)
  } finally {
    fs.closeSync(fd)
  }
  fs.renameSync(tmp, file)
}

function appendJson(file, value) {
  const fd = fs.openSync(file, 'a', 0o600)
  try {
    fs.writeSync(fd, `${JSON.stringify(value)}\n`, null, 'utf8')
    fs.fsyncSync(fd)
  } finally {
    fs.closeSync(fd)
  }
}

function psql(sql) {
  return execFileSync('psql', ['-X', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, '-d', DB_NAME, '-At', '-F', '\t', '-c', sql], {
    cwd: REPO_ROOT,
    encoding: 'utf8',
    env: { ...process.env, PGPASSWORD: '' },
    stdio: ['ignore', 'pipe', 'pipe']
  }).trim()
}

function fixtureSummary() {
  const output = psql("select count(*)::int, count(*) filter (where status='published' and hidden=false)::int, count(*) filter (where status='published' and hidden=true)::int, count(*) filter (where status='draft')::int, count(*) filter (where slug='pra04-d1' and status='published' and hidden=false)::int from notes")
  const [total, publicVisible, publishedHidden, drafts, d1Public] = output.split('\t').map(Number)
  return { total, public_visible: publicVisible, published_hidden: publishedHidden, drafts, d1_public: d1Public === 1 }
}

function rotateTemporaryPassword(password) {
  const code = `
import asyncio, os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.models.note import User
from app.utils.auth import hash_password

async def main():
    engine = create_async_engine(os.environ['DATABASE_URL'])
    try:
        async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
            result = await session.execute(select(User).where(User.username == os.environ['PRA06_TEMP_USERNAME']))
            user = result.scalar_one_or_none()
            if user is None:
                raise RuntimeError('temporary admin not found')
            user.password_hash = hash_password(os.environ['PRA06_TEMP_PASSWORD'])
            user.is_admin = True
            await session.commit()
    finally:
        await engine.dispose()

asyncio.run(main())
`
  const result = spawnSync(ISOLATED_PYTHON, ['-c', code], {
    cwd: REPO_ROOT,
    encoding: 'utf8',
    env: {
      ...process.env,
      PYTHONPATH: path.join(ISOLATED_WORKTREE, 'backend'),
      DATABASE_URL: `postgresql+asyncpg://${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}`,
      PRA06_TEMP_USERNAME: TEMP_ADMIN_USERNAME,
      PRA06_TEMP_PASSWORD: password
    },
    stdio: ['ignore', 'ignore', 'ignore']
  })
  if (result.error || result.status !== 0) throw new Error('temporary admin password rotation failed')
}

function initScript() {
  return () => {
    window.__pra06ApiEvents = []
    const originalFetch = window.fetch.bind(window)
    window.fetch = async (input, init) => {
      const url = typeof input === 'string' ? input : input.url
      const method = init?.method || (typeof input === 'string' ? 'GET' : input.method) || 'GET'
      const isApi = url.includes('/api/')
      const started = performance.now()
      try {
        const response = await originalFetch(input, init)
        const responseEnd = performance.now()
        if (isApi) window.__pra06ApiEvents.push({ url, method, status: response.status, start: started, responseEnd, duration: responseEnd - started })
        return response
      } catch (error) {
        const responseEnd = performance.now()
        if (isApi) window.__pra06ApiEvents.push({ url, method, status: 0, start: started, responseEnd, duration: responseEnd - started, error: safeClientText(String(error)) })
        throw error
      }
    }
    function safeClientText(value) {
      return String(value).replace(/(authorization|cookie|password|token|secret)\s*[:=]\s*[^\s]+/gi, '$1=[REDACTED]').slice(0, 300)
    }
  }
}

function eventPath(event) {
  return safeUrl(event.url)
}

function apiEvent(event) {
  return {
    url: eventPath(event),
    method: event.method,
    status: event.status,
    start: event.start,
    responseEnd: event.responseEnd,
    duration: event.duration,
    ...(event.error ? { error: safeText(event.error) } : {})
  }
}

async function evaluateEvidence(page) {
  return page.evaluate(() => {
    const nodes = [...document.querySelectorAll('[data-render-state]')]
    const node = nodes[0]
    const main = node?.tagName.toLowerCase() === 'main' ? node : null
    const nav = performance.getEntriesByType('navigation')[0]
    const lcpEntries = performance.getEntriesByType('largest-contentful-paint')
    const markEntries = name => performance.getEntriesByName(name, 'mark').map(entry => ({ name: entry.name, start: entry.startTime, duration: entry.duration }))
    const apiEvents = (window.__pra06ApiEvents || []).map(event => ({ ...event, url: new URL(event.url, location.href).pathname + new URL(event.url, location.href).search }))
    return {
      navigation: nav ? { ttfb: nav.responseStart - nav.startTime, dom_content_loaded: nav.domContentLoadedEventEnd, load: nav.loadEventEnd, duration: nav.duration } : null,
      lcp: lcpEntries.length ? lcpEntries[lcpEntries.length - 1].startTime : null,
      marks: { auth_submit: markEntries('manage:auth-submit'), content_ready: markEntries('manage:content-ready') },
      api_events: apiEvents,
      dom: {
        selector: '[data-render-state]',
        selector_count: nodes.length,
        tag_name: node?.tagName.toLowerCase() || null,
        state: node?.getAttribute('data-render-state') || null,
        list_row_count: main?.querySelectorAll('tbody tr').length || 0,
        table_count: main?.querySelectorAll('table').length || 0,
        heading_count: main?.querySelectorAll('h1,h2,h3').length || 0,
        text_length: main?.textContent?.length || 0
      }
    }
  })
}

function markTiming(marks) {
  const auth = marks.auth_submit[0] || null
  const ready = marks.content_ready[0] || null
  return {
    auth_submit: auth,
    content_ready: ready,
    login_to_content_ready: auth && ready ? ready.start - auth.start : null
  }
}

function requiredApiEvents(events) {
  const login = events.filter(event => event.url.startsWith('/api/auth/login') && event.method === 'POST')
  const me = events.filter(event => event.url.startsWith('/api/auth/me') && event.method === 'GET')
  const management = events.filter(event => event.url.startsWith('/api/notes?') && event.url.includes('size=30') && event.method === 'GET')
  return { login, me, management }
}

async function sample(browser, sampleId, runId, browserVersion, fixture) {
  const startedAt = new Date().toISOString()
  const targetUrl = `${FRONTEND_BASE}/manage`
  const consoleErrors = []
  const pageErrors = []
  const failedRequests = []
  const unexpectedNavigations = []
  const dialogs = []
  const downloads = []
  let context
  let page
  const reasons = []
  try {
    context = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'zh-CN' })
    await context.addInitScript(initScript())
    page = await context.newPage()
    page.on('console', message => { if (message.type() === 'error') consoleErrors.push(safeText(message.text())) })
    page.on('pageerror', error => pageErrors.push(safeText(error.message)))
    page.on('requestfailed', request => failedRequests.push({ url: safeUrl(request.url()), method: request.method(), failure: safeText(request.failure()?.errorText) }))
    page.on('framenavigated', frame => {
      if (frame === page.mainFrame()) {
        const current = frame.url()
        const currentPath = safeUrl(current)
        if (currentPath !== '/manage' && currentPath !== '/manage/') unexpectedNavigations.push(currentPath)
      }
    })
    page.on('dialog', async dialog => { dialogs.push({ type: dialog.type(), message: safeText(dialog.message()) }); await dialog.dismiss() })
    page.on('download', download => downloads.push({ suggested_filename: safeText(download.suggestedFilename()) }))

    let navigationResponse
    try { navigationResponse = await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 10000 }) }
    catch (error) { reasons.push(`navigation:${safeText(error.message)}`) }
    if (navigationResponse && navigationResponse.status() !== 200) reasons.push(`navigation-status:${navigationResponse.status()}`)

    try {
      await page.getByLabel('用户名').waitFor({ state: 'visible', timeout: 10000 })
      await page.getByLabel('用户名').fill(TEMP_ADMIN_USERNAME)
      await page.getByLabel('密码').fill(process.env.PRA06_RUNTIME_PASSWORD)
      await page.getByRole('button', { name: '密码登录' }).click()
    } catch (error) { reasons.push(`auth-submit:${safeText(error.message)}`) }

    try {
      await page.waitForFunction(() => {
        const nodes = document.querySelectorAll('[data-render-state]')
        return nodes.length === 1 && nodes[0].tagName.toLowerCase() === 'main' && nodes[0].getAttribute('data-render-state') === 'ready' && performance.getEntriesByName('manage:content-ready', 'mark').length >= 1
      }, { timeout: 15000 })
    } catch (error) { reasons.push(`readiness:${safeText(error.message)}`) }

    const evidence = await evaluateEvidence(page)
    const cookies = await context.cookies(API_BASE)
    const sessionCookie = cookies.find(cookie => cookie.name === 'admin_session')
    const events = evidence.api_events.map(apiEvent)
    const required = requiredApiEvents(events)
    const timing = markTiming(evidence.marks)
    const me200 = required.me.filter(event => event.status === 200)

    if (required.login.length !== 1 || required.login[0].status !== 200) reasons.push(`login-api:${required.login.length ? required.login.map(event => event.status).join(',') : 'missing'}`)
    if (me200.length !== 1) reasons.push(`me-api-200:${me200.length}`)
    if (required.management.length !== 1 || required.management[0].status !== 200) reasons.push(`manage-api:${required.management.length ? required.management.map(event => event.status).join(',') : 'missing'}`)
    if (!sessionCookie || sessionCookie.httpOnly !== true) reasons.push('admin-session-not-httponly')
    if (evidence.dom.selector_count !== 1 || evidence.dom.tag_name !== 'main') reasons.push(`dom-selector:${evidence.dom.selector_count}:${evidence.dom.tag_name || 'missing'}`)
    if (evidence.dom.state !== 'ready') reasons.push(`dom-state:${evidence.dom.state || 'missing'}`)
    if (evidence.dom.list_row_count !== 30) reasons.push(`m30-row-count:${evidence.dom.list_row_count}`)
    if (evidence.marks.auth_submit.length !== 1) reasons.push(`auth-submit-mark-count:${evidence.marks.auth_submit.length}`)
    if (evidence.marks.content_ready.length !== 1) reasons.push(`content-ready-mark-count:${evidence.marks.content_ready.length}`)
    if (consoleErrors.length) reasons.push('console-errors')
    if (pageErrors.length) reasons.push('page-errors')
    if (failedRequests.length) reasons.push('failed-requests')
    if (unexpectedNavigations.length) reasons.push('unexpected-navigation')
    if (dialogs.length) reasons.push('dialogs')
    if (downloads.length) reasons.push('downloads')

    return {
      run_id: runId,
      sample_id: sampleId,
      scenario: 'M30-admin-login',
      sample_status: reasons.length ? 'failed' : 'valid',
      valid: reasons.length === 0,
      browser_temperature: 'cold',
      server_temperature: 'warm',
      browser_version: browserVersion,
      environment_mode: 'production-build-local-isolated',
      base_url: FRONTEND_BASE,
      api_base: API_BASE,
      navigation_url: targetUrl,
      started_at: startedAt,
      ended_at: new Date().toISOString(),
      fixture,
      navigation: evidence.navigation ? { ...evidence.navigation, response_status: navigationResponse?.status() || null } : null,
      lcp: evidence.lcp,
      readiness: timing,
      api: { login: required.login, me: required.me, management_list: required.management },
      api_requests: events,
      auth: { login_post_status: required.login[0]?.status || null, me_200_status: me200[0]?.status || null, admin_session_httponly: sessionCookie?.httpOnly === true },
      dom: evidence.dom,
      console_errors: consoleErrors,
      page_errors: pageErrors,
      failed_requests: failedRequests,
      unexpected_navigations: unexpectedNavigations,
      dialogs,
      downloads,
      request_count: events.length,
      failure_reason: reasons.length ? reasons.join('; ') : null
    }
  } catch (error) {
    return {
      run_id: runId,
      sample_id: sampleId,
      scenario: 'M30-admin-login',
      sample_status: 'failed',
      valid: false,
      browser_temperature: 'cold',
      server_temperature: 'warm',
      browser_version: browserVersion,
      environment_mode: 'production-build-local-isolated',
      base_url: FRONTEND_BASE,
      api_base: API_BASE,
      navigation_url: targetUrl,
      started_at: startedAt,
      ended_at: new Date().toISOString(),
      fixture,
      navigation: null,
      lcp: null,
      readiness: { auth_submit: null, content_ready: null, login_to_content_ready: null },
      api: { login: [], me: [], management_list: [] },
      api_requests: [],
      auth: { login_post_status: null, me_200_status: null, admin_session_httponly: false },
      dom: { selector: '[data-render-state]', selector_count: null, tag_name: null, state: null, list_row_count: null },
      console_errors: consoleErrors,
      page_errors: pageErrors,
      failed_requests: failedRequests,
      unexpected_navigations: unexpectedNavigations,
      dialogs,
      downloads,
      request_count: 0,
      failure_reason: `harness:${safeText(error.message)}`
    }
  } finally {
    if (context) await context.close().catch(() => undefined)
  }
}

async function negativeProbe(browser, runId, browserVersion) {
  const reasons = []
  let context
  let page
  try {
    context = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'zh-CN' })
    page = await context.newPage()
    const navigationResponse = await page.goto(`${FRONTEND_BASE}/manage`, { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.getByLabel('用户名').fill(TEMP_ADMIN_USERNAME)
    await page.getByLabel('密码').fill(process.env.PRA06_RUNTIME_PASSWORD)
    await page.getByRole('button', { name: '密码登录' }).click()
    await page.waitForFunction(() => document.querySelectorAll('[data-render-state="ready"]').length === 1, { timeout: 15000 })
    const result = await page.evaluate(async apiBase => {
      const logout = await fetch(`${apiBase}/api/auth/logout`, { method: 'POST', credentials: 'include' })
      const me = await fetch(`${apiBase}/api/auth/me`, { credentials: 'include' })
      const strictManagement = await fetch(`${apiBase}/api/admin/dashboard/summary`, { credentials: 'include' })
      const publicRead = await fetch(`${apiBase}/api/notes?status=published&page=1&size=20`, { credentials: 'include' })
      return { logout: logout.status, me: me.status, strict_management: strictManagement.status, public_read: publicRead.status }
    }, API_BASE)
    const cookies = await context.cookies(API_BASE)
    const hasSessionCookie = cookies.some(cookie => cookie.name === 'admin_session')
    if (result.logout !== 200) reasons.push(`logout:${result.logout}`)
    if (result.me !== 401) reasons.push(`me-after-logout:${result.me}`)
    if (result.strict_management !== 401) reasons.push(`strict-management:${result.strict_management}`)
    if (result.public_read !== 200) reasons.push(`public-read:${result.public_read}`)
    if (hasSessionCookie) reasons.push('session-cookie-remains-after-logout')
    return {
      run_id: runId,
      probe: 'logout-invalid-session-boundary',
      valid: reasons.length === 0,
      browser_version: browserVersion,
      environment_mode: 'production-build-local-isolated',
      base_url: FRONTEND_BASE,
      api_base: API_BASE,
      navigation_status: navigationResponse?.status() || null,
      authenticated_before_logout: true,
      logout_status: result.logout,
      no_cookie_after_logout: !hasSessionCookie,
      rejected: { auth_me_status: result.me, strict_management_status: result.strict_management },
      public_reads_allowed: { notes_list_status: result.public_read },
      failure_reason: reasons.length ? reasons.join('; ') : null,
      recorded_at: new Date().toISOString()
    }
  } catch (error) {
    return {
      run_id: runId,
      probe: 'logout-invalid-session-boundary',
      valid: false,
      browser_version: browserVersion,
      environment_mode: 'production-build-local-isolated',
      base_url: FRONTEND_BASE,
      api_base: API_BASE,
      navigation_status: null,
      authenticated_before_logout: false,
      logout_status: null,
      no_cookie_after_logout: null,
      rejected: { auth_me_status: null, strict_management_status: null },
      public_reads_allowed: { notes_list_status: null },
      failure_reason: `harness:${safeText(error.message)}`,
      recorded_at: new Date().toISOString()
    }
  } finally {
    if (context) await context.close().catch(() => undefined)
  }
}

async function main() {
  const options = args()
  if (!Number.isInteger(options.count) || options.count < 1 || options.count > 10) throw new Error('--count must be 1..10')
  if (!Number.isInteger(options.batchSize) || options.batchSize < 1 || options.batchSize > 3) throw new Error('--batch-size must be 1..3')
  if (!Number.isInteger(options.maxAttempts) || options.maxAttempts < options.count || options.maxAttempts > 20) throw new Error('--max-attempts must be count..20')
  const runId = options.runId || `pra06-${new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)}`
  const fixture = fixtureSummary()
  if (fixture.total !== 30 || fixture.public_visible !== 20 || fixture.published_hidden !== 5 || fixture.drafts !== 5 || !fixture.d1_public) throw new Error(`M30 precondition failed: ${JSON.stringify(fixture)}`)
  if (process.env.AUTH_BYPASS === 'true' || process.env.AUTH_BYPASS_ALLOW === 'true') throw new Error('AUTH_BYPASS and AUTH_BYPASS_ALLOW must remain false')

  const runtimePassword = crypto.randomBytes(32).toString('base64url')
  process.env.PRA06_RUNTIME_PASSWORD = runtimePassword
  rotateTemporaryPassword(runtimePassword)
  const browser = await chromium.launch({ headless: true })
  const browserVersion = browser.version()
  fsyncWrite(path.join(ASSET_DIR, 'pra06-login-manifest.json'), `${JSON.stringify({
    run_id: runId,
    scenario: 'M30-admin-login',
    count_requested: options.count,
    batch_size: options.batchSize,
    max_attempts: options.maxAttempts,
    frontend_base: FRONTEND_BASE,
    api_base: API_BASE,
    browser_version: browserVersion,
    environment_mode: 'production-build-local-isolated',
    browser_temperature: 'cold',
    server_temperature: 'warm',
    fixture,
    auth_bypass: false,
    auth_bypass_allow: false,
    git_head: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: REPO_ROOT, encoding: 'utf8' }).trim(),
    recorded_at: new Date().toISOString()
  }, null, 2)}\n`)

  let valid = 0
  let attempted = 0
  try {
    while (valid < options.count && attempted < options.maxAttempts) {
      const batchTarget = Math.min(options.batchSize, options.count - valid)
      for (let i = 0; i < batchTarget && attempted < options.maxAttempts && valid < options.count; i += 1) {
        attempted += 1
        const record = await sample(browser, `M30-${String(attempted).padStart(2, '0')}`, runId, browserVersion, fixture)
        appendJson(RAW_FILE, record)
        console.log(JSON.stringify({ sample_id: record.sample_id, valid: record.valid, failure_reason: record.failure_reason }))
        if (record.valid) valid += 1
      }
    }
    const negative = await negativeProbe(browser, runId, browserVersion)
    fsyncWrite(NEGATIVE_FILE, `${JSON.stringify(negative, null, 2)}\n`)
    console.log(JSON.stringify({ run_id: runId, valid, attempted, negative_valid: negative.valid, raw_file: path.basename(RAW_FILE), negative_file: path.basename(NEGATIVE_FILE) }))
    if (valid !== options.count || !negative.valid) process.exitCode = 2
  } finally {
    await browser.close().catch(() => undefined)
    delete process.env.PRA06_RUNTIME_PASSWORD
  }
}

main().catch(error => { console.error(safeText(error.message)); process.exitCode = 1 })
