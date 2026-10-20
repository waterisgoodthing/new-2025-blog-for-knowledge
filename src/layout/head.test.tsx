import { describe, expect, it } from 'vitest'

import { VIEWPORT_CONTENT } from './head'

describe('document viewport metadata', () => {
  it('keeps user zoom enabled on mobile', () => {
    expect(VIEWPORT_CONTENT).toBe('width=device-width, initial-scale=1')
    expect(VIEWPORT_CONTENT).not.toMatch(/maximum-scale|user-scalable\s*=\s*no/)
  })
})
