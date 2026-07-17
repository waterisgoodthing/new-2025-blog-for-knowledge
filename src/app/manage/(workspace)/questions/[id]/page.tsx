import { ManagePageHeader } from '../../../components/manage-page-header'
import { QuestionCreateForm } from '../components/question-create-form'
import { QuestionEditor } from '../components/question-editor'

export default async function QuestionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Question System'
        title={id === 'new' ? 'New Question' : 'Question Detail'}
        description={id === 'new' ? '创建可复用的正式题目。' : '查看并维护正式题目的内容与知识组织。'}
      />
      {id === 'new' ? <QuestionCreateForm /> : <QuestionEditor questionId={id} />}
    </div>
  )
}
