'use client'

import { useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { getApiBase } from '@/lib/api/config'

interface ProviderInfo {
	name: string
	model: string
	base_url_label: string
	role: string
	configured: boolean
}

interface PromptTemplate {
	name: string
	description: string
	prompt: string
	route: string
}

interface PromptGroups {
	[group: string]: { [key: string]: PromptTemplate }
}

interface TestResult {
	success: boolean
	provider_used: string
	fallback_used: boolean
	latency_ms: number
	output: any
	error?: string
	attempts: { provider: string; model: string; success: boolean; latency_ms: number; error: string }[]
}

export function AITab() {
	const [providers, setProviders] = useState<ProviderInfo[]>([])
	const [prompts, setPrompts] = useState<PromptGroups>({})
	const [loading, setLoading] = useState(true)
	const [selectedGroup, setSelectedGroup] = useState('')
	const [selectedKey, setSelectedKey] = useState('')
	const [draftPrompt, setDraftPrompt] = useState('')
	const [sampleInput, setSampleInput] = useState('')
	const [testResult, setTestResult] = useState<TestResult | null>(null)
	const [testing, setTesting] = useState(false)

	const load = useCallback(async () => {
		setLoading(true)
		try {
			const API_BASE = getApiBase()
			const [provRes, promptRes] = await Promise.all([
				fetch(`${API_BASE}/api/ai/provider-status`, { credentials: 'include' }),
				fetch(`${API_BASE}/api/ai/prompts`, { credentials: 'include' }),
			])
			if (provRes.ok) setProviders(await provRes.json())
			if (promptRes.ok) {
				const data = await promptRes.json()
				setPrompts(data)
				const firstGroup = Object.keys(data)[0]
				if (firstGroup) {
					setSelectedGroup(firstGroup)
					const firstKey = Object.keys(data[firstGroup])[0]
					if (firstKey) {
						setSelectedKey(firstKey)
						setDraftPrompt(data[firstGroup][firstKey].prompt)
					}
				}
			}
		} catch {
			// ignore
		} finally {
			setLoading(false)
		}
	}, [])

	useEffect(() => { load() }, [load])

	useEffect(() => {
		if (selectedGroup && selectedKey && prompts[selectedGroup]?.[selectedKey]) {
			setDraftPrompt(prompts[selectedGroup][selectedKey].prompt)
			setTestResult(null)
		}
	}, [selectedGroup, selectedKey, prompts])

	const handleTest = async () => {
		if (!sampleInput.trim()) return toast.warning('请输入测试输入')
		setTesting(true)
		setTestResult(null)
		try {
			const API_BASE = getApiBase()
			const res = await fetch(`${API_BASE}/api/ai/prompt-test`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({
					prompt_key: `${selectedGroup}.${selectedKey}`,
					sample_input: sampleInput,
					custom_prompt: draftPrompt !== (prompts[selectedGroup]?.[selectedKey]?.prompt || '') ? draftPrompt : undefined,
					route: prompts[selectedGroup]?.[selectedKey]?.route || 'text JSON',
				}),
			})
			if (res.ok) {
				setTestResult(await res.json())
			} else {
				const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
				toast.error('测试失败: ' + (err.detail || res.status))
			}
		} catch (e: any) {
			toast.error('测试失败: ' + e.message)
		} finally {
			setTesting(false)
		}
	}

	const handleReset = () => {
		if (selectedGroup && selectedKey && prompts[selectedGroup]?.[selectedKey]) {
			setDraftPrompt(prompts[selectedGroup][selectedKey].prompt)
			toast.success('已重置为默认提示词')
		}
	}

	if (loading) {
		return <div className='py-20 text-center text-gray-400'>加载中...</div>
	}

	return (
		<div className='space-y-6'>
			<div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
				<h3 className='mb-4 font-medium'>Provider Status</h3>
				<div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
					{providers.map(p => (
						<div key={p.name} className='rounded-xl bg-white/40 p-4'>
							<div className='flex items-center justify-between'>
								<span className='text-sm font-medium'>{p.name}</span>
								<span className={`inline-block rounded-full px-2 py-0.5 text-xs ${
									p.configured ? 'bg-green-500/10 text-green-600' : 'bg-red-500/10 text-red-600'
								}`}>
									{p.configured ? '已配置' : '未配置'}
								</span>
							</div>
							<div className='mt-2 space-y-1 text-xs text-gray-500'>
								<div>Model: <span className='font-mono text-gray-700'>{p.model}</span></div>
								<div>Endpoint: {p.base_url_label}</div>
								<div>Role: {p.role}</div>
							</div>
						</div>
					))}
				</div>
			</div>

			<div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
				<h3 className='mb-4 font-medium'>Prompt Lab</h3>
				<div className='grid gap-4 lg:grid-cols-[220px_1fr_1fr]'>
					<div className='space-y-3'>
						{Object.entries(prompts).map(([group, templates]) => (
							<div key={group}>
								<div className='mb-1 text-xs font-semibold uppercase text-gray-400'>{group}</div>
								<div className='space-y-1'>
									{Object.entries(templates).map(([key, tmpl]) => (
										<button
											key={key}
											onClick={() => { setSelectedGroup(group); setSelectedKey(key) }}
											className={`w-full rounded-lg px-3 py-2 text-left text-sm transition-colors ${
												selectedGroup === group && selectedKey === key
													? 'bg-[var(--color-brand)]/10 text-[var(--color-brand)]'
													: 'hover:bg-white/60 text-gray-600'
											}`}
										>
											<div className='font-medium'>{tmpl.name}</div>
											<div className='text-xs text-gray-400'>{tmpl.route}</div>
										</button>
									))}
								</div>
							</div>
						))}
					</div>

					<div className='space-y-3'>
						<div className='flex items-center justify-between'>
							<span className='text-sm font-medium text-gray-700'>Prompt Editor</span>
							<button
								onClick={handleReset}
								className='rounded-lg bg-white/60 px-2 py-1 text-xs text-gray-500 hover:bg-white/80'
							>
								Reset
							</button>
						</div>
						<textarea
							value={draftPrompt}
							onChange={e => setDraftPrompt(e.target.value)}
							rows={12}
							className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-3 font-mono text-xs leading-5 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
						/>
						{prompts[selectedGroup]?.[selectedKey]?.description && (
							<p className='text-xs text-gray-400'>{prompts[selectedGroup][selectedKey].description}</p>
						)}
					</div>

					<div className='space-y-3'>
						<div className='text-sm font-medium text-gray-700'>Test Panel</div>
						<textarea
							value={sampleInput}
							onChange={e => setSampleInput(e.target.value)}
							placeholder='输入测试内容...'
							rows={4}
							className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-3 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
						/>
						<button
							onClick={handleTest}
							disabled={testing || !sampleInput.trim()}
							className='w-full rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white disabled:opacity-50'
						>
							{testing ? 'Testing...' : 'Run Test'}
						</button>

						{testResult && (
							<div className='rounded-xl border border-white/40 bg-white/60 p-4 text-sm backdrop-blur-sm'>
								<div className='mb-2 flex items-center gap-2'>
									<span className={`rounded-full px-2 py-0.5 text-xs ${
										testResult.success ? 'bg-green-500/10 text-green-600' : 'bg-red-500/10 text-red-600'
									}`}>
										{testResult.success ? 'Success' : 'Failed'}
									</span>
									<span className='text-xs text-gray-400'>{testResult.latency_ms}ms</span>
								</div>
								<div className='mb-2 space-y-1 text-xs text-gray-500'>
									<div>Provider: <span className='font-medium text-gray-700'>{testResult.provider_used || 'N/A'}</span></div>
									{testResult.fallback_used && (
										<div className='text-amber-600'>Fallback was used</div>
									)}
								</div>
								{testResult.attempts.length > 0 && (
									<div className='mb-2 space-y-1'>
										{testResult.attempts.map((a, i) => (
											<div key={i} className='flex items-center gap-2 text-xs'>
												<span className={a.success ? 'text-green-600' : 'text-red-600'}>
													{a.success ? '✓' : '✗'}
												</span>
												<span className='font-mono'>{a.provider}</span>
												<span className='text-gray-400'>{a.latency_ms}ms</span>
												{a.error && <span className='text-red-500 truncate max-w-[150px]'>{a.error}</span>}
											</div>
										))}
									</div>
								)}
								{testResult.output && (
									<pre className='mt-2 max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-xs'>
										{typeof testResult.output === 'string' ? testResult.output : JSON.stringify(testResult.output, null, 2)}
									</pre>
								)}
								{testResult.error && (
									<div className='mt-2 rounded-lg bg-red-50 p-3 text-xs text-red-600'>{testResult.error}</div>
								)}
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	)
}
