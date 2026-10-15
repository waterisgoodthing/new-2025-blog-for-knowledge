#!/usr/bin/env node
import fs from 'node:fs'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { createRequire } from 'node:module'

const ASSET_DIR = process.env.PRA_ASSET_DIR || path.dirname(new URL(import.meta.url).pathname)
const FRONTEND_BASE = process.env.PRA_FRONTEND_BASE
const API_BASE = process.env.PRA_API_BASE
const SNAPSHOT = process.env.PRA_ISOLATED_WORKTREE
const PYTHON = process.env.PRA_ISOLATED_PYTHON || path.join(SNAPSHOT || '', 'backend/.pra06-venv/bin/python')
const DB_URL = process.env.DATABASE_URL
const USERNAME = process.env.PRA06_TEMP_USERNAME || 'pra06-cookie-diagnostic-admin'
const RUN_ID = process.env.PRA06_NEGATIVE_RUN_ID || 'pra06-negative-boundary-20260822'
const SEED_FILE = process.env.PRA_SEED_FILE || path.join(ASSET_DIR, 'pra06-cookie-diagnostic-20260822-seed.py')
const OUTPUT = path.join(ASSET_DIR, `${RUN_ID}.json`)

if (!FRONTEND_BASE || !API_BASE || !SNAPSHOT || !DB_URL || !fs.existsSync(PYTHON)) {
  throw new Error('isolated runtime inputs are missing')
}
const { chromium } = createRequire(path.join(SNAPSHOT, 'package.json'))('playwright')

