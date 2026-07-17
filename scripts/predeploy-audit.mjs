import { execFileSync } from 'node:child_process'

function run(command, args, options = {}) {
	return execFileSync(command, args, {
		cwd: process.cwd(),
		encoding: 'utf8',
		stdio: options.stdio ?? 'pipe'
	})
}

function fail(message) {
	console.error(`predeploy: blocked - ${message}`)
	process.exit(1)
}

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

const status = run('git', ['status', '--porcelain']).trim()
if (status) fail('worktree is not clean')

try {
	run('npm', ['audit', '--omit=dev', '--audit-level=high', '--json'])
} catch (error) {
	const output = `${error.stdout ?? ''}${error.stderr ?? ''}`
	const report = parseAuditReport(output)
	if (report) {
		const counts = report.metadata?.vulnerabilities ?? {}
		if ((counts.high ?? 0) > 0 || (counts.critical ?? 0) > 0) {
			fail(`production audit has ${counts.high ?? 0} high and ${counts.critical ?? 0} critical vulnerabilities`)
		}
	} else {
		fail('production audit command failed')
	}
}

try {
	run('npm', ['ls', 'next', '@opennextjs/cloudflare'], { stdio: 'pipe' })
} catch {
	fail('Next/OpenNext dependency tree is invalid')
}

try {
	run('npm', ['test'], { stdio: 'inherit' })
	run('npm', ['run', 'build:cf'], { stdio: 'inherit' })
	run('npx', ['tsc', '--noEmit', '--pretty', 'false'], { stdio: 'inherit' })
} catch {
	fail('test, TypeScript check, or Cloudflare build failed')
}

console.log('predeploy: passed - clean worktree, audit, peer contract, tests, TypeScript, and Cloudflare build')
