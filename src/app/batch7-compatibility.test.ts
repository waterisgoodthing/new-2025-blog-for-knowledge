import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const root = resolve(process.cwd(), 'src/app')

function source(relativePath: string) {
  return readFileSync(resolve(root, relativePath), 'utf8')
}

describe('Batch 7 route compatibility contract', () => {
  it('keeps the public read routes available without page-level AuthGate', () => {
    const publicRoutes = [
      '(home)/page.tsx',
      'blog/page.tsx',
      'blog/[id]/page.tsx',
      'notes/page.tsx',
      'notes/[id]/page.tsx',
      'mistakes/page.tsx',
    ]

    for (const route of publicRoutes) {
      expect(existsSync(resolve(root, route)), route).toBe(true)
      expect(source(route), route).not.toContain("from '@/components/auth-gate'")
    }
  })

  it('keeps private entry points behind AuthGate', () => {
    const protectedRoutes = [
      'manage/(workspace)/layout.tsx',
      'mistakes/review/page.tsx',
      'write-note/page.tsx',
      'write-note/[slug]/page.tsx',
      'write-mistake/page.tsx',
      'write-mistake/[slug]/page.tsx',
    ]

    for (const route of protectedRoutes) {
      expect(existsSync(resolve(root, route)), route).toBe(true)
      expect(source(route), route).toContain('AuthGate')
    }
  })

  it('keeps current content links on the manage workflow without removing legacy routes', () => {
    const routes = source('../lib/content-routes.ts')
    expect(routes).toContain("return `/manage/mistakes`")
    expect(routes).toContain("return `/manage/dashboard`")
    expect(existsSync(resolve(root, 'write-note/page.tsx'))).toBe(true)
    expect(existsSync(resolve(root, 'write-note/[slug]/page.tsx'))).toBe(true)
    expect(existsSync(resolve(root, 'write-mistake/page.tsx'))).toBe(true)
    expect(existsSync(resolve(root, 'write-mistake/[slug]/page.tsx'))).toBe(true)
  })

  it('keeps the public mistakes route while preserving private review cutover', () => {
    const nextConfig = readFileSync(resolve(process.cwd(), 'next.config.ts'), 'utf8')
    expect(nextConfig).not.toContain("{ source: '/mistakes', destination: '/manage/mistakes', permanent: false }")
    expect(nextConfig).toContain("{ source: '/mistakes/review', destination: '/manage/review', permanent: false }")
  })
})
