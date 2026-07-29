import { readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'

const rootFlagIndex = process.argv.indexOf('--root')
const root =
	rootFlagIndex >= 0 && process.argv[rootFlagIndex + 1]
		? resolve(process.argv[rootFlagIndex + 1])
		: process.cwd()
const packageDir = join(root, 'node_modules', '@opennextjs', 'aws')
const packageJsonPath = join(packageDir, 'package.json')
const targetPath = join(packageDir, 'dist', 'minimize-js.js')
const expectedVersion = '4.1.0'

const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'))
if (packageJson.version !== expectedVersion) {
	throw new Error(
		`Unsupported @opennextjs/aws version ${packageJson.version}; expected ${expectedVersion}`,
	)
}

const replacements = [
	[
		'import minify from "@node-minify/core";',
		'import { minify } from "@node-minify/core";',
	],
	[
		'import terser from "@node-minify/terser";',
		'import { terser } from "@node-minify/terser";',
	],
]

let source = readFileSync(targetPath, 'utf8')
for (const [before, after] of replacements) {
	if (source.includes(after)) continue
	if (!source.includes(before)) {
		throw new Error(`OpenNext node-minify import contract changed: ${before}`)
	}
	source = source.replace(before, after)
}

writeFileSync(targetPath, source)
console.log('postinstall: patched OpenNext AWS for node-minify 10 named exports')
