import { useState } from 'react'

import type {
	QuestionCardModel,
	QuestionPracticeState,
} from '../../../contracts/ui-v2/question'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2DifficultyBadge, Uiv2SourceBadge, Uiv2SubjectBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

const TYPE_LABEL: Record<QuestionCardModel['questionType'], string> = {
	single_choice: '单选',
	multiple_choice: '多选',
	true_false: '判断',
	short_answer: '简答',
	essay: '论述',
}

export interface Uiv2QuestionCardProps {
	question: QuestionCardModel
	initialState?: QuestionPracticeState
}

/**
 * Question card (U6): browse → answering (local selection, NO correctness
 * judgment) → result (reveals stored answer/analysis). The answering state
 * never claims 对/错；there is no attempt backend (GAP-006).
 */
export function Uiv2QuestionCard({ question, initialState = 'browse' }: Uiv2QuestionCardProps) {
	const [practiceState, setPracticeState] = useState<QuestionPracticeState>(initialState)
	const [selection, setSelection] = useState<string | null>(null)

	return (
		<Uiv2Card title={question.title}>
			<div className="flex flex-wrap items-center gap-2">
				<Uiv2Badge text={TYPE_LABEL[question.questionType]} tone="neutral" />
				<Uiv2DifficultyBadge difficulty={question.difficulty} />
				<Uiv2SubjectBadge label={question.subjectLabel} />
				{question.knowledgePointIds.length > 0 ? (
					<span className="text-[var(--uiv2-text-secondary)]">
						关联 {question.knowledgePointIds.length} 个知识点
					</span>
				) : (
					<span className="text-[var(--uiv2-text-secondary)]">未关联知识点</span>
				)}
			</div>
			<p>{question.stem}</p>

			{practiceState === 'browse' ? (
				<button
					type="button"
					onClick={() => setPracticeState('answering')}
					className="min-h-[40px] rounded-[var(--uiv2-radius-sm)] border border-[var(--uiv2-border)] px-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
				>
					开始作答
				</button>
			) : null}

			{practiceState === 'answering' ? (
				<fieldset>
					<legend className="text-[var(--uiv2-text-secondary)]">
						选择你的答案（本地练习，不评分）
					</legend>
					<div className="flex flex-col gap-2">
						{question.options.map(option => (
							<label key={option.key} className="flex min-h-[40px] items-center gap-2">
								<input
									type="radio"
									name={`uiv2-answer-${question.id}`}
									value={option.key}
									checked={selection === option.key}
									onChange={() => setSelection(option.key)}
								/>
								<span>
									{option.key}. {option.text}
								</span>
							</label>
						))}
						{question.options.length === 0 ? <p>本题为非选择题，请在纸上作答后查看解析。</p> : null}
					</div>
					<button
						type="button"
						disabled={question.options.length > 0 && selection === null}
						onClick={() => setPracticeState('result')}
						className="min-h-[40px] rounded-[var(--uiv2-radius-sm)] bg-[var(--uiv2-brand-ink)] px-4 text-white disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
					>
						查看解析
					</button>
				</fieldset>
			) : null}

			{practiceState === 'result' ? (
				<div>
					<p>
						{question.correctAnswer !== null
							? `参考答案：${question.correctAnswer}`
							: '本题暂无收录答案'}
					</p>
					{question.analysis ? <p>解析：{question.analysis}</p> : null}
					<p role="note" className="text-[var(--uiv2-text-secondary)]">
						本地练习记录，不计入成绩（作答同步能力缺失，GAP-006）
					</p>
					<button
						type="button"
						onClick={() => {
							setPracticeState('browse')
							setSelection(null)
						}}
						className="min-h-[40px] rounded-[var(--uiv2-radius-sm)] border border-[var(--uiv2-border)] px-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
					>
						重新练习
					</button>
				</div>
			) : null}
		</Uiv2Card>
	)
}

export interface Uiv2QuestionsSectionProps {
	model: UiPageModel<QuestionCardModel[]>
	onRetry?: () => void
}

export function Uiv2QuestionsSection({ model, onRetry }: Uiv2QuestionsSectionProps) {
	return (
		<section aria-label="题库">
			<Uiv2SectionHeader title="题库" description="可复用题目：练习、查看解析、关联知识点与错题" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载题库"
				emptyHint="题库是空的，先去新建第一道题吧。"
				onRetry={onRetry}
			>
				{questions => (
					<ul className="grid gap-4 md:grid-cols-2">
						{questions.map(question => (
							<li key={question.id}>
								<Uiv2QuestionCard question={question} />
							</li>
						))}
					</ul>
				)}
			</Uiv2PageStateView>
		</section>
	)
}
