import { ManagePageHeader } from '../../components/manage-page-header'
import { QuestionList } from './components/question-list'

export default function ManageQuestionsPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Question System'
        title='Questions'
        description='管理可复用题目、答案、解析与知识点关联。'
      />
      <QuestionList />
    </div>
  )
}
