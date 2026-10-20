const URL_ATTRIBUTES = ['href', 'src', 'xlink:href'] as const
const DANGEROUS_PROTOCOLS = ['javascript:', 'vbscript:', 'data:'] as const

export function parseHtml(html: string): DocumentFragment {
	const template = document.createElement('template')
	template.innerHTML = html
	return template.content
}

export function hasLiveElement(html: string, tag: string): boolean {
	return parseHtml(html).querySelector(tag) !== null
}

export function hasEventHandlerAttribute(html: string): boolean {
	return [...parseHtml(html).querySelectorAll('*')].some(element => [...element.attributes].some(attribute => attribute.name.toLowerCase().startsWith('on')))
}

export function hasDangerousUrlAttribute(html: string): boolean {
	return [...parseHtml(html).querySelectorAll('*')].some(element =>
		URL_ATTRIBUTES.some(name => {
			const value = element.getAttribute(name)
			return value !== null && DANGEROUS_PROTOCOLS.some(protocol => value.trim().toLowerCase().startsWith(protocol))
		})
	)
}
