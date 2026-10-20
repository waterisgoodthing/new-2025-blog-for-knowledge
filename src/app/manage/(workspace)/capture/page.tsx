import { Uiv2PageHeader } from '@/components/ui-v2'
import { CaptureContent } from './components/capture-content'

export default function ManageCapturePage() {
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader eyebrow='学习采集' title='图片采集' subtitle='可上传图片后识别，也可直接手工录入。识别失败不会阻止你手工补全并进入草稿审核。' />
      <CaptureContent />
    </div>
  )
}
