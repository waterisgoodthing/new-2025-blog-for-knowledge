import { IMAGE_BASE_URL } from './config'

export function resolveImageUrl(url: string): string {
	if (!url) return url
	if (url.startsWith('http://') || url.startsWith('https://')) return url
	return `${IMAGE_BASE_URL}${url.startsWith('/') ? '' : '/'}${url}`
}
