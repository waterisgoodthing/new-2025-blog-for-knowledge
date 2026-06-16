import { getApiBase } from './config'

const API_BASE = getApiBase()

export type PolishAction = 'polish' | 'summarize' | 'expand' | 'continue' | 'translate_en' | 'translate_zh' | 'extract_tags' | 'generate_questions' | 'title' | 'outline' | 'tags' | 'diagram' | 'compare' | 'mindmap' | 'data_chart' | 'custom'

export type PolishCallbacks = {
	onChunk: (chunk: string) => void
	onDone: () => void
	onError: (error: string) => void
}

export async function streamPolish(
	text: string,
	action: PolishAction,
	callbacks: PolishCallbacks,
	options?: { context?: string; signal?: AbortSignal; title?: string; noteType?: string; existingTags?: string[]; custom_prompt?: string }
): Promise<void> {
	let response: Response
	try {
		response = await fetch(`${API_BASE}/api/ai/polish`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
			body: JSON.stringify({
				text,
				action,
				context: options?.context,
				title: options?.title,
				note_type: options?.noteType,
				existing_tags: options?.existingTags,
				custom_prompt: options?.custom_prompt,
			}),
			signal: options?.signal,
		})
	} catch (err: any) {
		if (err.name === 'AbortError') { callbacks.onDone(); return }
		callbacks.onError('网络错误')
		return
	}

	if (!response.ok) {
		if (response.status === 429) {
			callbacks.onError('请求过于频繁，请稍后再试')
		} else if (response.status === 401) {
			callbacks.onError('未登录或登录已过期')
		} else {
			callbacks.onError(`服务错误 (${response.status})`)
		}
		return
	}

	const reader = response.body?.getReader()
	if (!reader) {
		callbacks.onError('无法读取响应')
		return
	}

	const decoder = new TextDecoder()
	let buffer = ''

	try {
		while (true) {
			const { done, value } = await reader.read()
			if (done) break

			buffer += decoder.decode(value, { stream: true })

			const events = buffer.split('\n\n')
			buffer = events.pop() || ''

			for (const event of events) {
				const lines = event.split('\n')
				for (const line of lines) {
					if (!line.startsWith('data: ')) continue
					const data = line.slice(6).trim()
					if (data === '[DONE]') {
						callbacks.onDone()
						return
					}
					try {
						const parsed = JSON.parse(data)
						if (parsed.error) {
							callbacks.onError(parsed.error)
							return
						}
						if (parsed.chunk) {
							callbacks.onChunk(parsed.chunk)
						}
					} catch {
						continue
					}
				}
			}
		}
		callbacks.onDone()
	} catch (err: any) {
		if (err.name === 'AbortError') { callbacks.onDone(); return }
		callbacks.onError('读取响应失败')
	}
}
