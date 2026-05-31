'use client'

import { useState, useEffect } from 'react'

export function useNoteEditorTab() {
	const [tab, setTab] = useState<'edit' | 'preview'>('edit')

	useEffect(() => {
		const handler = (e: KeyboardEvent) => {
			if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
				e.preventDefault()
				setTab(t => (t === 'edit' ? 'preview' : 'edit'))
			}
		}
		window.addEventListener('keydown', handler)
		return () => window.removeEventListener('keydown', handler)
	}, [])

	return { tab, setTab }
}
