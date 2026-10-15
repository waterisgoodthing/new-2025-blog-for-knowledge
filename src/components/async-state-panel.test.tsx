import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { AsyncStatePanel } from './async-state-panel'

describe('AsyncStatePanel', () => {
  it('renders a stable loading skeleton with reduced-motion support', () => {
    render(<AsyncStatePanel status='loading' />)

    expect(screen.getByRole('status', { name: '正在加载内容' })).toBeInTheDocument()
    expect(screen.getAllByTestId('async-state-panel-skeleton')).toHaveLength(4)
    expect(screen.getByRole('status').className).toContain('motion-reduce:animate-none')
  })

  it('renders an empty hint separately from an API error', () => {
    const { rerender } = render(<AsyncStatePanel status='empty' emptyHint='还没有可展示的笔记' />)

    expect(screen.getByText('还没有可展示的笔记')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()

		rerender(<AsyncStatePanel status='error' error='服务暂时不可用' />)
		expect(screen.getByRole('alert')).toHaveTextContent('服务暂时不可用')
	})

	it('does not expose an arbitrary runtime error message', () => {
		render(<AsyncStatePanel status='error' error={new Error('postgres password=secret')} />)

		expect(screen.getByRole('alert')).toHaveTextContent('服务暂时不可用，请稍后重试。')
		expect(screen.getByRole('alert')).not.toHaveTextContent('password=secret')
	})

  it('retries once while busy and focuses the panel when the retry completes', async () => {
    let resolveRetry!: () => void
    const retry = vi.fn(() => new Promise<void>(resolve => { resolveRetry = resolve }))
    render(<AsyncStatePanel status='error' error='请求失败' onRetry={retry} />)

    const button = screen.getByRole('button', { name: '重试' })
    fireEvent.click(button)
    fireEvent.click(button)

    expect(retry).toHaveBeenCalledOnce()
    expect(button).toBeDisabled()

    resolveRetry()
    await waitFor(() => expect(screen.getByRole('region', { name: '数据面板' })).toHaveFocus())
  })
})
