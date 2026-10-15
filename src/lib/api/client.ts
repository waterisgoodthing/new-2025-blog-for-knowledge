import { getApiBase } from './config'

const API_BASE = getApiBase()

export type ApiErrorKind = 'network' | 'cors' | 'auth' | 'backend' | 'upstream' | 'abort'

export class ApiError extends Error {
  public status: number
  public kind: ApiErrorKind

  constructor(status: number, message: string, kind: ApiErrorKind = 'backend') {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.kind = kind
  }
}

function classifyFetchError(err: unknown): ApiError {
  const msg = err instanceof Error ? err.message : String(err)

  if (err instanceof DOMException && err.name === 'AbortError') {
    return new ApiError(0, '请求已取消', 'abort')
  }

  if (
    msg.includes('Failed to fetch') ||
    msg.includes('NetworkError') ||
    msg.includes('Network request failed') ||
    msg.includes('ERR_CONNECTION') ||
    msg.includes('ERR_NAME_NOT_RESOLVED') ||
    msg.includes('ERR_TUNNEL') ||
    msg.includes('Load failed')
  ) {
    return new ApiError(0, `网络连接失败: 无法访问 API 服务器 (${API_BASE})`, 'network')
  }

  return new ApiError(0, `请求失败: ${msg}`, 'network')
}

function classifyHttpResponse(res: Response, body: string): ApiError {
  const status = res.status

  if (status === 401 || status === 403) {
    let detail = '登录已过期或无权限访问'
    try {
      const parsed = JSON.parse(body)
      if (parsed.detail) detail = parsed.detail
    } catch {}
    return new ApiError(status, detail, 'auth')
  }

  const contentType = res.headers.get('content-type') || ''
  if (!contentType.includes('application/json') && body.length > 0) {
    if (body.includes('cf-error-code') || body.includes('cloudflare') || status === 530 || status === 1033) {
      return new ApiError(status, 'Cloudflare 隧道不可用，请检查 API 服务状态', 'upstream')
    }
    if (body.includes('<html') || body.includes('<!DOCTYPE')) {
      return new ApiError(status, `API 返回了非 JSON 响应 (${status})，可能是 Access 认证重定向`, 'upstream')
    }
    return new ApiError(status, `API 返回非 JSON 响应 (${status})`, 'upstream')
  }

  let detail = body
  try {
    const parsed = JSON.parse(body)
    if (parsed.detail) {
      detail = typeof parsed.detail === 'string' ? parsed.detail : JSON.stringify(parsed.detail)
    }
  } catch {}

  return new ApiError(status, detail || `服务错误 (${status})`, 'backend')
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  }
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      credentials: 'include',
      headers,
    })
  } catch (err) {
    throw classifyFetchError(err)
  }

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw classifyHttpResponse(res, text)
  }

  if (res.status === 204) return undefined as T

  try {
    return await res.json()
  } catch {
    throw new ApiError(res.status, '响应解析失败: 返回的不是有效 JSON', 'upstream')
  }
}
