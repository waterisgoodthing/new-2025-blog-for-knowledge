import { spawnSync } from 'node:child_process'
import path from 'node:path'

export interface Week4SeedResult {
  marker: string
  admin_username: string
  subject_id: number
  knowledge_point_id: number
  question_id: string
  question_title: string
  question_text: string
  correct_answer: string
  mistake_id: string
  review_item_id: string
}

function repoRoot(): string {
  return path.resolve(__dirname, '..', '..')
}

/**
 * Global setup for the R22b business E2E (F04).
 *
 * Runs the deterministic Python seed against the scratch database carried in
 * DATABASE_URL, then exposes the resulting identifiers to the specs through
 * `process.env.E2E_SEED_*` (Playwright spawns workers after globalSetup, so the
 * worker processes inherit these). The specs fall back to API discovery by the
 * stable marker, so the env hand-off is convenience, not the only contract.
 */
export default async function globalSetup(): Promise<void> {
  const root = repoRoot()
  const databaseUrl = process.env.DATABASE_URL
  if (!databaseUrl) {
    throw new Error(
      'E2E globalSetup requires DATABASE_URL pointing at a local astra_week4_* scratch database. ' +
        'Set E2E_SKIP_SEED=1 only for runs that do not need the backend.',
    )
  }

  const pythonPath = process.env.E2E_SEED_PYTHON ?? path.join(root, 'backend', '.venv', 'bin', 'python')
  const scriptPath = path.join(root, 'tests', 'e2e', 'seed', 'seed_week4_business.py')

  const result = spawnSync(pythonPath, [scriptPath], {
    cwd: path.join(root, 'backend'),
    env: {
      ...process.env,
      PYTHONPATH: path.join(root, 'backend'),
      DATABASE_URL: databaseUrl,
    },
    encoding: 'utf8',
  })

  if (result.error) {
    throw new Error(`E2E seed could not start (${pythonPath}): ${result.error.message}`)
  }
  if (result.status !== 0) {
    throw new Error(
      `E2E seed failed (exit ${result.status}).\nstdout:\n${result.stdout ?? ''}\nstderr:\n${result.stderr ?? ''}`,
    )
  }

  const line = (result.stdout ?? '')
    .split('\n')
    .find((candidate) => candidate.startsWith('E2E_SEED_RESULT='))
  if (!line) {
    throw new Error(`E2E seed produced no E2E_SEED_RESULT line.\nstdout:\n${result.stdout ?? ''}`)
  }

  const seed = JSON.parse(line.slice('E2E_SEED_RESULT='.length)) as Week4SeedResult
  process.env.E2E_SEED_QUESTION_ID = seed.question_id
  process.env.E2E_SEED_QUESTION_TEXT = seed.question_text
  process.env.E2E_SEED_REVIEW_ITEM_ID = seed.review_item_id
  process.env.E2E_SEED_CORRECT_ANSWER = seed.correct_answer
  process.env.E2E_SEED_MISTAKE_ID = seed.mistake_id

  console.log(
    `[e2e-seed] question=${seed.question_id} review_item=${seed.review_item_id} ` +
      `marker=${seed.marker}`,
  )
}
