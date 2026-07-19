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

describe('ManageAiPage — deferred product surface', () => {
  it('states the deferred boundary without calling AI APIs', () => {
    render(<ManageAiPage />)

    expect(screen.getByRole('heading', { name: 'AI 助手' })).toBeInTheDocument()
    expect(screen.getByText('后续能力')).toBeInTheDocument()
    expect(screen.getByText(/不调用 AI/)).toBeInTheDocument()

    expect(api.getCallLogs).not.toHaveBeenCalled()
    expect(api.getCallLogStats).not.toHaveBeenCalled()
    expect(api.getProviderStatus).not.toHaveBeenCalled()
    expect(api.getUsageCostStats).not.toHaveBeenCalled()
    expect(api.getProviderHealthSnapshot).not.toHaveBeenCalled()
  })
})
