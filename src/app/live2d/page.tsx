'use client'

import { motion } from 'motion/react'
import { useConfigStore } from '@/app/(home)/stores/config-store'
import { Settings, Monitor, Upload, Power } from 'lucide-react'

export default function Live2DPage() {
	const { setConfigDialogOpen } = useConfigStore()

	return (
		<div className='flex min-h-[60vh] items-center justify-center px-6 py-8'>
			<motion.div
				initial={{ opacity: 0, y: 20 }}
				animate={{ opacity: 1, y: 0 }}
				className='w-full max-w-md rounded-2xl border border-white/40 bg-white/60 p-8 shadow-lg backdrop-blur-xl'
			>
				<div className='mb-6 text-center'>
					<div className='mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--color-brand)]/10 text-[var(--color-brand)]'>
						<Monitor className='h-7 w-7' />
					</div>
					<h1 className='text-lg font-bold text-gray-800'>Live2D 模型管理</h1>
				</div>

				<div className='mb-6 rounded-xl border border-white/50 bg-white/50 p-4'>
					<div className='mb-2 text-xs font-medium text-gray-400'>当前状态</div>
					<div className='flex items-center gap-2 text-sm text-gray-600'>
						<span className='inline-block h-2 w-2 rounded-full bg-gray-400' />
						未启用
					</div>
				</div>

				<div className='mb-6'>
					<div className='mb-3 text-xs font-medium text-gray-400'>如何使用</div>
					<div className='space-y-3'>
						{[
							{ icon: Settings, text: '在网站设置中上传 Live2D 模型文件' },
							{ icon: Power, text: '启用 Live2D 显示开关' },
							{ icon: Monitor, text: '返回此页面查看模型效果' },
						].map((step, i) => (
							<div key={i} className='flex items-start gap-3 text-sm text-gray-600'>
								<div className='flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-[var(--color-brand)]/8 text-[var(--color-brand)]'>
									<step.icon className='h-3.5 w-3.5' />
								</div>
								<span className='pt-0.5'>{step.text}</span>
							</div>
						))}
					</div>
				</div>

				<button
					type='button'
					onClick={() => setConfigDialogOpen(true)}
					className='flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-transform hover:scale-[1.01] active:scale-[0.99]'
				>
					<Settings className='h-4 w-4' />
					前往网站设置
				</button>
			</motion.div>
		</div>
	)
}
