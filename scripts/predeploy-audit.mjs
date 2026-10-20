import { execFileSync } from 'node:child_process'

import { runFullGate } from './predeploy-gates.mjs'

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
	runFullGate({ run, cwd: process.cwd(), env: process.env, fail })
	console.log('predeploy: passed - clean worktree, frontend, backend, Alembic, and Cloudflare build')
} catch (error) {
	console.error(error.message)
	process.exitCode = 1
}
