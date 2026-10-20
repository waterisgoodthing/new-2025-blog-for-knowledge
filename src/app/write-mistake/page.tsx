'use client'

import { StagedMistakeForm } from './components/staged-mistake-form'
import { AuthGate } from '@/components/auth-gate'
import Link from 'next/link'

export default function WriteMistakePage() {
	return (
		<AuthGate>
			<div className='mx-auto mb-6 max-w-5xl rounded-2xl border border-amber-200/70 bg-amber-50/80 px-5 py-4 text-sm leading-6 text-amber-900'>
				<p className='font-medium'>旧错题入口已进入兼容模式</p>
				<p className='mt-1'>
					第一版 MVP 的新错题闭环位于管理工作区：先在题库确认正式题目，再从
					<Link href='/manage/mistakes' className='mx-1 underline underline-offset-4'>/manage/mistakes</Link>
					创建错题草稿。此旧表单暂时保留用于兼容历史录入，不会自动迁移或删除旧数据。
				</p>
			</div>
			<StagedMistakeForm />
		</AuthGate>
	)
}
