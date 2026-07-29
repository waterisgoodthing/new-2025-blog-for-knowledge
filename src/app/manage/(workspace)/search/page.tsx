'use client'

import { FormEvent, useState } from 'react'
import { searchWorkspace, type SearchResult } from '@/lib/api/search'

export default function ManageSearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [state, setState] = useState<'idle' | 'loading' | 'empty' | 'error'>('idle')

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!query.trim()) {
      setResults([])
      setState('empty')
      return
    }
    setState('loading')
    try {
      const next = await searchWorkspace(query.trim())
      setResults(next)
      setState(next.length ? 'idle' : 'empty')
    } catch {
      setResults([])
      setState('error')
    }
  }

  return (
    <main className='mx-auto max-w-5xl space-y-6 p-4 sm:p-8'>
      <header>
        <p className='text-sm text-gray-500'>知识库</p>
        <h1 className='text-2xl font-semibold text-gray-900'>搜索</h1>
        <p className='mt-2 text-sm text-gray-600'>搜索仅返回当前管理员可见的已发布内容。</p>
      </header>
      <form onSubmit={submit} className='flex gap-2'>
        <label className='sr-only' htmlFor='workspace-search'>搜索内容</label>
        <input id='workspace-search' value={query} onChange={event => setQuery(event.target.value)} placeholder='搜索标题、正文或分类' className='min-w-0 flex-1 rounded-lg border px-3 py-2' />
        <button type='submit' className='rounded-lg bg-gray-900 px-4 py-2 text-white' disabled={state === 'loading'}>{state === 'loading' ? '搜索中…' : '搜索'}</button>
      </form>
      {state === 'error' && <p role='alert' className='rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700'>搜索失败，请稍后重试。</p>}
      {state === 'empty' && <p className='rounded-lg border border-dashed p-6 text-sm text-gray-500'>没有找到匹配内容。</p>}
      {results.length > 0 && <ul className='divide-y rounded-lg border bg-white'>{results.map(item => <li key={item.id} className='p-4'><a href={`/notes/${item.slug}`} className='font-medium text-gray-900 hover:underline'>{item.title}</a><p className='mt-1 text-xs text-gray-500'>{item.type} · {new Date(item.updated_at).toLocaleString()}</p></li>)}</ul>}
    </main>
  )
}