function writeSync(file, value) {
  const tmp = `${file}.tmp-${process.pid}`
  fs.writeFileSync(tmp, value, { encoding: 'utf8', mode: 0o600 })
  fs.renameSync(tmp, file)
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

function seed(command) {
  const result = spawnSync(PYTHON, [SEED_FILE, command, USERNAME], {
    cwd: path.join(SNAPSHOT, 'backend'),
    env: { ...process.env, DATABASE_URL: DB_URL, PYTHONPATH: path.join(SNAPSHOT, 'backend') },
    encoding: 'utf8',
    maxBuffer: 1024 * 1024
  })
  if (result.status !== 0) throw new Error(`seed-${command}-failed:exit-${result.status}`)
  return JSON.parse(result.stdout.trim())
}

async function statuses(page, apiBase) {
  return page.evaluate(async base => {
    const read = async pathName => {
      try {
        const response = await fetch(`${base}${pathName}`, { credentials: 'include' })
        return response.status
      } catch {
        return null
      }
    }
    return {
      auth_me: await read('/api/auth/me'),
      strict_management: await read('/api/admin/dashboard/summary')
    }
  }, apiBase)
}

async function main() {
  const startedAt = new Date().toISOString()
  const reasons = []
  let browser
  let unauthContext
  let authContext
  let fixture = null
  const result = {
    run_id: RUN_ID,
    probe: 'no-cookie-and-logout-invalid-session-boundary',
    environment_mode: 'production-build-local-isolated',
    frontend_base: FRONTEND_BASE,
    api_base: API_BASE,
    browser_temperature: 'cold',
    server_temperature: 'warm',
    authenticated_before_logout: false,
    no_cookie_boundary: { auth_me_status: null, strict_management_status: null, valid: false },
    logout_boundary: {
      auth_me_before_logout_status: null,
      logout_status: null,
      auth_me_after_logout_status: null,
      strict_management_after_logout_status: null,
      admin_session_present_after_logout: null,
      valid: false
    },
    password_token_cookie_values_persisted: false,
    started_at: startedAt
  }

  try {
    const prepared = seed('prepare')
    fixture = prepared.fixture
    browser = await chromium.launch({ headless: true })

    unauthContext = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'zh-CN' })
    const unauthPage = await unauthContext.newPage()
    await unauthPage.goto(`${FRONTEND_BASE}/manage`, { waitUntil: 'domcontentloaded', timeout: 15000 })
    result.no_cookie_boundary = { ...(await statuses(unauthPage, API_BASE)), valid: false }
    result.no_cookie_boundary.valid = result.no_cookie_boundary.auth_me === 401 && result.no_cookie_boundary.strict_management === 401
    if (!result.no_cookie_boundary.valid) reasons.push(`no-cookie:${JSON.stringify(result.no_cookie_boundary)}`)

    authContext = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'zh-CN' })
    const authPage = await authContext.newPage()
    const navigation = await authPage.goto(`${FRONTEND_BASE}/manage`, { waitUntil: 'domcontentloaded', timeout: 15000 })
    await authPage.getByLabel('用户名').fill(USERNAME)
    await authPage.getByLabel('密码').fill(prepared.password)
    await authPage.getByRole('button', { name: '密码登录' }).click()
    await authPage.waitForFunction(() => {
      const nodes = document.querySelectorAll('[data-render-state]')
      return nodes.length === 1 && nodes[0].tagName.toLowerCase() === 'main' && nodes[0].getAttribute('data-render-state') === 'ready'
    }, { timeout: 15000 })
    result.logout_boundary.auth_me_before_logout_status = (await statuses(authPage, API_BASE)).auth_me
    result.authenticated_before_logout = result.logout_boundary.auth_me_before_logout_status === 200
    const logoutResult = await authPage.evaluate(async apiBase => {
      try {
        const response = await fetch(`${apiBase}/api/auth/logout`, { method: 'POST', credentials: 'include' })
        return response.status
      } catch {
        return null
      }
    }, API_BASE)
    result.logout_boundary.logout_status = logoutResult
    const afterLogout = await statuses(authPage, API_BASE)
    result.logout_boundary.auth_me_after_logout_status = afterLogout.auth_me
    result.logout_boundary.strict_management_after_logout_status = afterLogout.strict_management
    const cookies = await authContext.cookies(`${API_BASE}/api/auth/me`)
    result.logout_boundary.admin_session_present_after_logout = cookies.some(cookie => cookie.name === 'admin_session')
    result.logout_boundary.valid = result.authenticated_before_logout &&
      result.logout_boundary.logout_status === 200 &&
      result.logout_boundary.auth_me_after_logout_status === 401 &&
      result.logout_boundary.strict_management_after_logout_status === 401 &&
      !result.logout_boundary.admin_session_present_after_logout
    if (!result.logout_boundary.valid) reasons.push(`logout-boundary:${JSON.stringify(result.logout_boundary)}`)
    result.navigation_status = navigation?.status() ?? null
    result.fixture = fixture
    result.valid = reasons.length === 0
    result.failure_reason = result.valid ? null : reasons.join('; ')
    result.recorded_at = new Date().toISOString()
    writeSync(OUTPUT, `${JSON.stringify(result, null, 2)}\n`)
    console.log(JSON.stringify({ run_id: RUN_ID, valid: result.valid, output: OUTPUT }))
    if (!result.valid) process.exitCode = 2
  } catch (error) {
    result.fixture = fixture
    result.valid = false
    result.failure_reason = `harness:${safeText(error.message)}`
    result.recorded_at = new Date().toISOString()
    writeSync(OUTPUT, `${JSON.stringify(result, null, 2)}\n`)
    process.exitCode = 1
  } finally {
    await authContext?.close().catch(() => undefined)
    await unauthContext?.close().catch(() => undefined)
    await browser?.close().catch(() => undefined)
    try { seed('disable') } catch { /* runner retains the failure evidence */ }
  }
}

main().catch(error => {
  writeSync(OUTPUT, `${JSON.stringify({ run_id: RUN_ID, probe: 'no-cookie-and-logout-invalid-session-boundary', valid: false, failure_reason: `fatal:${safeText(error.message)}`, password_token_cookie_values_persisted: false, recorded_at: new Date().toISOString() }, null, 2)}\n`)
  process.exitCode = 1
})
