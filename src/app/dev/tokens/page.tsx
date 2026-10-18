'use client'

/**
 * Phase 1 (VSC-02-B) — 双表面 Token 检验台.
 *
 * Route: `/dev/tokens`. Do not move this under a `_`-prefixed folder — Next.js
 * treats those as private folders and emits no route. Access is gated by
 * AuthGate (UX only); the page reads no private data.
 */

import React, { useState, useEffect } from 'react'
import { AuthGate } from '@/components/auth-gate'
import { Sun, Moon, Mail, Lock, Eye, EyeOff, Sparkles, ChevronRight, ShieldCheck, ArrowUpRight } from 'lucide-react'

export default function TokensDemoPage() {
	return (
		<AuthGate>
			<TokensDemoContent />
		</AuthGate>
	)
}

function TokensDemoContent() {
	const [isDark, setIsDark] = useState(false)
	const [isScrolled, setIsScrolled] = useState(false)
	const [showPassword, setShowPassword] = useState(false)
	const [activeTab, setActiveTab] = useState<'all' | 'editorial' | 'admin'>('all')

	// Handle scroll for sticky glass bar transition demo
	useEffect(() => {
		const handleScroll = () => {
			setIsScrolled(window.scrollY > 40)
		}
		window.addEventListener('scroll', handleScroll, { passive: true })
		return () => window.removeEventListener('scroll', handleScroll)
	}, [])

	// Theme toggle. Scope the attribute to this page's own subtree instead of
	// <html>: writing `data-theme` onto documentElement would leak dark tokens
	// into the app shell and persist across client-side navigation.
	const toggleTheme = () => {
		setIsDark(prev => !prev)
	}

	return (
		<div
			className='min-h-screen transition-colors duration-300'
			data-theme={isDark ? 'dark' : 'light'}
			style={{
				background: isDark ? 'var(--editorial-bg, #1a1311)' : 'var(--editorial-bg, #f5f1eb)'
			}}
		>
			{/* =========================================================================
			    TOP GLASS BAR (Navigation / Overlay Demo)
			    Demonstrates floating (at top) → sticky (on scroll) + backdrop blur
			========================================================================= */}
			<header
				className={`sticky top-0 z-50 transition-all duration-300 ${
					isScrolled ? 'py-3 shadow-md' : 'py-5 shadow-none'
				}`}
				style={{
					background: 'var(--nav-glass-bg, rgba(255, 255, 255, 0.8))',
					backdropFilter: 'var(--nav-blur, blur(20px))',
					WebkitBackdropFilter: 'var(--nav-blur, blur(20px))',
					borderBottom: '1px solid var(--nav-glass-border, rgba(255, 255, 255, 0.3))',
					boxShadow: isScrolled ? 'var(--nav-glass-shadow, 0 8px 32px rgba(0, 0, 0, 0.08))' : 'none'
				}}
			>
				<div className='mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8'>
					{/* Brand & Status */}
					<div className='flex items-center gap-3'>
						<div
							className='flex h-9 w-9 items-center justify-center rounded-xl text-white shadow-sm'
							style={{ background: 'var(--brand, #3db8a8)' }}
						>
							<Sparkles className='h-5 w-5' />
						</div>
						<div>
							<div className='flex items-center gap-2'>
								<span
									className='font-semibold tracking-tight'
									style={{ color: 'var(--editorial-text-primary, #4a3832)' }}
								>
									UI Token System
								</span>
								<span
									className='rounded-full px-2 py-0.5 text-xs font-medium'
									style={{
										background: isScrolled
											? 'var(--nav-active-bg, rgba(61, 184, 168, 0.15))'
											: 'rgba(0, 0, 0, 0.05)',
										color: isScrolled ? 'var(--brand-ink, #1f7a6e)' : 'inherit'
									}}
								>
									{isScrolled ? 'Sticky (Scrolled)' : 'Floating (Top)'}
								</span>
							</div>
							<p className='text-xs' style={{ color: 'var(--editorial-text-tertiary, #b8a393)' }}>
								Phase 1 · Dual-Surface Architecture Demo
							</p>
						</div>
					</div>

					{/* Navigation Pills */}
					<div className='hidden items-center gap-1.5 sm:flex'>
						<button
							onClick={() => setActiveTab('all')}
							className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
								activeTab === 'all'
									? 'text-white'
									: isDark ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'
							}`}
							style={{
								background: activeTab === 'all' ? 'var(--brand, #3db8a8)' : 'transparent'
							}}
						>
							双表面全景对比
						</button>
						<button
							onClick={() => setActiveTab('editorial')}
							className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
								activeTab === 'editorial'
									? 'text-white'
									: isDark ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'
							}`}
							style={{
								background: activeTab === 'editorial' ? 'var(--editorial-accent, #b85e4c)' : 'transparent'
							}}
						>
							Editorial 表面
						</button>
						<button
							onClick={() => setActiveTab('admin')}
							className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
								activeTab === 'admin'
									? 'text-white'
									: isDark ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'
							}`}
							style={{
								background: activeTab === 'admin' ? 'var(--brand-ink, #1f7a6e)' : 'transparent'
							}}
						>
							Admin 表面
						</button>
					</div>

					{/* Action Buttons: Dark/Light Mode toggle & Indicator */}
					<div className='flex items-center gap-2'>
						<button
							onClick={toggleTheme}
							className='flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-all hover:shadow-sm'
							style={{
								borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
								background: 'var(--nav-hover-bg, rgba(255, 255, 255, 0.6))',
								color: 'inherit'
							}}
							title='切换深色/浅色模式'
						>
							{isDark ? (
								<>
									<Sun className='h-3.5 w-3.5 text-amber-400' />
									<span>Light</span>
								</>
							) : (
								<>
									<Moon className='h-3.5 w-3.5 text-slate-700' />
									<span>Dark</span>
								</>
							)}
						</button>

						<div
							className='flex items-center gap-1 rounded-full px-2.5 py-1 text-xs'
							style={{
								background: 'var(--nav-active-bg, rgba(61, 184, 168, 0.12))',
								color: 'var(--brand-ink, #1f7a6e)'
							}}
						>
							<ShieldCheck className='h-3.5 w-3.5' />
							<span className='font-mono text-[11px]'>AuthGate Verified</span>
						</div>
					</div>
				</div>
			</header>

			{/* =========================================================================
			    MAIN CONTENT AREA: DUAL SURFACE COMPARISON
			========================================================================= */}
			<main className='mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8'>
				{/* Introduction Banner */}
				<div
					className='mb-8 rounded-2xl border p-6 transition-all'
					style={{
						background: 'var(--nav-glass-bg, rgba(255, 255, 255, 0.7))',
						borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
						backdropFilter: 'var(--nav-blur, blur(20px))'
					}}
				>
					<div className='flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between'>
						<div>
							<h1
								className='text-xl font-bold tracking-tight sm:text-2xl'
								style={{ color: 'var(--editorial-text-primary, #4a3832)' }}
							>
								双表面设计系统规范检验台 (Phase 1)
							</h1>
							<p className='mt-1 text-sm' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
								合并 Legacy (site-content.json) + Tailwind (theme.css) + UI V2 (tokens.css) 为单一真相来源。
							</p>
						</div>
						<div className='flex flex-wrap items-center gap-2 text-xs'>
							<span className='inline-flex items-center gap-1 rounded-lg border border-amber-300 bg-amber-50 px-2.5 py-1 font-medium text-amber-800'>
								Editorial: #f5f1eb (Warm Beige)
							</span>
							<span className='inline-flex items-center gap-1 rounded-lg border border-teal-300 bg-teal-50 px-2.5 py-1 font-medium text-teal-800'>
								Admin: #f0fffe → #f5fbfb (Cool Gradient)
							</span>
							<span className='inline-flex items-center gap-1 rounded-lg border border-emerald-300 bg-emerald-50 px-2.5 py-1 font-medium text-emerald-800'>
								Brand: #3db8a8 (Unified Teal)
							</span>
						</div>
					</div>
				</div>

				{/* Dual Surface Columns */}
				<div className='grid grid-cols-1 gap-8 lg:grid-cols-2'>
					{/* -----------------------------------------------------------------
					    LEFT: EDITORIAL SURFACE (公开阅读表面)
					----------------------------------------------------------------- */}
					{(activeTab === 'all' || activeTab === 'editorial') && (
						<section
							className='flex flex-col gap-6 rounded-3xl border p-6 sm:p-8 transition-all'
							style={{
								background: 'var(--editorial-bg, #f5f1eb)',
								borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
								color: 'var(--editorial-text-primary, #4a3832)'
							}}
						>
							{/* Surface Header */}
							<div className='border-b pb-4' style={{ borderColor: 'var(--editorial-divider, rgba(74, 56, 50, 0.08))' }}>
								<div className='flex items-center justify-between'>
									<div className='flex items-center gap-2'>
										<span
											className='flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold text-white'
											style={{ background: 'var(--editorial-accent, #b85e4c)' }}
										>
											E
										</span>
										<span className='text-xs font-semibold tracking-wider uppercase' style={{ color: 'var(--editorial-accent, #b85e4c)' }}>
											Editorial Surface · 公开阅读表面
										</span>
									</div>
									<span className='text-xs font-mono' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
										#f5f1eb warm beige
									</span>
								</div>
								<h2 className='mt-2 text-2xl font-bold tracking-tight sm:text-3xl' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
									沉浸、优雅、克制
								</h2>
								<p className='mt-1 text-sm' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
									适用于 Blog 文章、随想日记、公开知识库。以大留白、暖白表面与砖红序号营造纯净阅读节奏。
								</p>
							</div>

							{/* Editorial 4 Principles Cards (Directly matching editorial-whitespace-reference.png) */}
							<div className='grid grid-cols-1 gap-4 sm:grid-cols-2'>
								{/* Card 1: Whitespace 留白 */}
								<div
									className='flex flex-col gap-3 rounded-2xl border p-5 transition-shadow hover:shadow-md'
									style={{
										background: 'var(--editorial-surface, #fffef8)',
										borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
										boxShadow: 'var(--ui-shadow-sm, 0 1px 4px rgba(0, 0, 0, 0.06))'
									}}
								>
									<div className='flex items-center gap-2'>
										<span
											className='flex h-7 w-7 items-center justify-center rounded-lg text-sm font-bold text-white'
											style={{ background: 'var(--editorial-accent, #b85e4c)' }}
										>
											1
										</span>
										<span className='font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
											Whitespace 留白
										</span>
									</div>
									<h4 className='text-lg font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
										留白
									</h4>
									<p className='text-xs leading-relaxed' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
										别把页面塞满，元素之间多留空。留白越舍得，越高级。
									</p>
								</div>

								{/* Card 2: Typography 排版 */}
								<div
									className='flex flex-col gap-3 rounded-2xl border p-5 transition-shadow hover:shadow-md'
									style={{
										background: 'var(--editorial-surface, #fffef8)',
										borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
										boxShadow: 'var(--ui-shadow-sm, 0 1px 4px rgba(0, 0, 0, 0.06))'
									}}
								>
									<div className='flex items-center gap-2'>
										<span
											className='flex h-7 w-7 items-center justify-center rounded-lg text-sm font-bold text-white'
											style={{ background: 'var(--editorial-accent, #b85e4c)' }}
										>
											2
										</span>
										<span className='font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
											Typography 排版
										</span>
									</div>
									<h4 className='text-lg font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
										排版
									</h4>
									<p className='text-xs leading-relaxed' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
										以字体的粗细、层级与行高，建立如纸质书般的从容秩序。
									</p>
								</div>

								{/* Card 3: Content Rhythm 节奏 */}
								<div
									className='flex flex-col gap-3 rounded-2xl border p-5 transition-shadow hover:shadow-md'
									style={{
										background: 'var(--editorial-surface, #fffef8)',
										borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
										boxShadow: 'var(--ui-shadow-sm, 0 1px 4px rgba(0, 0, 0, 0.06))'
									}}
								>
									<div className='flex items-center gap-2'>
										<span
											className='flex h-7 w-7 items-center justify-center rounded-lg text-sm font-bold text-white'
											style={{ background: 'var(--editorial-accent, #b85e4c)' }}
										>
											3
										</span>
										<span className='font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
											Rhythm 节奏
										</span>
									</div>
									<h4 className='text-lg font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
										节奏
									</h4>
									<p className='text-xs leading-relaxed' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
										克制用色，大面积中性底色，只在关键节点点缀砖红。
									</p>
								</div>

								{/* Card 4: Liquid Glass 液态玻璃 */}
								<div
									className='flex flex-col gap-3 rounded-2xl border p-5 transition-shadow hover:shadow-md'
									style={{
										background: 'var(--editorial-surface, #fffef8)',
										borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
										boxShadow: 'var(--ui-shadow-sm, 0 1px 4px rgba(0, 0, 0, 0.06))'
									}}
								>
									<div className='flex items-center gap-2'>
										<span
											className='flex h-7 w-7 items-center justify-center rounded-lg text-sm font-bold text-white'
											style={{ background: 'var(--editorial-accent, #b85e4c)' }}
										>
											4
										</span>
										<span className='font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
											Liquid Glass 玻璃
										</span>
									</div>
									<h4 className='text-lg font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
										流动
									</h4>
									<p className='text-xs leading-relaxed' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
										半透明磨砂加背景折射，轻盈浮于内容之上的灵动质感。
									</p>
								</div>
							</div>

							{/* Editorial Long-form Article Preview */}
							<div
								className='flex flex-col gap-4 rounded-2xl border p-6'
								style={{
									background: 'var(--editorial-surface, #fffef8)',
									borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
									boxShadow: 'var(--ui-shadow-md, 0 4px 16px rgba(0, 0, 0, 0.08))'
								}}
							>
								<div className='flex items-center gap-3 text-xs'>
									<span
										className='rounded-full px-2.5 py-0.5 font-medium'
										style={{
											background: 'rgba(184, 94, 76, 0.12)',
											color: 'var(--editorial-accent, #b85e4c)'
										}}
									>
										深度阅读 · Essay
									</span>
									<span style={{ color: 'var(--editorial-text-tertiary, #b8a393)' }}>2026-10-15</span>
									<span style={{ color: 'var(--editorial-text-tertiary, #b8a393)' }}>· 5 分钟阅读</span>
								</div>

								<h3 className='text-xl font-bold leading-snug sm:text-2xl' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
									把喧嚣留在页外：数字花园中的留白美学
								</h3>

								<p className='text-sm leading-relaxed' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
									我们这个时代，最稀缺的不是信息，而是一口气把一件事读完的耐心。屏幕越来越亮，内容越来越多，我们能安静停留的时间却越来越短。一个纯粹的阅读表面，需要给予文字足够的喘息空间。
								</p>

								{/* Quote Block */}
								<div
									className='rounded-xl border-l-4 p-4'
									style={{
										background: 'var(--editorial-bg, #f5f1eb)',
										borderColor: 'var(--editorial-accent, #b85e4c)'
									}}
								>
									<p className='text-xs italic leading-relaxed' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
										“好的设计不是在没有东西可以添加的时候达成的，而是在没有任何东西可以剔除的时候达成的。”
									</p>
								</div>

								{/* Editorial Action Bar */}
								<div className='flex items-center justify-between pt-2 border-t' style={{ borderColor: 'var(--editorial-divider, rgba(74, 56, 50, 0.08))' }}>
									<div className='flex items-center gap-2 text-xs' style={{ color: 'var(--editorial-text-tertiary, #b8a393)' }}>
										<span>#视觉重构</span>
										<span>#DesignTokens</span>
									</div>
									<button
										className='flex items-center gap-1 rounded-full px-4 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90'
										style={{ background: 'var(--editorial-accent, #b85e4c)' }}
									>
										<span>继续阅读</span>
										<ChevronRight className='h-3.5 w-3.5' />
									</button>
								</div>
							</div>

							{/* Editorial Token Swatches Table */}
							<div
								className='rounded-2xl border p-5'
								style={{
									background: 'var(--editorial-surface, #fffef8)',
									borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))'
								}}
							>
								<h4 className='mb-3 text-xs font-bold uppercase tracking-wider' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
									Editorial Tokens 调色板
								</h4>
								<div className='grid grid-cols-2 gap-2 sm:grid-cols-3 text-xs'>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--editorial-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--editorial-bg)' }} />
										<div>
											<div className='font-mono font-medium'>--editorial-bg</div>
											<div className='text-[10px] text-gray-500'>#f5f1eb (base)</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--editorial-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--editorial-surface)' }} />
										<div>
											<div className='font-mono font-medium'>--editorial-surface</div>
											<div className='text-[10px] text-gray-500'>#fffef8 (card)</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--editorial-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--editorial-text-primary)' }} />
										<div>
											<div className='font-mono font-medium'>--editorial-text-primary</div>
											<div className='text-[10px] text-gray-500'>#4a3832 (deep brown)</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--editorial-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--editorial-text-secondary)' }} />
										<div>
											<div className='font-mono font-medium'>--editorial-text-secondary</div>
											<div className='text-[10px] text-gray-500'>#8b7667</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--editorial-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--editorial-accent)' }} />
										<div>
											<div className='font-mono font-medium'>--editorial-accent</div>
											<div className='text-[10px] text-gray-500'>#b85e4c (brick red)</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--editorial-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--editorial-border)' }} />
										<div>
											<div className='font-mono font-medium'>--editorial-border</div>
											<div className='text-[10px] text-gray-500'>rgba(74,56,50,0.12)</div>
										</div>
									</div>
								</div>
							</div>
						</section>
					)}

					{/* -----------------------------------------------------------------
					    RIGHT: ADMIN SURFACE (管理工具表面)
					----------------------------------------------------------------- */}
					{(activeTab === 'all' || activeTab === 'admin') && (
						<section
							className='flex flex-col gap-6 rounded-3xl border p-6 sm:p-8 transition-all'
							style={{
								background: 'var(--admin-bg, linear-gradient(180deg, #f0fffe 0%, #f5fbfb 100%))',
								borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
								color: 'var(--admin-text-primary, #2d3e3c)'
							}}
						>
							{/* Surface Header */}
							<div className='border-b pb-4' style={{ borderColor: 'var(--admin-divider, rgba(45, 62, 60, 0.08))' }}>
								<div className='flex items-center justify-between'>
									<div className='flex items-center gap-2'>
										<span
											className='flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold text-white'
											style={{ background: 'var(--brand, #3db8a8)' }}
										>
											A
										</span>
										<span className='text-xs font-semibold tracking-wider uppercase' style={{ color: 'var(--brand-ink, #1f7a6e)' }}>
											Admin Surface · 管理工具表面
										</span>
									</div>
									<span className='text-xs font-mono' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
										#f0fffe → #f5fbfb gradient
									</span>
								</div>
								<h2 className='mt-2 text-2xl font-bold tracking-tight sm:text-3xl' style={{ color: 'var(--admin-text-primary, #2d3e3c)' }}>
									高效、清晰、精确
								</h2>
								<p className='mt-1 text-sm' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
									适用于后台控制台、仪表盘、表单录入与审核。高信息密度、微青网格结构与稳定 Teal 交互控件。
								</p>
							</div>

							{/* Interactive Login/Auth Card (Directly inspired by admin-login-cool-grid-reference.png) */}
							<div
								className='flex flex-col gap-4 rounded-2xl border p-6 transition-all'
								style={{
									background: 'var(--admin-surface, #ffffff)',
									borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
									boxShadow: 'var(--ui-shadow-sm, 0 1px 4px rgba(0, 0, 0, 0.06))'
								}}
							>
								<div className='text-center'>
									<div
										className='mx-auto flex h-10 w-10 items-center justify-center rounded-xl text-white shadow-sm'
										style={{ background: 'var(--brand, #3db8a8)' }}
									>
										<Lock className='h-5 w-5' />
									</div>
									<h3 className='mt-3 text-lg font-bold' style={{ color: 'var(--admin-text-primary, #2d3e3c)' }}>
										管理员登录控件演示
									</h3>
									<p className='text-xs' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
										参考图 admin-login-cool-grid-reference 规范复现
									</p>
								</div>

								{/* Form Fields */}
								<div className='flex flex-col gap-3'>
									<div>
										<label className='block text-xs font-medium mb-1' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
											管理员邮箱
										</label>
										<div className='relative'>
											<Mail className='absolute left-3 top-2.5 h-4 w-4 text-gray-400' />
											<input
												type='email'
												defaultValue='admin@blog.limengyang.me'
												className='w-full rounded-xl border py-2 pl-9 pr-3 text-xs outline-none transition-all'
												style={{
													borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
													background: 'var(--admin-surface-subtle, #fafcfc)',
													color: 'var(--admin-text-primary, #2d3e3c)'
												}}
											/>
										</div>
									</div>

									<div>
										<label className='block text-xs font-medium mb-1' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
											访问密码
										</label>
										<div className='relative'>
											<Lock className='absolute left-3 top-2.5 h-4 w-4 text-gray-400' />
											<input
												type={showPassword ? 'text' : 'password'}
												defaultValue='admin-session-secure-key'
												className='w-full rounded-xl border py-2 pl-9 pr-10 text-xs outline-none transition-all'
												style={{
													borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
													background: 'var(--admin-surface-subtle, #fafcfc)',
													color: 'var(--admin-text-primary, #2d3e3c)'
												}}
											/>
											<button
												type='button'
												onClick={() => setShowPassword(!showPassword)}
												className='absolute right-3 top-2.5 text-gray-400 hover:text-gray-600'
											>
												{showPassword ? <EyeOff className='h-4 w-4' /> : <Eye className='h-4 w-4' />}
											</button>
										</div>
									</div>

									{/* Teal Brand Buttons */}
									<button
										type='button'
										className='flex items-center justify-center gap-2 rounded-xl py-2.5 text-xs font-semibold text-white transition-opacity hover:opacity-90 shadow-sm'
										style={{ background: 'var(--brand, #3db8a8)' }}
									>
										<span>进入管理后台 (Teal Button)</span>
										<ArrowUpRight className='h-3.5 w-3.5' />
									</button>

									<div className='flex items-center justify-between text-[11px] pt-1'>
										<span style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>Session: Active (HttpOnly)</span>
										<span className='font-mono font-medium' style={{ color: 'var(--brand-ink, #1f7a6e)' }}>
											--brand: #3db8a8
										</span>
									</div>
								</div>
							</div>

							{/* High Density Metric & Control Cards */}
							<div className='grid grid-cols-2 gap-3 sm:grid-cols-3'>
								<div
									className='flex flex-col gap-1 rounded-xl border p-3'
									style={{
										background: 'var(--admin-surface, #ffffff)',
										borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))'
									}}
								>
									<span className='text-[11px]' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
										知识条目 (Notes)
									</span>
									<span className='text-lg font-bold' style={{ color: 'var(--admin-text-primary, #2d3e3c)' }}>
										128
									</span>
									<span className='text-[10px] text-emerald-600'>+4 本周新增</span>
								</div>

								<div
									className='flex flex-col gap-1 rounded-xl border p-3'
									style={{
										background: 'var(--admin-surface, #ffffff)',
										borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))'
									}}
								>
									<span className='text-[11px]' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
										错题复习 (Mistakes)
									</span>
									<span className='text-lg font-bold' style={{ color: 'var(--admin-text-primary, #2d3e3c)' }}>
										42
									</span>
									<span className='text-[10px] text-amber-600'>8 项待复习</span>
								</div>

								<div
									className='flex flex-col gap-1 rounded-xl border p-3 col-span-2 sm:col-span-1'
									style={{
										background: 'var(--admin-surface, #ffffff)',
										borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))'
									}}
								>
									<span className='text-[11px]' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
										系统健康度
									</span>
									<span className='text-lg font-bold text-emerald-600'>100%</span>
									<span className='text-[10px]' style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>
										531/531 tests pass
									</span>
								</div>
							</div>

							{/* High Density Table Sample */}
							<div
								className='overflow-hidden rounded-2xl border'
								style={{
									background: 'var(--admin-surface, #ffffff)',
									borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))'
								}}
							>
								<div className='flex items-center justify-between border-b px-4 py-3' style={{ borderColor: 'var(--admin-divider)' }}>
									<span className='text-xs font-bold' style={{ color: 'var(--admin-text-primary)' }}>
										最近处理记录 (High Density Table)
									</span>
									<span className='text-[11px]' style={{ color: 'var(--admin-text-secondary)' }}>
										3 项活跃
									</span>
								</div>
								<div className='divide-y text-xs' style={{ borderColor: 'var(--admin-divider)' }}>
									<div className='flex items-center justify-between px-4 py-2.5 hover:bg-black/5'>
										<div className='flex items-center gap-2'>
											<span className='h-2 w-2 rounded-full' style={{ background: 'var(--brand, #3db8a8)' }} />
											<span className='font-medium'>Next.js App Router Token 重构</span>
										</div>
										<span className='rounded bg-teal-50 px-2 py-0.5 text-[10px] font-medium text-teal-700'>
											Phase 1
										</span>
									</div>
									<div className='flex items-center justify-between px-4 py-2.5 hover:bg-black/5'>
										<div className='flex items-center gap-2'>
											<span className='h-2 w-2 rounded-full bg-amber-500' />
											<span className='font-medium'>PostgreSQL 会话持久化</span>
										</div>
										<span className='rounded bg-amber-50 px-2 py-0.5 text-[10px] font-medium text-amber-700'>
											Synced
										</span>
									</div>
									<div className='flex items-center justify-between px-4 py-2.5 hover:bg-black/5'>
										<div className='flex items-center gap-2'>
											<span className='h-2 w-2 rounded-full bg-blue-500' />
											<span className='font-medium'>Cloudflare OpenNext Worker 部署</span>
										</div>
										<span className='rounded bg-blue-50 px-2 py-0.5 text-[10px] font-medium text-blue-700'>
											Ready
										</span>
									</div>
								</div>
							</div>

							{/* Admin Token Swatches Table */}
							<div
								className='rounded-2xl border p-5'
								style={{
									background: 'var(--admin-surface, #ffffff)',
									borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))'
								}}
							>
								<h4 className='mb-3 text-xs font-bold uppercase tracking-wider' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
									Admin Tokens 调色板
								</h4>
								<div className='grid grid-cols-2 gap-2 sm:grid-cols-3 text-xs'>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--admin-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--admin-surface)' }} />
										<div>
											<div className='font-mono font-medium'>--admin-surface</div>
											<div className='text-[10px] text-gray-500'>#ffffff</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--admin-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--admin-text-primary)' }} />
										<div>
											<div className='font-mono font-medium'>--admin-text-primary</div>
											<div className='text-[10px] text-gray-500'>#2d3e3c</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--admin-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--admin-text-secondary)' }} />
										<div>
											<div className='font-mono font-medium'>--admin-text-secondary</div>
											<div className='text-[10px] text-gray-500'>#6b7b79</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--admin-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--brand)' }} />
										<div>
											<div className='font-mono font-medium'>--brand</div>
											<div className='text-[10px] text-gray-500'>#3db8a8 (unified)</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--admin-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--brand-ink)' }} />
										<div>
											<div className='font-mono font-medium'>--brand-ink</div>
											<div className='text-[10px] text-gray-500'>#1f7a6e</div>
										</div>
									</div>
									<div className='flex items-center gap-2 rounded-lg border p-2' style={{ borderColor: 'var(--admin-divider)' }}>
										<div className='h-5 w-5 rounded border' style={{ background: 'var(--admin-border)' }} />
										<div>
											<div className='font-mono font-medium'>--admin-border</div>
											<div className='text-[10px] text-gray-500'>rgba(45,62,60,0.12)</div>
										</div>
									</div>
								</div>
							</div>
						</section>
					)}
				</div>

				{/* =========================================================================
				    BOTTOM: TOKEN CONSOLIDATION AUDIT & ACCEPTANCE MATRIX
				========================================================================= */}
				<section
					className='mt-8 rounded-3xl border p-6 sm:p-8'
					style={{
						background: 'var(--nav-glass-bg, rgba(255, 255, 255, 0.7))',
						borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
						backdropFilter: 'var(--nav-blur, blur(20px))'
					}}
				>
					<h3 className='text-lg font-bold' style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
						3 套 Token 系统收敛状态审计 (VSC-02 Verification)
					</h3>
					<p className='mt-1 text-xs' style={{ color: 'var(--editorial-text-tertiary, #b8a393)' }}>
						记录当前完成的系统整合进度与技术约束验证。
					</p>

					<div className='mt-4 overflow-x-auto'>
						<table className='w-full text-left text-xs'>
							<thead>
								<tr
									className='border-b'
									style={{ borderColor: 'var(--editorial-border)', color: 'var(--editorial-text-secondary)' }}
								>
									<th className='py-2 font-medium'>系统</th>
									<th className='py-2 font-medium'>原始定义</th>
									<th className='py-2 font-medium'>品牌色</th>
									<th className='py-2 font-medium'>Phase 1 收敛策略</th>
									<th className='py-2 font-medium'>状态</th>
								</tr>
							</thead>
							<tbody
								className='divide-y'
								style={{ borderColor: 'var(--editorial-divider, rgba(74, 56, 50, 0.08))' }}
							>
								<tr>
									<td className='py-2.5 font-sans font-semibold'>1. Legacy</td>
									<td className='py-2.5'>site-content.json</td>
									<td className='py-2.5 text-cyan-600'>#2fcbe7</td>
									<td className='py-2.5 font-sans'>在 layout.tsx htmlStyle 中桥接保留，确保零破坏</td>
									<td className='py-2.5 text-emerald-600 font-sans'>✅ 已桥接</td>
								</tr>
								<tr>
									<td className='py-2.5 font-sans font-semibold'>2. Tailwind</td>
									<td className='py-2.5'>src/styles/theme.css</td>
									<td className='py-2.5 text-teal-600'>#35bfab</td>
									<td className='py-2.5 font-sans'>字体与颜色合并入 ui-v2/tokens.css @theme，废弃并删除该文件</td>
									<td className='py-2.5 text-emerald-600 font-sans'>✅ 已合并废弃</td>
								</tr>
								<tr>
									<td className='py-2.5 font-sans font-semibold'>3. UI V2</td>
									<td className='py-2.5'>src/components/ui-v2/tokens.css</td>
									<td className='py-2.5 font-bold' style={{ color: 'var(--brand, #3db8a8)' }}>#3db8a8</td>
									<td className='py-2.5 font-sans'>扩充双表面（Editorial + Admin + Glass），成为全局唯一样式真相源</td>
									<td className='py-2.5 text-emerald-600 font-sans'>✅ 统一基准</td>
								</tr>
							</tbody>
						</table>
					</div>
				</section>
			</main>
		</div>
	)
}
