import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

vi.mock('./drafts/components/draft-workspace', () => ({
  DraftWorkspace: () => <div aria-label='草稿审核队列' />,
}))

import { manageCapabilityStates } from './capability-state'
import ManageDraftsPage from './drafts/page'

describe('management capability state', () => {
  it('marks every proven daily-workflow surface active', () => {
    expect(manageCapabilityStates).toEqual({
      drafts: 'active',
      capture: 'active',
      ai: 'active',
      aiRuns: 'active',
      search: 'deferred',
      analytics: 'active',
      jobs: 'active',
    })
  })

  it('exposes the implemented draft review workspace instead of a static shell', () => {
    render(<ManageDraftsPage />)

    expect(screen.getByRole('heading', { name: '草稿' })).toBeInTheDocument()
    expect(screen.getByLabelText('草稿审核队列')).toBeInTheDocument()
    expect(screen.queryByText(/Static|Coming Soon|Batch 1/i)).not.toBeInTheDocument()
  })
})
