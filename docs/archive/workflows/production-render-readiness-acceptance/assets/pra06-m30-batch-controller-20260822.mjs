#!/usr/bin/env node
import fs from 'node:fs'
import path from 'node:path'
import { spawnSync } from 'node:child_process'

const ASSET_DIR = process.env.PRA_ASSET_DIR || path.dirname(new URL(import.meta.url).pathname)
const SNAPSHOT = process.env.PRA_ISOLATED_WORKTREE
const DIAGNOSTIC = path.join(SNAPSHOT, 'docs/workflows/production-render-readiness-acceptance/assets/pra06-cookie-diagnostic-20260822.mjs')
const NEGATIVE = path.join(SNAPSHOT, 'docs/workflows/production-render-readiness-acceptance/assets/pra06-negative-boundary-20260822.mjs')
const RUN_ID = process.env.PRA_M30_BATCH_ID || process.env.PRA_RUN_ID || 'pra06-m30-batch-20260822'
const COUNT = Number(process.env.PRA_M30_COUNT || 10)
const MAX_ATTEMPTS = Number(process.env.PRA_M30_MAX_ATTEMPTS || Math.max(COUNT, 12))
const SKIP_SAMPLES = process.env.PRA_M30_SKIP_SAMPLES === 'true'
const USERNAME = process.env.PRA06_TEMP_USERNAME || 'pra06-cookie-diagnostic-admin'
const BATCH_MANIFEST = path.join(ASSET_DIR, `${RUN_ID}.batch.manifest.json`)

if (!SNAPSHOT || !Number.isInteger(COUNT) || COUNT < 1 || COUNT > 10 || !Number.isInteger(MAX_ATTEMPTS) || MAX_ATTEMPTS < COUNT || MAX_ATTEMPTS > 20) {
  throw new Error('invalid M30 batch inputs')
}

function writeSync(file, value) {
  const tmp = `${file}.tmp-${process.pid}`
  fs.writeFileSync(tmp, value, { encoding: 'utf8', mode: 0o600 })
  fs.renameSync(tmp, file)
}

function readRaw(file) {
  if (!fs.existsSync(file)) return null
  const lines = fs.readFileSync(file, 'utf8').trim().split('\n').filter(Boolean)
  if (lines.length !== 1) return null
  try { return JSON.parse(lines[0]) } catch { return null }
}

function fallbackRaw(runId, sampleId, exitCode) {
  return {
    run_id: runId,
    sample_id: sampleId,
    sample_status: 'failed',
    valid: false,
    browser_temperature: 'cold',
    server_temperature: 'warm',
    environment_mode: 'production-build-local-isolated',
    navigation: { url: null, status: null, error: null, ttfb: null, dom_content_loaded: null, load: null, duration: null },
    lcp: null,
    api_timings: [],
    readiness: { navigation_timing: null, lcp: null, resource_timings: [], dom: { selector: '[data-render-state]', selector_count: null, main_count: null, state: null }, marks: { auth_submit: [], content_ready: [] } },
    console_errors: [],
    expected_console_errors: [],
    unexpected_console_errors: [],
    page_errors: [],
    failed_requests: [],
    expected_failed_requests: [],
    unexpected_failed_requests: [],
    unexpected_navigations: [],
    dialogs: [],
    downloads: [],
    failure_reason: `harness-exit:${exitCode}`,
    password_token_cookie_values_persisted: false,
    recorded_at: new Date().toISOString()
  }
}

function currentManifest(samples, status = 'in_progress', negative = null) {
  const failed = samples.filter(sample => !sample.valid).length
  return {
    run_id: RUN_ID,
    purpose: 'M30 browser-cold/server-warm raw sampling only; no performance aggregation',
    environment_mode: 'production-build-local-isolated',
    browser_temperature: 'cold',
    server_temperature: 'warm',
    requested_valid_count: COUNT,
    max_attempts: MAX_ATTEMPTS,
    attempts: samples.length,
    valid_count: samples.filter(sample => sample.valid).length,
    failed_count: failed,
    failure_rate: samples.length ? failed / samples.length : null,
    samples,
    negative_boundary: negative,
    p50: null,
    p90: null,
    performance_baseline: false,
    production_readiness_claim: false,
    status,
    recorded_at: new Date().toISOString()
  }
}

