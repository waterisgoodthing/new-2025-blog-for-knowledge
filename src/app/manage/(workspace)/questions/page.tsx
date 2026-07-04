import { ManagePageHeader } from '../../components/manage-page-header'
import { QuestionList } from './components/question-list'

export default function ManageQuestionsPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Batch 3 · 私有题库'
        title='正式题库'
        description='这里只展示已经人工确认入库的题目。'
      />
      <QuestionList />
    </div>
  )
}
