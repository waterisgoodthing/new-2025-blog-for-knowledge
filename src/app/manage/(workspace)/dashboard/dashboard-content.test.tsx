import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mutate = vi.fn()
let swrState: { data?: unknown; error?: unknown; isLoading: boolean; mutate: typeof mutate }

vi.mock('swr', () => ({
  default: () => swrState,
}))

vi.mock('@/lib/api/dashboard', () => ({
  getDashboardSummary: vi.fn(),
}))

vi.mock('@/lib/api/admin-profile', () => ({
  getAdminProfile: vi.fn(),
}))

vi.mock('./dashboard-overview', () => ({
  DashboardOverview: () => <div>dashboard ready</div>,
}))

const { DashboardContent } = await import('./dashboard-content')

describe('DashboardContent states', () => {
  beforeEach(() => {
    mutate.mockReset()
  })

  it('uses the shared loading skeleton', () => {
    swrState = { isLoading: true, mutate }
    render(<DashboardContent />)

    expect(screen.getByRole('status', { name: '正在加载学习概览' })).toBeInTheDocument()
    expect(screen.getAllByTestId('feature-state-skeleton').length).toBeGreaterThan(0)
  })

  it('uses the shared retry action on failure', () => {
    swrState = { isLoading: false, error: new Error('offline'), mutate }
    render(<DashboardContent />)

    fireEvent.click(screen.getByRole('button', { name: '重新尝试' }))
    expect(mutate).toHaveBeenCalledOnce()
  })
})
