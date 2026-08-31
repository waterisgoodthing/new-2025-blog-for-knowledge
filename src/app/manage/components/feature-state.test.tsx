import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { FeatureState } from './feature-state'

describe('FeatureState', () => {
  it('renders a labelled skeleton without generic loading copy', () => {
    render(<FeatureState state={{ kind: 'loading', label: '正在加载草稿', rows: 3 }} />)

    expect(screen.getByRole('status', { name: '正在加载草稿' })).toBeInTheDocument()
    expect(screen.getAllByTestId('feature-state-skeleton')).toHaveLength(3)
    expect(screen.queryByText('加载中...')).not.toBeInTheDocument()
  })

  it('keeps empty and deferred states semantically distinct', () => {
    const { rerender } = render(
      <FeatureState state={{ kind: 'empty', title: '暂无错题', description: '记录第一次错误后会显示在这里。' }} />,
    )
    expect(screen.getByRole('heading', { name: '暂无错题' })).toBeInTheDocument()

    rerender(
      <FeatureState state={{ kind: 'deferred', title: 'AI 助手', description: '当前版本未启用。' }} />,
    )
    expect(screen.getByText('后续能力')).toBeInTheDocument()
    expect(screen.getByText('当前版本未启用。')).toBeInTheDocument()
  })

  it('exposes an explicit retry action for recoverable errors', () => {
    const retry = vi.fn()
    render(
      <FeatureState state={{ kind: 'error', title: '加载失败', description: '请重试。', retry }} />,
    )

    fireEvent.click(screen.getByRole('button', { name: '重新尝试' }))
    expect(retry).toHaveBeenCalledOnce()
  })
})
