'use client'

import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { toast } from 'sonner'
import { useConfigStore } from '../stores/config-store'
import { pushSiteContent } from '../services/push-site-content'
import type { SiteContent, CardStyles } from '../stores/config-store'
import { SiteSettings, type FileItem, type ArtImageUploads, type BackgroundImageUploads, type SocialButtonImageUploads } from './site-settings'
import { ColorConfig } from './color-config'
import { HomeLayout } from './home-layout'

type TabType = 'site' | 'color' | 'layout'

interface SiteSettingsPanelProps {
	onSaved?: () => void
}

export function SiteSettingsPanel({ onSaved }: SiteSettingsPanelProps) {
	const { siteContent, setSiteContent, cardStyles, setCardStyles, regenerateBubbles } = useConfigStore()
	const [formData, setFormData] = useState<SiteContent>(siteContent)
	const [cardStylesData, setCardStylesData] = useState<CardStyles>(cardStyles)
	const [originalData, setOriginalData] = useState<SiteContent>(siteContent)
	const [originalCardStyles, setOriginalCardStyles] = useState<CardStyles>(cardStyles)
	const [isSaving, setIsSaving] = useState(false)
	const [activeTab, setActiveTab] = useState<TabType>('site')
	const [faviconItem, setFaviconItem] = useState<FileItem | null>(null)
	const [avatarItem, setAvatarItem] = useState<FileItem | null>(null)
	const [artImageUploads, setArtImageUploads] = useState<ArtImageUploads>({})
	const [backgroundImageUploads, setBackgroundImageUploads] = useState<BackgroundImageUploads>({})
	const [socialButtonImageUploads, setSocialButtonImageUploads] = useState<SocialButtonImageUploads>({})

	const resetState = () => {
		const current = { ...siteContent }
		const currentCardStyles = { ...cardStyles }
		setFormData(current)
		setCardStylesData(currentCardStyles)
		setOriginalData(current)
		setOriginalCardStyles(currentCardStyles)
		setFaviconItem(null)
		setAvatarItem(null)
		setArtImageUploads({})
		setBackgroundImageUploads({})
		setSocialButtonImageUploads({})
		setActiveTab('site')
	}

	useEffect(() => {
		resetState()
	}, [])

	useEffect(() => {
		return () => {
			if (faviconItem?.type === 'file') URL.revokeObjectURL(faviconItem.previewUrl)
			if (avatarItem?.type === 'file') URL.revokeObjectURL(avatarItem.previewUrl)
			Object.values(artImageUploads).forEach(item => { if (item.type === 'file') URL.revokeObjectURL(item.previewUrl) })
			Object.values(backgroundImageUploads).forEach(item => { if (item.type === 'file') URL.revokeObjectURL(item.previewUrl) })
			Object.values(socialButtonImageUploads).forEach(item => { if (item.type === 'file') URL.revokeObjectURL(item.previewUrl) })
		}
	}, [faviconItem, avatarItem, artImageUploads, backgroundImageUploads, socialButtonImageUploads])

	const updateThemeVariables = (theme?: SiteContent['theme']) => {
		if (typeof document === 'undefined' || !theme) return
		const { colorBrand, colorBrandSecondary, colorPrimary, colorSecondary, colorBg, colorBorder, colorCard, colorArticle } = theme
		const root = document.documentElement
		if (colorBrand) root.style.setProperty('--color-brand', colorBrand)
		if (colorBrandSecondary) root.style.setProperty('--color-brand-secondary', colorBrandSecondary)
		if (colorPrimary) root.style.setProperty('--color-primary', colorPrimary)
		if (colorSecondary) root.style.setProperty('--color-secondary', colorSecondary)
		if (colorBg) root.style.setProperty('--color-bg', colorBg)
		if (colorBorder) root.style.setProperty('--color-border', colorBorder)
		if (colorCard) root.style.setProperty('--color-card', colorCard)
		if (colorArticle) root.style.setProperty('--color-article', colorArticle)
	}

	const handleSave = async () => {
		setIsSaving(true)
		try {
			const originalArtImages = originalData.artImages ?? []
			const currentArtImages = formData.artImages ?? []
			const removedArtImages = originalArtImages.filter(orig => !currentArtImages.some(current => current.id === orig.id))

			const originalBackgroundImages = originalData.backgroundImages ?? []
			const currentBackgroundImages = formData.backgroundImages ?? []
			const removedBackgroundImages = originalBackgroundImages.filter(orig => !currentBackgroundImages.some(current => current.id === orig.id))

			setSiteContent(formData)
			setCardStyles(cardStylesData)
			updateThemeVariables(formData.theme)
			setFaviconItem(null)
			setAvatarItem(null)
			setArtImageUploads({})
			setBackgroundImageUploads({})
			setSocialButtonImageUploads({})

			try {
				await pushSiteContent(
					formData, cardStylesData, faviconItem, avatarItem,
					artImageUploads, removedArtImages,
					backgroundImageUploads, removedBackgroundImages,
					socialButtonImageUploads
				)
				toast.success('设置已保存并同步到 GitHub')
			} catch (syncError: any) {
				console.error('GitHub sync failed:', syncError)
				toast.warning(`本地设置已保存，GitHub 同步失败: ${syncError?.message || '未知错误'}`)
			}
			onSaved?.()
		} catch (error: any) {
			console.error('Failed to save:', error)
			toast.error(`保存失败: ${error?.message || '未知错误'}`)
		} finally {
			setIsSaving(false)
		}
	}

	const handleCancel = () => {
		if (faviconItem?.type === 'file') URL.revokeObjectURL(faviconItem.previewUrl)
		if (avatarItem?.type === 'file') URL.revokeObjectURL(avatarItem.previewUrl)
		Object.values(artImageUploads).forEach(item => { if (item.type === 'file') URL.revokeObjectURL(item.previewUrl) })
		Object.values(backgroundImageUploads).forEach(item => { if (item.type === 'file') URL.revokeObjectURL(item.previewUrl) })
		Object.values(socialButtonImageUploads).forEach(item => { if (item.type === 'file') URL.revokeObjectURL(item.previewUrl) })

		setFormData(originalData)
		setCardStylesData(originalCardStyles)
		setSiteContent(originalData)
		setCardStyles(originalCardStyles)
		regenerateBubbles()
		if (typeof document !== 'undefined') {
			document.title = originalData.meta.title
			const metaDescription = document.querySelector('meta[name="description"]')
			if (metaDescription) metaDescription.setAttribute('content', originalData.meta.description)
		}
		updateThemeVariables(originalData.theme)
		setFaviconItem(null)
		setAvatarItem(null)
		setArtImageUploads({})
		setBackgroundImageUploads({})
		setSocialButtonImageUploads({})
	}

	const tabs: { id: TabType; label: string }[] = [
		{ id: 'site', label: '网站设置' },
		{ id: 'color', label: '色彩配置' },
		{ id: 'layout', label: '首页布局' },
	]

	return (
		<div>
			<div className='mb-6 flex items-center justify-between'>
				<div className='flex gap-1'>
					{tabs.map(tab => (
						<button
							key={tab.id}
							onClick={() => setActiveTab(tab.id)}
							className={`relative px-4 py-2 text-sm font-medium transition-colors ${
								activeTab === tab.id ? 'text-[var(--color-brand)]' : 'text-gray-500 hover:text-gray-700'
							}`}
						>
							{tab.label}
							{activeTab === tab.id && <div className='absolute right-0 bottom-0 left-0 h-0.5 bg-[var(--color-brand)]' />}
						</button>
					))}
				</div>
				<div className='flex gap-3'>
					<motion.button
						whileHover={{ scale: 1.05 }}
						whileTap={{ scale: 0.95 }}
						onClick={handleCancel}
						disabled={isSaving}
						className='rounded-xl border border-white/40 bg-white/60 px-6 py-2 text-sm backdrop-blur-sm'
					>
						重置
					</motion.button>
					<motion.button
						whileHover={{ scale: 1.05 }}
						whileTap={{ scale: 0.95 }}
						onClick={handleSave}
						disabled={isSaving}
						className='rounded-xl bg-[var(--color-brand)] px-6 py-2 text-sm text-white'
					>
						{isSaving ? '保存中...' : '保存'}
					</motion.button>
				</div>
			</div>

			<div className='min-h-[200px]'>
				{activeTab === 'site' && (
					<SiteSettings
						formData={formData}
						setFormData={setFormData}
						faviconItem={faviconItem}
						setFaviconItem={setFaviconItem}
						avatarItem={avatarItem}
						setAvatarItem={setAvatarItem}
						artImageUploads={artImageUploads}
						setArtImageUploads={setArtImageUploads}
						backgroundImageUploads={backgroundImageUploads}
						setBackgroundImageUploads={setBackgroundImageUploads}
						socialButtonImageUploads={socialButtonImageUploads}
						setSocialButtonImageUploads={setSocialButtonImageUploads}
					/>
				)}
				{activeTab === 'color' && <ColorConfig formData={formData} setFormData={setFormData} />}
				{activeTab === 'layout' && <HomeLayout cardStylesData={cardStylesData} setCardStylesData={setCardStylesData} />}
			</div>
		</div>
	)
}
