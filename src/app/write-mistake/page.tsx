'use client'

import { MistakeForm } from './components/mistake-form'
import { AuthGate } from '@/components/auth-gate'

export default function WriteMistakePage() {
	return (
		<AuthGate>
			<MistakeForm mode='create' />
		</AuthGate>
	)
}
