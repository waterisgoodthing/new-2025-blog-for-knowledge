import { AiRunsPanel } from '../components/ai-runs-panel'
import { Uiv2PageHeader } from '@/components/ui-v2'

export default function ManageAiRunsPage() {
  return <div className='space-y-8'><Uiv2PageHeader eyebrow='AI 治理' title='AI 运行记录' subtitle='真实来源、失败态和人工确认闸门。' /><AiRunsPanel /></div>
}
