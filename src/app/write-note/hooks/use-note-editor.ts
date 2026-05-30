'use client'

import { useCallback, type RefObject } from 'react'
import dayjs from 'dayjs'

const DEFAULT_FALLBACK = '文本'

type UseNoteEditorOptions = {
	textareaRef: RefObject<HTMLTextAreaElement | null>
	content: string
	onContentChange: (content: string) => void
}

type UseNoteEditorReturn = {
	handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void
	insertText: (text: string) => void
	wrapSelection: (before: string, after: string, fallback?: string) => void
}

export function useNoteEditor({
	textareaRef,
	content,
	onContentChange,
}: UseNoteEditorOptions): UseNoteEditorReturn {
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

	return { handleKeyDown, insertText, wrapSelection }
}
