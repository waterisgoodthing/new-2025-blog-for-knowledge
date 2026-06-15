'use client'

import { StagedMistakeForm } from './components/staged-mistake-form'
import { AuthGate } from '@/components/auth-gate'

export default function WriteMistakePage() {
	return (
		<AuthGate>
			<StagedMistakeForm />
		</AuthGate>
	)
}
