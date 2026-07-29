import { AiRunsPanel } from './components/ai-runs-panel'
import { ManagePageHeader } from '../../components/manage-page-header'

export default function ManageAiPage() {
  return <div className='space-y-8'><ManagePageHeader eyebrow='AI 治理' title='AI 运行记录' description='仅审查真实运行记录；人工确认不会直接写入正式学习对象。' /><AiRunsPanel /></div>
}
