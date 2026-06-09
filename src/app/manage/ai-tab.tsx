'use client'

import { useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { EmptyState } from '@/components/empty-state'
import { getApiBase } from '@/lib/api/config'

interface AIConfig {
  ai_model: string
  ai_base_url: string
  dashscope_model: string
  deepseek_model: string
  has_ai_key: boolean
  has_dashscope_key: boolean
  has_deepseek_key: boolean
}

export function AITab() {
  const [config, setConfig] = useState<AIConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [testInput, setTestInput] = useState('')
  const [testResult, setTestResult] = useState<string | null>(null)
  const [testing, setTesting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const API_BASE = getApiBase()
      const res = await fetch(`${API_BASE}/api/ai/config`, { credentials: 'include' })
      if (res.ok) {
        setConfig(await res.json())
      }
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleTest = async () => {
    if (!testInput.trim()) return
    setTesting(true)
    setTestResult(null)
    try {
      const API_BASE = getApiBase()
      const res = await fetch(`${API_BASE}/api/ai/polish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ text: testInput, action: 'polish' }),
      })
      if (!res.ok) {
        setTestResult(`Error: ${res.status}`)
        return
      }
      const reader = res.body?.getReader()
      if (!reader) return
      const decoder = new TextDecoder()
      let result = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        result += decoder.decode(value, { stream: true })
      }
      setTestResult(result || '(empty response)')
    } catch (e: any) {
      setTestResult(`Error: ${e.message}`)
    } finally {
      setTesting(false)
    }
  }

  if (loading) {
    return <div className='py-20 text-center text-gray-400'>加载中...</div>
  }

  return (
    <div className='space-y-6'>
      <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
        <h3 className='mb-4 font-medium'>AI 配置状态</h3>
        <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
          <StatusCard
            title='通用 AI'
            model={config?.ai_model || '--'}
            connected={config?.has_ai_key ?? false}
          />
          <StatusCard
            title='DashScope (视觉)'
            model={config?.dashscope_model || '--'}
            connected={config?.has_dashscope_key ?? false}
          />
          <StatusCard
            title='DeepSeek'
            model={config?.deepseek_model || '--'}
            connected={config?.has_deepseek_key ?? false}
          />
        </div>
      </div>

      <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
        <h3 className='mb-4 font-medium'>AI 功能</h3>
        <div className='grid grid-cols-2 gap-3 md:grid-cols-4'>
          {[
            { label: '错题分析', desc: 'OCR/文本分析错题' },
            { label: '文本润色', desc: '润色、翻译、摘要' },
            { label: '标签建议', desc: 'AI 推荐标签' },
            { label: '知识总结', desc: '带引用的知识总结' },
            { label: '每日推荐', desc: 'AI 生成推荐理由' },
            { label: '薄弱点诊断', desc: 'AI 诊断薄弱知识点' },
            { label: '变式题生成', desc: '生成类似题目' },
            { label: '周报总结', desc: '一周学习总结' },
          ].map(f => (
            <div key={f.label} className='rounded-xl bg-white/40 p-3'>
              <div className='text-sm font-medium'>{f.label}</div>
              <div className='text-xs text-gray-500'>{f.desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
        <h3 className='mb-4 font-medium'>AI 测试</h3>
        <div className='flex gap-2'>
          <input
            value={testInput}
            onChange={e => setTestInput(e.target.value)}
            placeholder='输入文本测试 AI 响应...'
            className='flex-1 rounded-xl border border-white/40 bg-white/60 px-4 py-2 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
          />
          <button
            onClick={handleTest}
            disabled={testing || !testInput.trim()}
            className='rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white disabled:opacity-50'
          >
            {testing ? '测试中...' : '测试'}
          </button>
        </div>
        {testResult && (
          <div className='mt-3 rounded-xl bg-white/40 p-4 text-sm'>
            <pre className='whitespace-pre-wrap'>{testResult}</pre>
          </div>
        )}
      </div>

      <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
        <h3 className='mb-3 font-medium'>使用日志</h3>
        <p className='text-sm text-gray-500'>AI 调用日志将在审计日志中记录。</p>
      </div>
    </div>
  )
}

function StatusCard({ title, model, connected }: { title: string; model: string; connected: boolean }) {
  return (
    <div className='rounded-xl bg-white/40 p-4'>
      <div className='text-sm text-gray-500'>{title}</div>
      <div className='mt-1 font-medium'>{model}</div>
      <div className='mt-1'>
        <span className={`inline-block rounded-full px-2 py-0.5 text-xs ${
          connected ? 'bg-green-500/10 text-green-600' : 'bg-red-500/10 text-red-600'
        }`}>
          {connected ? '已配置' : '未配置'}
        </span>
      </div>
    </div>
  )
}