function disableSeed() {
  const python = process.env.PRA_ISOLATED_PYTHON
  const seed = process.env.PRA_SEED_FILE
  if (!python || !seed) return
  spawnSync(python, [seed, 'disable', USERNAME], {
    cwd: path.join(SNAPSHOT, 'backend'),
    env: { ...process.env, DATABASE_URL: process.env.DATABASE_URL, PYTHONPATH: path.join(SNAPSHOT, 'backend') },
    stdio: 'ignore'
  })
}

const samples = []
let validCount = 0
try {
  for (let attempt = 1; !SKIP_SAMPLES && attempt <= MAX_ATTEMPTS && validCount < COUNT; attempt += 1) {
    const suffix = String(attempt).padStart(2, '0')
    const sampleRunId = `${RUN_ID}-attempt-${suffix}`
    const sampleId = `M30-${suffix}`
    const rawFile = path.join(ASSET_DIR, `${sampleRunId}.raw.ndjson`)
    const manifestFile = path.join(ASSET_DIR, `${sampleRunId}.manifest.json`)
    const child = spawnSync(process.execPath, [DIAGNOSTIC], {
      cwd: SNAPSHOT,
      env: {
        ...process.env,
        PRA_RUN_ID: sampleRunId,
        PRA_SAMPLE_ID: sampleId,
        PRA_M30_BATCH: 'true'
      },
      stdio: 'inherit'
    })
    let raw = readRaw(rawFile)
    if (!raw) {
      raw = fallbackRaw(sampleRunId, sampleId, child.status ?? 1)
      writeSync(rawFile, `${JSON.stringify(raw)}\n`)
    }
    if (!fs.existsSync(manifestFile)) {
      writeSync(manifestFile, `${JSON.stringify({ run_id: sampleRunId, status: raw.valid ? 'pass' : 'fail', result: { sample_id: sampleId, valid: raw.valid, failure_reason: raw.failure_reason }, raw_file: rawFile, password_token_cookie_values_persisted: false }, null, 2)}\n`)
    }
    const record = {
      attempt,
      run_id: sampleRunId,
      sample_id: raw.sample_id || sampleId,
      raw_path: rawFile,
      manifest_path: manifestFile,
      exit_code: child.status ?? 1,
      valid: raw.valid === true,
      failure_reason: raw.failure_reason || null
    }
    samples.push(record)
    if (record.valid) validCount += 1
    writeSync(BATCH_MANIFEST, `${JSON.stringify(currentManifest(samples), null, 2)}\n`)
    disableSeed()
  }

  const negativeRunId = `${RUN_ID}-negative`
  const negativeFile = path.join(ASSET_DIR, `${negativeRunId}.json`)
  const negativeChild = spawnSync(process.execPath, [NEGATIVE], {
    cwd: SNAPSHOT,
    env: { ...process.env, PRA06_NEGATIVE_RUN_ID: negativeRunId },
    stdio: 'inherit'
  })
  const negative = {
    run_id: negativeRunId,
    path: negativeFile,
    exit_code: negativeChild.status ?? 1,
    valid: fs.existsSync(negativeFile) && JSON.parse(fs.readFileSync(negativeFile, 'utf8')).valid === true
  }
  const finalStatus = validCount === COUNT && negative.valid ? 'pass' : 'blocked'
  writeSync(BATCH_MANIFEST, `${JSON.stringify(currentManifest(samples, finalStatus, negative), null, 2)}\n`)
  console.log(JSON.stringify({ run_id: RUN_ID, valid_count: validCount, attempts: samples.length, negative_valid: negative.valid, batch_manifest: BATCH_MANIFEST }))
  if (finalStatus !== 'pass') process.exitCode = 2
} finally {
  disableSeed()
}
