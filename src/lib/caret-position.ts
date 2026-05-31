const MIRROR_STYLE_PROPS = [
	'fontFamily',
	'fontSize',
	'fontWeight',
	'fontStyle',
	'letterSpacing',
	'lineHeight',
	'textTransform',
	'wordSpacing',
	'wordWrap',
	'overflowWrap',
	'whiteSpace',
	'paddingTop',
	'paddingRight',
	'paddingBottom',
	'paddingLeft',
	'borderTopWidth',
	'borderRightWidth',
	'borderBottomWidth',
	'borderLeftWidth',
	'boxSizing',
	'tabSize',
] as const

let mirror: HTMLDivElement | null = null
let span: HTMLSpanElement | null = null
let lastTextarea: HTMLTextAreaElement | null = null
let lastWidth = 0

export function getCaretCoordinates(
	textarea: HTMLTextAreaElement,
	offset: number
): { top: number; left: number } {
	const width = textarea.clientWidth

	if (!mirror) {
		mirror = document.createElement('div')
		mirror.style.position = 'absolute'
		mirror.style.visibility = 'hidden'
		mirror.style.whiteSpace = 'pre-wrap'
		mirror.style.wordWrap = 'break-word'
		mirror.style.overflowWrap = 'break-word'
		mirror.style.overflow = 'hidden'
		span = document.createElement('span')
		span.textContent = '\u200b'
	}

	if (lastTextarea !== textarea || lastWidth !== width) {
		const style = getComputedStyle(textarea)
		for (const prop of MIRROR_STYLE_PROPS) {
			;(mirror.style as any)[prop] = (style as any)[prop]
		}
		mirror.style.width = `${width}px`
		lastTextarea = textarea
		lastWidth = width
	}

	mirror.textContent = textarea.value.substring(0, offset)
	mirror.appendChild(span!)

	if (!mirror.parentNode) document.body.appendChild(mirror)

	const spanRect = span!.getBoundingClientRect()
	const textareaRect = textarea.getBoundingClientRect()

	const top = spanRect.top - textareaRect.top
	const left = spanRect.left - textareaRect.left

	mirror.removeChild(span!)

	return { top, left }
}
