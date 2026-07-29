import { execFileSync } from 'node:child_process'

import { runFrontendGate } from './predeploy-gates.mjs'

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
	runFrontendGate({ run, cwd: process.cwd(), env: process.env, fail })
	console.log('predeploy:frontend passed - clean worktree, audit, frontend tests, TypeScript, and Cloudflare build')
} catch (error) {
	console.error(error.message)
	process.exitCode = 1
}
