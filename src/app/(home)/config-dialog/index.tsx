'use client'

import { Uiv2Modal as Modal } from '@/components/ui-v2/Modal'
import { SiteSettingsPanel } from './site-settings-panel'

interface ConfigDialogProps {
	open: boolean
	onClose: () => void
}

export default function ConfigDialog({ open, onClose }: ConfigDialogProps) {
	return (
		<Modal bare ariaLabel='站点配置' open={open} onClose={onClose} className='card scrollbar-none max-h-[90vh] min-h-[600px] w-[640px] overflow-y-auto'>
			<SiteSettingsPanel onSaved={onClose} />
		</Modal>
	)
}
