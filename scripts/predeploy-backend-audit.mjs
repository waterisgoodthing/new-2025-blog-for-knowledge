import { execFileSync } from 'node:child_process'

import { runBackendGate } from './predeploy-gates.mjs'

function run(command, args, options = {}) {
	return execFileSync(command, args, {
		cwd: options.cwd ?? process.cwd(),
		env: options.env ?? process.env,
		encoding: 'utf8',
		stdio: options.stdio ?? 'pipe',
	})
}

function fail(message) {
	throw new Error(`predeploy: blocked - ${message}`)
}

try {
	runBackendGate({ run, cwd: process.cwd(), env: process.env, fail })
	console.log('predeploy:backend passed - clean worktree, backend tests, revision, and Alembic authority')
} catch (error) {
	console.error(error.message)
	process.exitCode = 1
}
