const LOCAL_API_BASE = 'http://localhost:8000'

function isLocalApiBase(url: string): boolean {
	try {
		const { hostname } = new URL(url)
		return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1'
	} catch {
		return false
	}
}

export function getApiBase(): string {
	const apiBase = process.env.NEXT_PUBLIC_API_URL || LOCAL_API_BASE

	if (process.env.NODE_ENV === 'production' && isLocalApiBase(apiBase)) {
		throw new Error('NEXT_PUBLIC_API_URL must be set to a non-localhost URL in production')
	}

	return apiBase.replace(/\/$/, '')
}

export const IMAGE_BASE_URL = (process.env.NEXT_PUBLIC_IMAGE_BASE_URL || getApiBase()).replace(/\/$/, '')
