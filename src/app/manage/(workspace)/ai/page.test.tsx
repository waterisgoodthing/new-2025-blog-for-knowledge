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

vi.mock('@/lib/api/ai-runs', () => ({
  getAiRuns: vi.fn().mockResolvedValue({ items: [], total: 0, limit: 20, offset: 0 }),
  getAiRun: vi.fn(),
  retryAiRun: vi.fn(),
  decideAiRun: vi.fn(),
}))

const api = await import('@/lib/api/ai')
const { default: ManageAiPage } = await import('./page')

describe('ManageAiPage — governance surface', () => {
  it('states the governed boundary without calling legacy AI APIs', () => {
    render(<ManageAiPage />)

    expect(screen.getByRole('heading', { name: 'AI 运行记录' })).toBeInTheDocument()
    expect(screen.getByText(/人工确认不会直接写入/)).toBeInTheDocument()

    expect(api.getCallLogs).not.toHaveBeenCalled()
    expect(api.getCallLogStats).not.toHaveBeenCalled()
    expect(api.getProviderStatus).not.toHaveBeenCalled()
    expect(api.getUsageCostStats).not.toHaveBeenCalled()
    expect(api.getProviderHealthSnapshot).not.toHaveBeenCalled()
  })
})
