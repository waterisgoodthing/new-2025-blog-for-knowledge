import { AiRunsPanel } from '../components/ai-runs-panel'
import { ManagePageHeader } from '../../../components/manage-page-header'

export default function ManageAiRunsPage() {
  return <div className='space-y-8'><ManagePageHeader eyebrow='AI 治理' title='AI 运行记录' description='真实来源、失败态和人工确认闸门。' /><AiRunsPanel /></div>
}
