import { join } from 'node:path'

function parseAuditReport(output) {
	const start = output.indexOf('{')
	const end = output.lastIndexOf('}')
	if (start < 0 || end < start) return null
	try {
		return JSON.parse(output.slice(start, end + 1))
	} catch {
		return null
	}
}

export function runFrontendGate({ run, cwd, env, fail }) {
	const commandOptions = { cwd, env, stdio: 'inherit' }
	const status = run('git', ['status', '--porcelain'], { cwd, env }).trim()
	if (status) fail('worktree is not clean')

	try {
		run('npm', ['audit', '--omit=dev', '--audit-level=high', '--json'], { cwd, env })
	} catch (error) {
		const output = `${error.stdout ?? ''}${error.stderr ?? ''}`
		const report = parseAuditReport(output)
		if (!report) fail('production audit command failed')
		const counts = report.metadata?.vulnerabilities ?? {}
		if ((counts.high ?? 0) > 0 || (counts.critical ?? 0) > 0) {
			fail(`production audit has ${counts.high ?? 0} high and ${counts.critical ?? 0} critical vulnerabilities`)
		}
	}

	try {
		run('npm', ['ls', 'next', '@opennextjs/cloudflare'], { cwd, env })
	} catch {
		fail('Next/OpenNext dependency tree is invalid')
	}

	try {
		run('npm', ['test'], commandOptions)
		run('npm', ['run', 'build:cf'], commandOptions)
		run('npx', ['tsc', '--noEmit', '--pretty', 'false'], commandOptions)
		run('git', ['diff', '--check'], commandOptions)
	} catch {
		fail('frontend test, TypeScript check, Cloudflare build, or diff hygiene failed')
	}
}

export function runBackendGate({ run, cwd, env, fail }) {
	const backendTestDatabaseUrl = env.PREDEPLOY_BACKEND_TEST_DATABASE_URL
	const backendTargetDatabaseUrl = env.PREDEPLOY_BACKEND_DATABASE_URL
	if (!backendTestDatabaseUrl || !backendTargetDatabaseUrl) {
		fail('PREDEPLOY_BACKEND_TEST_DATABASE_URL and PREDEPLOY_BACKEND_DATABASE_URL are required')
	}
	if (backendTestDatabaseUrl === backendTargetDatabaseUrl) {
		fail('backend test and target database URLs must be different')
	}

	const status = run('git', ['status', '--porcelain'], { cwd, env }).trim()
	if (status) fail('worktree is not clean')

	const backendDir = join(cwd, 'backend')
	const backendTestEnv = { ...env, DATABASE_URL: backendTestDatabaseUrl }
	const backendTargetEnv = { ...env, DATABASE_URL: backendTargetDatabaseUrl }
	try {
		run('.venv/bin/python', ['-m', 'pytest', '-q'], {
			cwd: backendDir,
			env: backendTestEnv,
			stdio: 'inherit',
		})
		run('.venv/bin/alembic', ['current'], {
			cwd: backendDir,
			env: backendTargetEnv,
			stdio: 'inherit',
		})
		run('.venv/bin/alembic', ['heads'], {
			cwd: backendDir,
			env: backendTargetEnv,
			stdio: 'inherit',
		})
		run('.venv/bin/alembic', ['check'], {
			cwd: backendDir,
			env: backendTargetEnv,
			stdio: 'inherit',
		})
	} catch {
		fail('backend test, revision, or Alembic metadata check failed')
	}
}

export function runFullGate(context) {
	runFrontendGate(context)
	runBackendGate(context)
}
