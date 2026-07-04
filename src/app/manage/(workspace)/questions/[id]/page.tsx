import { QuestionEditor } from '../components/question-editor'

export default async function QuestionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return <QuestionEditor questionId={id} />
}
