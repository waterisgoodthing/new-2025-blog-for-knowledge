import { AiRunsPanel } from './components/ai-runs-panel'
import { Uiv2PageHeader } from '@/components/ui-v2'

export default function ManageAiPage() {
  return <div className='space-y-8'><Uiv2PageHeader eyebrow='AI 治理' title='AI 运行记录' subtitle='仅审查真实运行记录；人工确认不会直接写入正式学习对象。' /><AiRunsPanel /></div>
}
