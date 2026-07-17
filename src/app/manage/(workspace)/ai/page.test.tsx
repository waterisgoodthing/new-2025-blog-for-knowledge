import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('../../components/manage-page-header', () => ({
  ManagePageHeader: ({
    title,
    description,
  }: {
    title: string
    description: string
  }) => (
    <header>
      <h1>{title}</h1>
      <p>{description}</p>
    </header>
  ),
}))

vi.mock('@/lib/api/ai', () => ({
  getCallLogs: vi.fn(),
  getCallLogStats: vi.fn(),
  getProviderStatus: vi.fn(),
  getUsageCostStats: vi.fn(),
  getProviderHealthSnapshot: vi.fn(),
}))

const api = await import('@/lib/api/ai')
const { default: ManageAiPage } = await import('./page')

describe('ManageAiPage — Batch 6 placeholder', () => {
  it('renders the static AI shell without calling AI APIs', () => {
    render(<ManageAiPage />)

    expect(screen.getByRole('heading', { name: 'AI' })).toBeInTheDocument()
    expect(screen.getByText('后续批次启用')).toBeInTheDocument()
    expect(screen.getByText(/不会调用任何 AI API/)).toBeInTheDocument()

    expect(api.getCallLogs).not.toHaveBeenCalled()
    expect(api.getCallLogStats).not.toHaveBeenCalled()
    expect(api.getProviderStatus).not.toHaveBeenCalled()
    expect(api.getUsageCostStats).not.toHaveBeenCalled()
    expect(api.getProviderHealthSnapshot).not.toHaveBeenCalled()
  })
})
