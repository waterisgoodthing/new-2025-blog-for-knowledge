import { apiFetch } from "./client";
import { getApiBase } from "./config";

const API_BASE = getApiBase()

export interface DiagramItem {
  type: "flowchart" | "timeline" | "formula_breakdown" | "network_topology" | "geometry" | "state_machine";
  title: string;
  mermaid: string;
}

export interface AnalyzeResponse {
  title: string;
  question: string;
  correct_answer: string;
  analysis: string;
  knowledge_points: string;
  subject: string;
  difficulty: string;
  tags: string[];
  error_reason?: string;
  key_step?: string;
  similar_traps?: string[];
  generalization?: string;
  review_advice?: string;
  variant_questions?: string[];
  related_notes?: { slug: string; title: string }[];
  diagrams?: DiagramItem[];
}

export type StreamEvent =
  | { type: 'received'; label: string }
  | { type: 'progress'; step: string; label: string }
  | { type: 'done'; label: string }
  | { type: 'result'; data: AnalyzeResponse }
  | { type: 'error'; message: string }

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

export async function analyzeMistake(images: { base64: string; mime_type: string }[]): Promise<AnalyzeResponse> {
  return apiFetch<AnalyzeResponse>("/api/ai/analyze", {
    method: "POST",
    body: JSON.stringify({ images }),
  });
}

export async function analyzeText(text: string): Promise<AnalyzeResponse> {
  return apiFetch<AnalyzeResponse>("/api/ai/analyze-text", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function analyzeMistakeStream(
  images: { base64: string; mime_type: string }[],
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const token = getAuthToken()
  if (!token) { onEvent({ type: 'error', message: '未登录' }); return }

  let response: Response
  try {
    response = await fetch(`${API_BASE}/api/ai/analyze-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ images }),
      signal,
    })
  } catch (err: any) {
    if (err.name === 'AbortError') return
    onEvent({ type: 'error', message: '网络错误' })
    return
  }

  if (!response.ok) {
    onEvent({ type: 'error', message: `服务错误 (${response.status})` })
    return
  }

  const reader = response.body?.getReader()
  if (!reader) { onEvent({ type: 'error', message: '无法读取响应' }); return }

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
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'error') {
              onEvent({ type: 'error', message: parsed.message || '未知错误' })
              return
            }
            if (parsed.type === 'done') {
              onEvent({ type: 'done', label: parsed.label || '完成' })
              return
            }
            if (parsed.type === 'result') {
              onEvent({ type: 'result', data: parsed.data })
            } else {
              onEvent(parsed as StreamEvent)
            }
          } catch {
            continue
          }
        }
      }
    }
  } catch (err: any) {
    if (err.name === 'AbortError') return
    onEvent({ type: 'error', message: '读取响应失败' })
  }
}

export async function analyzeTextStream(
  text: string,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const token = getAuthToken()
  if (!token) { onEvent({ type: 'error', message: '未登录' }); return }

  let response: Response
  try {
    response = await fetch(`${API_BASE}/api/ai/analyze-text-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ text }),
      signal,
    })
  } catch (err: any) {
    if (err.name === 'AbortError') return
    onEvent({ type: 'error', message: '网络错误' })
    return
  }

  if (!response.ok) {
    onEvent({ type: 'error', message: `服务错误 (${response.status})` })
    return
  }

  const reader = response.body?.getReader()
  if (!reader) { onEvent({ type: 'error', message: '无法读取响应' }); return }

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
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'error') {
              onEvent({ type: 'error', message: parsed.message || '未知错误' })
              return
            }
            if (parsed.type === 'done') {
              onEvent({ type: 'done', label: parsed.label || '完成' })
              return
            }
            if (parsed.type === 'result') {
              onEvent({ type: 'result', data: parsed.data })
            } else {
              onEvent(parsed as StreamEvent)
            }
          } catch {
            continue
          }
        }
      }
    }
  } catch (err: any) {
    if (err.name === 'AbortError') return
    onEvent({ type: 'error', message: '读取响应失败' })
  }
}
