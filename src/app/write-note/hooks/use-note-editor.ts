'use client'

import { useCallback, useRef, useState, type RefObject } from 'react'
import dayjs from 'dayjs'

const DEFAULT_FALLBACK = '文本'

export type SlashState = {
	open: boolean
	position: { top: number; left: number }
	query: string
	commandStart: number
}

type UseNoteEditorOptions = {
	textareaRef: RefObject<HTMLTextAreaElement | null>
	content: string
	onContentChange: (content: string) => void
}

type UseNoteEditorReturn = {
	handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void
	handleChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
	insertText: (text: string) => void
	wrapSelection: (before: string, after: string, fallback?: string) => void
	slashState: SlashState
	closeSlash: () => void
	executeSlash: (insertText: string) => void
}

export function useNoteEditor({
	textareaRef,
	content,
	onContentChange,
}: UseNoteEditorOptions): UseNoteEditorReturn {
	const [slashState, setSlashState] = useState<SlashState>({
		open: false,
		position: { top: 0, left: 0 },
		query: '',
		commandStart: 0,
	})
	const slashStateRef = useRef(slashState)
	slashStateRef.current = slashState

	const closeSlash = useCallback(() => {
		setSlashState(s => ({ ...s, open: false, query: '' }))
	}, [])

	const insertText = useCallback(
		(text: string) => {
			const textarea = textareaRef.current
			if (!textarea) return

			textarea.focus()
			const success = document.execCommand('insertText', false, text)

			if (!success) {
				const { selectionStart, selectionEnd, value } = textarea
				const before = value.substring(0, selectionStart)
				const after = value.substring(selectionEnd)
				onContentChange(before + text + after)
				setTimeout(() => {
					const newPos = selectionStart + text.length
					textarea.setSelectionRange(newPos, newPos)
					textarea.focus()
				}, 0)
			}
		},
		[textareaRef, onContentChange]
	)

	const executeSlash = useCallback(
		(insert: string) => {
			const textarea = textareaRef.current
			if (!textarea) return

			const { commandStart, query } = slashStateRef.current
			const slashEnd = commandStart + 1 + query.length

			textarea.setSelectionRange(commandStart, slashEnd)
			closeSlash()

			setTimeout(() => {
				insertText(insert)
			}, 0)
		},
		[textareaRef, insertText, closeSlash]
	)

	const wrapSelection = useCallback(
		(before: string, after: string, fallback: string = DEFAULT_FALLBACK) => {
			const textarea = textareaRef.current
			if (!textarea) return

			const { selectionStart, selectionEnd, value } = textarea
			const selectedText = value.substring(selectionStart, selectionEnd)
			const textBefore = value.substring(0, selectionStart)
			const textAfter = value.substring(selectionEnd)

			const isWrapped = textBefore.endsWith(before) && textAfter.startsWith(after)

			if (isWrapped && selectedText) {
				textarea.setSelectionRange(selectionStart - before.length, selectionEnd + after.length)
				insertText(selectedText)
			} else {
				const text = selectedText || fallback
				insertText(`${before}${text}${after}`)
				if (!selectedText) {
					setTimeout(() => {
						textarea.setSelectionRange(selectionStart + before.length, selectionStart + before.length + text.length)
						textarea.focus()
					}, 0)
				}
			}
		},
		[textareaRef, insertText]
	)

	const handleKeyDown = useCallback(
		(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
			const textarea = textareaRef.current
			if (!textarea) return

			const { selectionStart, selectionEnd, value } = textarea
			const selectedText = value.substring(selectionStart, selectionEnd)
			const mod = e.ctrlKey || e.metaKey

			if (mod && e.key === 'b') {
				e.preventDefault()
				wrapSelection('**', '**')
				return
			}

			if (mod && e.key === 'i') {
				e.preventDefault()
				wrapSelection('*', '*')
				return
			}

			if (mod && e.key === 'k') {
				e.preventDefault()
				const text = selectedText || DEFAULT_FALLBACK
				insertText(`[${text}](url)`)
				setTimeout(() => {
					const urlStart = selectionStart + text.length + 3
					textarea.setSelectionRange(urlStart, urlStart + 3)
					textarea.focus()
				}, 0)
				return
			}

			if (mod && e.shiftKey && e.key === 'T') {
				e.preventDefault()
				insertText(dayjs().format('YYYY-MM-DD HH:mm'))
				return
			}

			if (e.key === 'Tab' && !e.shiftKey) {
				e.preventDefault()
				insertText('\t')
				return
			}

			if (e.key === 'Tab' && e.shiftKey) {
				e.preventDefault()
				const lineStart = value.lastIndexOf('\n', selectionStart - 1) + 1
				const line = value.substring(lineStart)

				if (line.startsWith('\t')) {
					textarea.setSelectionRange(lineStart, lineStart + 1)
					insertText('')
				} else if (line.startsWith('  ')) {
					textarea.setSelectionRange(lineStart, lineStart + 2)
					insertText('')
				}
				return
			}
		},
		[textareaRef, insertText, wrapSelection]
	)

	const handleChange = useCallback(
		(e: React.ChangeEvent<HTMLTextAreaElement>) => {
			const newValue = e.target.value
			onContentChange(newValue)

			const textarea = textareaRef.current
			if (!textarea) return

			const cursor = e.target.selectionStart || 0
			const textBeforeCursor = newValue.substring(0, cursor)

			const slashIdx = textBeforeCursor.lastIndexOf('/')
			if (slashStateRef.current.open) {
				if (slashIdx === -1 || cursor < slashIdx) {
					closeSlash()
					return
				}
				const q = textBeforeCursor.substring(slashIdx + 1)
				if (q.includes(' ')) {
					closeSlash()
					return
				}

				const rect = textarea.getBoundingClientRect()
				const lineHeight = parseInt(getComputedStyle(textarea).lineHeight) || 20
				const lines = textBeforeCursor.split('\n')
				const currentLine = lines.length - 1
				const charWidth = 8
				const currentCol = lines[lines.length - 1].length

				setSlashState({
					open: true,
					position: {
						top: rect.top + (currentLine + 1) * lineHeight + 4,
						left: rect.left + Math.min(currentCol * charWidth, rect.width - 200),
					},
					query: q,
					commandStart: slashIdx,
				})
			} else {
				if (slashIdx >= 0 && slashIdx === cursor - (textBeforeCursor.length - slashIdx)) {
					const charAfterSlash = newValue[slashIdx + 1]
					if (charAfterSlash === undefined || charAfterSlash === ' ' || charAfterSlash === '\n') return

					const rect = textarea.getBoundingClientRect()
					const lineHeight = parseInt(getComputedStyle(textarea).lineHeight) || 20
					const lines = textBeforeCursor.split('\n')
					const currentLine = lines.length - 1
					const charWidth = 8
					const currentCol = lines[lines.length - 1].length

					setSlashState({
						open: true,
						position: {
							top: rect.top + (currentLine + 1) * lineHeight + 4,
							left: rect.left + Math.min(currentCol * charWidth, rect.width - 200),
						},
						query: textBeforeCursor.substring(slashIdx + 1),
						commandStart: slashIdx,
					})
				}
			}
		},
		[textareaRef, onContentChange, closeSlash]
	)

	return { handleKeyDown, handleChange, insertText, wrapSelection, slashState, closeSlash, executeSlash }
}
