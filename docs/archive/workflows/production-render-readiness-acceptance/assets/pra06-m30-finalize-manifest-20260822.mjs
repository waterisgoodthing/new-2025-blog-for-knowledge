#!/usr/bin/env node
import fs from 'node:fs'
import path from 'node:path'

const assetDir = path.dirname(new URL(import.meta.url).pathname)
const sourceFile = path.join(assetDir, 'pra06-m30-batch-20260822.batch.manifest.json')
const negativeFile = path.join(assetDir, 'pra06-m30-negative-final-20260822-negative.json')
const outputFile = path.join(assetDir, 'pra06-m30-batch-final-20260822.manifest.json')

function writeSync(file, value) {
  const tmp = `${file}.tmp-${process.pid}`
  fs.writeFileSync(tmp, value, { encoding: 'utf8', mode: 0o600 })
  fs.renameSync(tmp, file)
}

const source = JSON.parse(fs.readFileSync(sourceFile, 'utf8'))
const negative = JSON.parse(fs.readFileSync(negativeFile, 'utf8'))
const output = {
  ...source,
  run_id: 'pra06-m30-batch-final-20260822',
  purpose: 'authoritative M30 browser-cold/server-warm raw sample manifest; no performance aggregation',
  negative_boundary: {
    run_id: negative.run_id,
    path: negativeFile,
    valid: negative.valid === true,
    no_cookie_auth_me_status: negative.no_cookie_boundary.auth_me,
    no_cookie_strict_management_status: negative.no_cookie_boundary.strict_management,
    authenticated_before_logout: negative.authenticated_before_logout === true,
    logout_status: negative.logout_boundary.logout_status,
    auth_me_after_logout_status: negative.logout_boundary.auth_me_after_logout_status,
    strict_management_after_logout_status: negative.logout_boundary.strict_management_after_logout_status,
    admin_session_present_after_logout: negative.logout_boundary.admin_session_present_after_logout === true,
    password_token_cookie_values_persisted: false
  },
  recheck_history: [
    { run_id: 'pra06-m30-batch-20260822-negative', path: path.join(assetDir, 'pra06-m30-batch-20260822-negative.json'), valid: false, preserved: true },
    { run_id: 'pra06-m30-negative-recheck-20260822-negative', path: path.join(assetDir, 'pra06-m30-negative-recheck-20260822-negative.json'), valid: false, preserved: true },
    { run_id: negative.run_id, path: negativeFile, valid: negative.valid === true, preserved: true }
  ],
  status: source.valid_count === source.requested_valid_count && negative.valid === true ? 'pass' : 'blocked',
  p50: null,
  p90: null,
  performance_baseline: false,
  production_readiness_claim: false,
  finalized_at: new Date().toISOString()
}
writeSync(outputFile, `${JSON.stringify(output, null, 2)}\n`)
console.log(JSON.stringify({ output: outputFile, valid_count: output.valid_count, attempts: output.attempts, failure_rate: output.failure_rate, negative_valid: output.negative_boundary.valid, status: output.status }))
