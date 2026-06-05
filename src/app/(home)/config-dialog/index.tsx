'use client'

import { DialogModal } from '@/components/dialog-modal'
import { SiteSettingsPanel } from './site-settings-panel'

interface ConfigDialogProps {
	open: boolean
	onClose: () => void
}

export default function ConfigDialog({ open, onClose }: ConfigDialogProps) {
	return (
		<DialogModal open={open} onClose={onClose} className='card scrollbar-none max-h-[90vh] min-h-[600px] w-[640px] overflow-y-auto'>
			<SiteSettingsPanel onSaved={onClose} />
		</DialogModal>
	)
}
