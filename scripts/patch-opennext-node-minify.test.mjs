import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import test from 'node:test'

test('postinstall compatibility patch makes OpenNext AWS use node-minify named exports', () => {
	const root = mkdtempSync(join(tmpdir(), 'opennext-node-minify-patch-'))
	const packageDir = join(root, 'node_modules', '@opennextjs', 'aws')
	const distDir = join(packageDir, 'dist')
	mkdirSync(distDir, { recursive: true })
	writeFileSync(join(packageDir, 'package.json'), JSON.stringify({ version: '4.1.0' }))
	writeFileSync(
		join(distDir, 'minimize-js.js'),
		[
			'import minify from "@node-minify/core";',
			'import terser from "@node-minify/terser";',
			'export { minify, terser };',
			'',
		].join('\n'),
	)

	execFileSync(process.execPath, [
		join(process.cwd(), 'scripts', 'patch-opennext-node-minify.mjs'),
		'--root',
		root,
	])

	const patched = readFileSync(join(distDir, 'minimize-js.js'), 'utf8')
	assert.match(patched, /import \{ minify \} from "@node-minify\/core";/)
	assert.match(patched, /import \{ terser \} from "@node-minify\/terser";/)
})
