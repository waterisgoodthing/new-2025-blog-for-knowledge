import assert from 'node:assert/strict'
import test from 'node:test'

import { runBackendGate, runFrontendGate, runFullGate } from './predeploy-gates.mjs'

test('frontend gate completes without reading backend database configuration', () => {
	const calls = []
	const run = (command, args, options = {}) => {
		calls.push({ command, args, options })
		return ''
	}

	runFrontendGate({
		run,
		cwd: '/release',
		env: {},
		fail: (message) => {
			throw new Error(message)
		},
	})

	assert.deepEqual(
		calls.map(({ command, args }) => [command, args]),
		[
			['git', ['status', '--porcelain']],
			['npm', ['audit', '--omit=dev', '--audit-level=high', '--json']],
			['npm', ['ls', 'next', '@opennextjs/cloudflare']],
			['npm', ['test']],
			['npm', ['run', 'build:cf']],
			['npx', ['tsc', '--noEmit', '--pretty', 'false']],
			['git', ['diff', '--check']],
		],
	)
})

test('backend gate fails before executing commands when its distinct database boundaries are absent', () => {
	let calls = 0

	assert.throws(
		() =>
			runBackendGate({
				run: () => {
					calls += 1
					return ''
				},
				cwd: '/release',
				env: {},
				fail: (message) => {
					throw new Error(message)
				},
			}),
		/PREDEPLOY_BACKEND_TEST_DATABASE_URL/,
	)
	assert.equal(calls, 0)
})

test('full gate composes frontend validation before backend authority validation', () => {
	const calls = []
	const run = (command, args, options = {}) => {
		calls.push([command, args])
		return ''
	}

	runFullGate({
		run,
		cwd: '/release',
		env: {
			PREDEPLOY_BACKEND_TEST_DATABASE_URL: 'test-url',
			PREDEPLOY_BACKEND_DATABASE_URL: 'target-url',
		},
		fail: (message) => {
			throw new Error(message)
		},
	})

	assert.deepEqual(calls.slice(-4), [
		['.venv/bin/python', ['-m', 'pytest', '-q']],
		['.venv/bin/alembic', ['current']],
		['.venv/bin/alembic', ['heads']],
		['.venv/bin/alembic', ['check']],
	])
})
