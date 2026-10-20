#!/usr/bin/env node

/**
 * Local project validation script.
 *
 * Runs the core checks that CI also runs:
 *   1. TypeScript type-check (npx tsc --noEmit)
 *   2. Next.js build (npx next build)
 *   3. Backend import check (python -c "from main import app")
 *   4. Backend tests (python -m pytest tests/ -v)
 *
 * Note: CI also provisions a PostgreSQL service container for backend tests.
 * Locally, pytest will skip or fail tests that need a live database unless
 * DATABASE_URL points to a running PostgreSQL instance.
 *
 * Usage: node scripts/check-project.mjs [--skip-build] [--skip-pytest]
 *        npm run check:project
 */

import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..')
const BACKEND = path.join(ROOT, 'backend')

const skipBuild = process.argv.includes('--skip-build')
const skipPytest = process.argv.includes('--skip-pytest')

let passed = 0
let failed = 0

function info(msg) {
  console.log(`  \x1b[32m✓\x1b[0m ${msg}`)
  passed++
}

function fail(msg) {
  console.log(`  \x1b[31m✗\x1b[0m ${msg}`)
  failed++
}

function warn(msg) {
  console.log(`  \x1b[33m⚠\x1b[0m ${msg}`)
}

function section(title) {
  console.log(`\n\x1b[1m${title}\x1b[0m`)
}

function runOrFail(cmd, label, opts = {}) {
  const timeoutMs = opts.timeout || 300_000
  const result = spawnSync(cmd, {
    cwd: opts.cwd || ROOT,
    stdio: 'inherit',
    env: { ...process.env, ...(opts.env || {}) },
    shell: true,
    timeout: timeoutMs,
    killSignal: 'SIGKILL',
  })
  if (result.error && result.error.code === 'ETIMEDOUT') {
    fail(`${label} (timed out after ${Math.round(timeoutMs / 1000)}s)`)
    return -1
  }
  if (result.status === 0) {
    info(label)
  } else {
    fail(`${label} (exit ${result.status})`)
  }
  return result.status
}

// ─── TypeScript check ─────────────────────────────────────────────

section('TypeScript check')
runOrFail('npx tsc --noEmit', 'TypeScript type-check', { timeout: 120_000 })

// ─── Frontend build ───────────────────────────────────────────────
//
// Uses `npx next build` directly (not `npm run build`) so that SIGKILL
// on timeout reaches the Next.js process instead of being swallowed by
// the npm wrapper.  NEXT_PUBLIC_API_URL is set to a non-localhost
// placeholder — no static page makes a build-time API call, so the
// value only needs to satisfy src/lib/api/config.ts's production guard.

if (skipBuild) {
  section('Frontend build')
  warn('Skipped (--skip-build)')
} else {
  section('Frontend build')
  const buildResult = runOrFail('npx next build', 'Next.js production build', {
    env: { NEXT_PUBLIC_API_URL: 'http://build-check.invalid:9999' },
    timeout: 300_000,
  })
  if (buildResult === -1) {
    warn('Build timed out. This is usually environment-specific (slow disk, antivirus, or Node.js version).')
    warn('Try running `npm run build` directly to diagnose.')
  }
}

// ─── Backend import check ────────────────────────────────────────

section('Backend import check')
const venvPython = process.platform === 'win32'
  ? path.join(BACKEND, '.venv', 'Scripts', 'python')
  : path.join(BACKEND, '.venv', 'bin', 'python')

const pythonCmd = fs.existsSync(venvPython) ? venvPython : 'python3'
runOrFail(`"${pythonCmd}" -c "from main import app"`, 'Backend app importable', {
  cwd: BACKEND,
  timeout: 30_000,
})

// ─── Backend tests ───────────────────────────────────────────────

if (skipPytest) {
  section('Backend tests')
  warn('Skipped (--skip-pytest)')
} else {
  section('Backend tests')
  const pytestStatus = runOrFail(
    `"${pythonCmd}" -m pytest tests/ -v --tb=short`,
    'Backend pytest',
    { cwd: BACKEND, timeout: 120_000 }
  )
  if (pytestStatus !== 0) {
    warn('Backend tests failed or timed out. If DATABASE_URL is not set or PostgreSQL is not running, tests requiring a database will fail.')
    warn('Set DATABASE_URL in backend/.env and ensure PostgreSQL is accepting connections.')
  }
}

// ─── Summary ─────────────────────────────────────────────────────

section('Summary')
if (failed > 0) {
  console.log(`\n  \x1b[31m${failed} check(s) failed, ${passed} passed.\x1b[0m\n`)
  process.exit(1)
} else {
  console.log(`\n  \x1b[32mAll ${passed} checks passed.\x1b[0m\n`)
}
